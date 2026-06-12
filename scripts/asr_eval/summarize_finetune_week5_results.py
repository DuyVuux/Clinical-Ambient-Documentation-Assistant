#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Summarize Week 5 fine-tune results into JSON and Markdown.

This script is intentionally flexible because metric JSON structures may differ
between compute_wer.py and training scripts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "_missing": True,
            "_path": str(path),
        }

    return json.loads(path.read_text(encoding="utf-8"))


def find_number(
    obj: Any,
    candidate_keys: list[str],
) -> float | int | None:
    if isinstance(obj, dict):
        for k in candidate_keys:
            if k in obj and isinstance(obj[k], (int, float)):
                return obj[k]

        for v in obj.values():
            found = find_number(v, candidate_keys)

            if found is not None:
                return found

    elif isinstance(obj, list):
        for x in obj:
            found = find_number(x, candidate_keys)

            if found is not None:
                return found

    return None


def metric_percent(x: float | int | None) -> str:
    if x is None:
        return "TBD"

    if x <= 1:
        return f"{x * 100:.2f}%"

    return f"{x:.2f}%"


def extract_asr_metrics(path: Path) -> dict[str, Any]:
    data = read_json(path)

    return {
        "path": str(path),
        "wer": find_number(
            data,
            ["wer", "strict_wer", "normalized_wer"],
        ),
        "cer": find_number(
            data,
            ["cer", "strict_cer", "normalized_cer"],
        ),
        "raw": data,
    }


def extract_medical_errors(path: Path) -> dict[str, Any]:
    data = read_json(path)

    # Flexible extraction.
    # If your script has exact keys, this will catch them.
    return {
        "path": str(path),
        "missing_negation": find_number(
            data,
            [
                "missing_negation",
                "negation_errors",
                "missing_negation_count",
            ],
        ),
        "missing_symptom": find_number(
            data,
            [
                "missing_symptom",
                "symptom_errors",
                "missing_symptom_count",
            ],
        ),
        "medication_error": find_number(
            data,
            [
                "medication_error",
                "medication_errors",
                "medication_error_count",
            ],
        ),
        "dose_unit_error": find_number(
            data,
            [
                "dose_unit_error",
                "dose_errors",
                "dose_unit_error_count",
            ],
        ),
        "numeric_error": find_number(
            data,
            [
                "numeric_error",
                "numeric_errors",
                "numeric_error_count",
            ],
        ),
        "raw": data,
    }


def build_rows(project_root: Path) -> list[dict[str, Any]]:
    base = project_root / "experiments/asr/finetune/week5"

    rows = [
        {
            "name": "ChunkFormer reference",
            "role": "primary_reference",
            "metrics": base
            / "baseline_safe_dev/chunkformer_safe_dev_metrics.json",
            "medical": base
            / "baseline_safe_dev/chunkformer_safe_dev_medical_errors.json",
            "edge_metrics": None,
            "edge_medical": None,
        },
        {
            "name": "PhoWhisper-medium baseline",
            "role": "backup_baseline",
            "metrics": base
            / "baseline_safe_dev/phowhisper_medium_safe_dev_metrics.json",
            "medical": base
            / "baseline_safe_dev/phowhisper_medium_safe_dev_medical_errors.json",
            "edge_metrics": base
            / "error_analysis/edge_subset_metrics/phowhisper_baseline_edge_metrics.json",
            "edge_medical": base
            / "error_analysis/edge_subset_metrics/phowhisper_baseline_edge_medical_errors.json",
        },
        {
            "name": "Run 01 conservative",
            "role": "candidate",
            "metrics": base
            / "run_01_phowhisper_medium_conservative/metrics_dev_project_wer.json",
            "medical": base
            / "run_01_phowhisper_medium_conservative/medical_errors_dev.json",
            "edge_metrics": base
            / "error_analysis/edge_subset_metrics/run_01_edge_metrics.json",
            "edge_medical": base
            / "error_analysis/edge_subset_metrics/run_01_edge_medical_errors.json",
        },
        {
            "name": "Run 02 low-lr",
            "role": "candidate",
            "metrics": base
            / "run_02_phowhisper_medium_low_lr/metrics_dev_project_wer.json",
            "medical": base
            / "run_02_phowhisper_medium_low_lr/medical_errors_dev.json",
            "edge_metrics": base
            / "error_analysis/edge_subset_metrics/run_02_edge_metrics.json",
            "edge_medical": base
            / "error_analysis/edge_subset_metrics/run_02_edge_medical_errors.json",
        },
    ]

    output = []

    for row in rows:
        asr = extract_asr_metrics(row["metrics"])
        med = extract_medical_errors(row["medical"])

        if row["edge_metrics"] is not None:
            edge_asr = extract_asr_metrics(row["edge_metrics"])
        else:
            edge_asr = None

        if row["edge_medical"] is not None:
            edge_med = extract_medical_errors(row["edge_medical"])
        else:
            edge_med = None

        output.append(
            {
                "name": row["name"],
                "role": row["role"],
                "wer": asr["wer"],
                "cer": asr["cer"],
                "missing_negation": med["missing_negation"],
                "missing_symptom": med["missing_symptom"],
                "medication_error": med["medication_error"],
                "dose_unit_error": med["dose_unit_error"],
                "numeric_error": med["numeric_error"],
                "edge_wer": edge_asr["wer"] if edge_asr else None,
                "edge_cer": edge_asr["cer"] if edge_asr else None,
                "edge_missing_negation": (
                    edge_med["missing_negation"]
                    if edge_med
                    else None
                ),
                "edge_missing_symptom": (
                    edge_med["missing_symptom"]
                    if edge_med
                    else None
                ),
            }
        )

    return output


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = []

    lines.append("# Day 5 Week 5 — Fine-tune Clinical Error Analysis")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append(
        "Compare PhoWhisper fine-tuning runs using WER/CER "
        "and clinical ASR error metrics."
    )
    lines.append("")
    lines.append("## Full dev comparison")
    lines.append("")
    lines.append(
        "| Model / Run | Role | WER | CER | Missing negation | "
        "Missing symptom | Medication error | Dose/unit error | Numeric error |"
    )
    lines.append(
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"
    )

    for r in rows:
        lines.append(
            f"| {r['name']} | {r['role']} | "
            f"{metric_percent(r['wer'])} | "
            f"{metric_percent(r['cer'])} | "
            f"{r['missing_negation']} | "
            f"{r['missing_symptom']} | "
            f"{r['medication_error']} | "
            f"{r['dose_unit_error']} | "
            f"{r['numeric_error']} |"
        )

    lines.append("")
    lines.append("## Edge-risk subset comparison")
    lines.append("")
    lines.append(
        "| Model / Run | Edge WER | Edge CER | "
        "Edge missing negation | Edge missing symptom |"
    )
    lines.append("|---|---:|---:|---:|---:|")

    for r in rows:
        if r["edge_wer"] is None:
            continue

        lines.append(
            f"| {r['name']} | "
            f"{metric_percent(r['edge_wer'])} | "
            f"{metric_percent(r['edge_cer'])} | "
            f"{r['edge_missing_negation']} | "
            f"{r['edge_missing_symptom']} |"
        )

    lines.append("")
    lines.append("## Decision rules")
    lines.append("")
    lines.append(
        "- Accept a fine-tuned backup only if WER < 20% "
        "and clinical errors do not increase."
    )
    lines.append(
        "- Reject a checkpoint if WER improves but "
        "missing negation/symptom/dose errors increase."
    )
    lines.append(
        "- If WER remains > 22%, Week 6 should focus on "
        "more data rather than more hyperparameter tuning."
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--project_root",
        default="/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant",
    )

    parser.add_argument(
        "--output_json",
        default=(
            "experiments/asr/finetune/week5/error_analysis/"
            "fine_tune_error_analysis_summary.json"
        ),
    )

    parser.add_argument(
        "--output_md",
        default=(
            "experiments/asr/finetune/week5/error_analysis/"
            "FINE_TUNE_ERROR_ANALYSIS.md"
        ),
    )

    args = parser.parse_args()

    project_root = Path(args.project_root)
    rows = build_rows(project_root)

    out_json = project_root / args.output_json
    out_md = project_root / args.output_md

    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    out_md.write_text(
        render_markdown(rows),
        encoding="utf-8",
    )

    print(f"[DONE] {out_json}")
    print(f"[DONE] {out_md}")


if __name__ == "__main__":
    main()