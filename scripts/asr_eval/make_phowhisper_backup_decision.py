#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_rate(x):
    if x is None:
        return None

    if x > 1:
        return x / 100

    return x


def fmt_pct(x):
    if x is None:
        return "TBD"

    x = as_rate(x)

    return f"{x * 100:.2f}%"


def clinical_tuple(row):
    keys = [
        "missing_negation",
        "missing_symptom",
        "medication_error",
        "dose_unit_error",
        "numeric_error",
    ]

    return tuple(row.get(k) for k in keys)


def clinical_not_worse(candidate, baseline):
    keys = [
        "missing_negation",
        "missing_symptom",
        "medication_error",
        "dose_unit_error",
        "numeric_error",
    ]

    for k in keys:
        c = candidate.get(k)
        b = baseline.get(k)

        if isinstance(c, (int, float)) and isinstance(b, (int, float)):
            if c > b:
                return False

    return True


def choose_decision(rows):
    baseline = next(
        r
        for r in rows
        if r["name"] == "PhoWhisper-medium baseline"
    )

    candidates = [
        r
        for r in rows
        if r["role"] == "candidate"
    ]

    acceptable = []
    continuing = []

    for c in candidates:
        wer = as_rate(c.get("wer"))

        if wer is None:
            continue

        safe = clinical_not_worse(c, baseline)

        if wer < 0.20 and safe:
            acceptable.append(c)

        elif 0.20 <= wer <= 0.22 and safe:
            continuing.append(c)

    if acceptable:
        best = sorted(
            acceptable,
            key=lambda r: as_rate(r["wer"]),
        )[0]

        return {
            "status": "ACCEPT_BACKUP_V0_1",
            "selected_run": best["name"],
            "reason": "WER < 20% and clinical errors did not increase.",
        }

    if continuing:
        best = sorted(
            continuing,
            key=lambda r: as_rate(r["wer"]),
        )[0]

        return {
            "status": "CONTINUE_FINE_TUNING_WEEK6",
            "selected_run": best["name"],
            "reason": (
                "WER improved but did not meet <20% target; "
                "clinical errors did not increase."
            ),
        }

    return {
        "status": "NEED_MORE_DATA_WEEK6",
        "selected_run": None,
        "reason": "No candidate met WER/safety acceptance criteria.",
    }


def render_md(rows, decision):
    lines = []

    lines.append("# Day 6 Week 5 — PhoWhisper Backup Model Decision")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append(
        "Decide whether fine-tuned PhoWhisper-medium can be accepted "
        "as backup ASR model v0.1."
    )
    lines.append("")
    lines.append("## Acceptance criteria")
    lines.append("")
    lines.append("- Dev WER < 20%")
    lines.append(
        "- Clinical errors do not increase compared with "
        "PhoWhisper-medium baseline"
    )
    lines.append("- test_holdout is not used")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append(
        "| Run | Role | WER | CER | Missing negation | Missing symptom | "
        "Medication error | Dose/unit error | Numeric error |"
    )
    lines.append(
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"
    )

    for r in rows:
        lines.append(
            f"| {r['name']} | {r['role']} | "
            f"{fmt_pct(r.get('wer'))} | "
            f"{fmt_pct(r.get('cer'))} | "
            f"{r.get('missing_negation')} | "
            f"{r.get('missing_symptom')} | "
            f"{r.get('medication_error')} | "
            f"{r.get('dose_unit_error')} | "
            f"{r.get('numeric_error')} |"
        )

    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"Status: **{decision['status']}**")
    lines.append("")
    lines.append(f"Selected run: `{decision['selected_run']}`")
    lines.append("")
    lines.append(f"Reason: {decision['reason']}")
    lines.append("")
    lines.append("## Next action")
    lines.append("")

    if decision["status"] == "ACCEPT_BACKUP_V0_1":
        lines.append("- Freeze the selected fine-tuned backup model.")
        lines.append("- Prepare final evaluation plan.")
        lines.append(
            "- Do not run test_holdout until final model selection "
            "protocol is frozen."
        )

    elif decision["status"] == "CONTINUE_FINE_TUNING_WEEK6":
        lines.append(
            "- Continue Week 6 fine-tuning with adjusted hyperparameters "
            "or more data."
        )
        lines.append("- Keep the best Week 5 run as current candidate.")

    else:
        lines.append("- Perform data gap analysis.")
        lines.append("- Add more VietMed data if available.")
        lines.append("- Add auxiliary speech only with controlled ratio.")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--summary_json",
        default=(
            "experiments/asr/finetune/week5/error_analysis/"
            "fine_tune_error_analysis_summary.json"
        ),
    )

    parser.add_argument(
        "--output_json",
        default=(
            "experiments/asr/finetune/week5/decision/"
            "backup_model_decision.json"
        ),
    )

    parser.add_argument(
        "--output_md",
        default=(
            "experiments/asr/finetune/week5/decision/"
            "PHOWHISPER_BACKUP_MODEL_DECISION.md"
        ),
    )

    parser.add_argument(
        "--project_root",
        default="/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root)

    summary_path = project_root / args.summary_json
    rows = read_json(summary_path)

    decision = choose_decision(rows)

    out_json = project_root / args.output_json
    out_md = project_root / args.output_md

    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(
        json.dumps(
            {
                "decision": decision,
                "rows": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    out_md.write_text(
        render_md(rows, decision),
        encoding="utf-8",
    )

    print(json.dumps(decision, ensure_ascii=False, indent=2))
    print(f"[DONE] {out_json}")
    print(f"[DONE] {out_md}")


if __name__ == "__main__":
    main()