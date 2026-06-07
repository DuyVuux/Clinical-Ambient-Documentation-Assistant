#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Summarize audio QA reports for preprocessing variants.

Input:
experiments/asr/preprocessing/audio_quality_audit/variants/*/audio_quality_report.json

Output:
- variant_audio_qa_summary.json
- VARIANT_AUDIO_QA_SUMMARY.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PROJECT_ROOT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)


VARIANTS = [
    "original",
    "p03_vad_pad_200ms",
    "p04_vad_pad_300ms",
    "p05_vad_pad_500ms",
]


IMPORTANT_WARNINGS = [
    "edge_loss_risk",
    "long_leading_silence",
    "long_trailing_silence",
    "too_quiet",
    "too_loud",
    "clipping_detected",
    "peak_near_0db_clipping_risk",
    "too_short",
    "long_audio_may_need_chunking",
    "non_16khz",
    "non_mono",
]


IMPORTANT_NUMERIC = [
    "duration_seconds",
    "rms_db",
    "peak_db",
    "leading_silence_ms",
    "trailing_silence_ms",
    "first_300ms_db",
    "last_300ms_db",
    "middle_db",
    "min_edge_to_middle_ratio",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_warning_count(report: dict[str, Any], warning: str) -> int:
    return int(report["summary"].get("warning_counts", {}).get(warning, 0))


def get_numeric_mean(report: dict[str, Any], metric: str) -> Any:
    return report["summary"].get("numeric_summary", {}).get(metric, {}).get("mean")


def get_numeric_median(report: dict[str, Any], metric: str) -> Any:
    return report["summary"].get("numeric_summary", {}).get(metric, {}).get("median")


def build_summary(variants_root: Path) -> list[dict[str, Any]]:
    rows = []

    for variant in VARIANTS:
        report_path = variants_root / variant / "audio_quality_report.json"
        padding_aware_path = variants_root / variant / "padding_aware_audio_quality_report.json"

        if not report_path.exists():
            rows.append({
                "variant": variant,
                "missing_report": True,
                "report_path": str(report_path),
            })
            continue

        report = read_json(report_path)

        speech_edge_loss_risk = None
        if padding_aware_path.exists():
            padding_report = read_json(padding_aware_path)
            speech_edge_loss_risk = padding_report.get("summary", {}).get("speech_edge_loss_risk")

        row = {
            "variant": variant,
            "missing_report": False,
            "report_path": str(report_path),
            "n_samples": report["summary"].get("n_samples"),
            "warnings": {
                warning: get_warning_count(report, warning)
                for warning in IMPORTANT_WARNINGS
            },
            "numeric_mean": {
                metric: get_numeric_mean(report, metric)
                for metric in IMPORTANT_NUMERIC
            },
            "numeric_median": {
                metric: get_numeric_median(report, metric)
                for metric in IMPORTANT_NUMERIC
            },
            "speech_edge_loss_risk": speech_edge_loss_risk,
        }

        rows.append(row)

    return rows


def make_decision(row: dict[str, Any], baseline_edge: int) -> str:
    if row.get("missing_report"):
        return "missing_report"

    warnings = row["warnings"]
    edge = warnings.get("edge_loss_risk", 0)
    clipping = warnings.get("clipping_detected", 0)
    too_short = warnings.get("too_short", 0)
    non_16khz = warnings.get("non_16khz", 0)
    non_mono = warnings.get("non_mono", 0)

    if non_16khz > 0 or non_mono > 0:
        return "drop_format_regression"

    if clipping > 0:
        return "drop_clipping_created"

    if too_short > 0:
        return "drop_too_short_created"

    if edge < baseline_edge:
        return "keep_candidate_edge_improved"

    if edge == baseline_edge:
        return "neutral_no_edge_improvement"

    return "drop_edge_worse"


def render_markdown(summary_rows: list[dict[str, Any]]) -> str:
    baseline = next((r for r in summary_rows if r["variant"] == "original"), None)
    baseline_edge = 29

    if baseline and not baseline.get("missing_report"):
        baseline_edge = baseline["warnings"].get("edge_loss_risk", 29)

    lines = []
    lines.append("# Day 3 Week 4 — Variant Audio QA Summary")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Audit VAD-padding preprocessing variants before ASR A/B testing.")
    lines.append("")
    lines.append("## Padding-Aware Edge Loss Comparison")
    lines.append("")
    lines.append("This table compares the old metric (file edge) against the new metric (speech edge).")
    lines.append("`speech_edge_loss_risk` ignores inserted silence padding and measures energy at the actual speech start/end.")
    lines.append("")
    lines.append("| Variant | N | file_edge_loss_risk | speech_edge_loss_risk | Difference |")
    lines.append("|---|---:|---:|---:|---:|")

    for row in summary_rows:
        if row.get("missing_report"):
            lines.append(f"| {row['variant']} | - | - | - | - |")
            continue
            
        file_edge = row["warnings"].get("edge_loss_risk", 0)
        speech_edge = row.get("speech_edge_loss_risk")
        
        if speech_edge is not None:
            diff = speech_edge - file_edge
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            speech_edge_str = str(speech_edge)
        else:
            speech_edge_str = "N/A"
            diff_str = "N/A"
            
        lines.append(
            f"| {row['variant']} | {row['n_samples']} | {file_edge} | {speech_edge_str} | {diff_str} |"
        )
        
    lines.append("")
    lines.append("## Baseline")
    lines.append("")
    lines.append(f"- Baseline original dev edge_loss_risk: **{baseline_edge}**")
    lines.append("")
    lines.append("## Warning comparison")
    lines.append("")
    lines.append(
        "| Variant | N | edge_loss_risk | long_leading_silence | long_trailing_silence | "
        "too_quiet | clipping | too_short | mean_duration | mean_edge_ratio | Decision |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")

    for row in summary_rows:
        if row.get("missing_report"):
            lines.append(
                f"| {row['variant']} | - | - | - | - | - | - | - | - | - | missing_report |"
            )
            continue

        decision = make_decision(row, baseline_edge)
        warnings = row["warnings"]
        mean = row["numeric_mean"]

        lines.append(
            f"| {row['variant']} | "
            f"{row['n_samples']} | "
            f"{warnings.get('edge_loss_risk', 0)} | "
            f"{warnings.get('long_leading_silence', 0)} | "
            f"{warnings.get('long_trailing_silence', 0)} | "
            f"{warnings.get('too_quiet', 0)} | "
            f"{warnings.get('clipping_detected', 0)} | "
            f"{warnings.get('too_short', 0)} | "
            f"{mean.get('duration_seconds')} | "
            f"{mean.get('min_edge_to_middle_ratio')} | "
            f"{decision} |"
        )

    lines.append("")
    lines.append("## Interpretation rules")
    lines.append("")
    lines.append("- Keep a variant if `edge_loss_risk` decreases and no new serious warning appears.")
    lines.append("- Drop a variant if it creates clipping, too-short audio, format regression, or worse edge-loss.")
    lines.append("- If all VAD variants fail to reduce edge-loss, create padding-only variants next.")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append("Select top 1–3 variants for Day 4 ASR A/B test on VietMed dev.")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--project_root",
        default=str(DEFAULT_PROJECT_ROOT),
    )

    parser.add_argument(
        "--variants_root",
        default="experiments/asr/preprocessing/audio_quality_audit/variants",
    )

    parser.add_argument(
        "--output_json",
        default="experiments/asr/preprocessing/audio_quality_audit/variant_audio_qa_summary.json",
    )

    parser.add_argument(
        "--output_md",
        default="experiments/asr/preprocessing/audio_quality_audit/VARIANT_AUDIO_QA_SUMMARY.md",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root)

    variants_root = Path(args.variants_root)
    if not variants_root.is_absolute():
        variants_root = project_root / variants_root

    output_json = Path(args.output_json)
    if not output_json.is_absolute():
        output_json = project_root / output_json

    output_md = Path(args.output_md)
    if not output_md.is_absolute():
        output_md = project_root / output_md

    summary_rows = build_summary(variants_root)

    write_json(output_json, summary_rows)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(summary_rows), encoding="utf-8")

    print(f"[DONE] JSON: {output_json}")
    print(f"[DONE] MD:   {output_md}")


if __name__ == "__main__":
    main()