#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Summarize Phase 4 Run A/B and decide whether to proceed to Run C.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_missing": True, "_path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def find_metric(data: Any, keys: list[str]) -> float | None:
    if isinstance(data, dict):
        for key in keys:
            if key in data and isinstance(data[key], (int, float)):
                return float(data[key])
        for value in data.values():
            found = find_metric(value, keys)
            if found is not None:
                return found
    elif isinstance(data, list):
        for value in data:
            found = find_metric(value, keys)
            if found is not None:
                return found
    return None


def as_rate(value: float | None) -> float | None:
    if value is None:
        return None
    return value / 100 if value > 1 else value


def fmt_pct(value: float | None) -> str:
    value = as_rate(value)
    if value is None:
        return "TBD"
    return f"{value * 100:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drive_root", required=True)
    parser.add_argument("--run0_val_metrics", default=None)
    parser.add_argument("--week5_vietmed_wer", type=float, default=0.1657)
    parser.add_argument("--forgetting_tolerance_abs", type=float, default=0.05)
    args = parser.parse_args()

    drive_root = Path(args.drive_root)

    runa_metrics_path = drive_root / "finetune/runA_smoke_200/metrics.json"
    runb_metrics_path = drive_root / "finetune/runB_mini_1000/metrics.json"
    forgetting_metrics_path = drive_root / "finetune/runB_mini_1000/forgetting_vietmed_metrics.json"

    runa = read_json(runa_metrics_path)
    runb = read_json(runb_metrics_path)
    forgetting = read_json(forgetting_metrics_path)
    run0 = read_json(Path(args.run0_val_metrics)) if args.run0_val_metrics else {}

    runa_wer = find_metric(runa, ["wer", "test_wer", "eval_wer"])
    runb_wer = find_metric(runb, ["wer", "test_wer", "eval_wer"])
    run0_wer = find_metric(run0, ["wer", "test_wer", "eval_wer"])
    forgetting_wer = find_metric(forgetting, ["wer", "test_wer", "eval_wer"])

    reasons = []

    runb_ok = not runb.get("_missing") and runb_wer is not None
    if not runb_ok:
        status = "DO_NOT_RUN_C_FIX_PIPELINE"
        reasons.append("Run B metrics are missing or invalid.")
    else:
        forgetting_ok = True
        if forgetting_wer is not None:
            forgetting_ok = as_rate(forgetting_wer) <= args.week5_vietmed_wer + args.forgetting_tolerance_abs

        if not forgetting_ok:
            status = "DO_NOT_RUN_C_FORGETTING_RISK"
            reasons.append("Run B degrades VietMed forgetting check beyond tolerance.")
        elif run0_wer is not None and runb_wer is not None:
            if as_rate(runb_wer) < as_rate(run0_wer):
                status = "PROCEED_TO_RUN_C"
                reasons.append("Run B improves ViMedCSS validation over Run 0 and forgetting is acceptable.")
            else:
                status = "DO_NOT_RUN_C_INSPECT_DATA_OR_PREPROCESSING"
                reasons.append("Run B does not improve over Run 0 validation baseline.")
        else:
            status = "PROCEED_TO_RUN_C_WITH_CAUTION"
            reasons.append("Run 0 baseline metrics were not provided; Run B ran technically and forgetting is acceptable.")

    decision = {
        "status": status,
        "reasons": reasons,
        "metrics": {
            "runA_wer": runa_wer,
            "runB_wer": runb_wer,
            "run0_wer": run0_wer,
            "forgetting_vietmed_wer": forgetting_wer,
            "week5_vietmed_wer_reference": args.week5_vietmed_wer,
            "forgetting_tolerance_abs": args.forgetting_tolerance_abs,
        },
        "paths": {
            "runA_metrics": str(runa_metrics_path),
            "runB_metrics": str(runb_metrics_path),
            "forgetting_metrics": str(forgetting_metrics_path),
            "run0_metrics": str(args.run0_val_metrics) if args.run0_val_metrics else None,
        },
    }

    out_dir = drive_root / "finetune"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_json = out_dir / "phase4_runA_runB_decision.json"
    out_md = out_dir / "PHASE4_RUNA_RUNB_DECISION.md"

    out_json.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# Phase 4 — Run A/B Decision")
    md.append("")
    md.append(f"## Status: **{status}**")
    md.append("")
    md.append("## Metrics")
    md.append("")
    md.append("| Item | WER |")
    md.append("|---|---:|")
    md.append(f"| Run 0 ViMedCSS validation baseline | {fmt_pct(run0_wer)} |")
    md.append(f"| Run A smoke eval | {fmt_pct(runa_wer)} |")
    md.append(f"| Run B mini eval | {fmt_pct(runb_wer)} |")
    md.append(f"| Run B VietMed forgetting eval | {fmt_pct(forgetting_wer)} |")
    md.append(f"| Week 5 VietMed reference | {fmt_pct(args.week5_vietmed_wer)} |")
    md.append("")
    md.append("## Reasons")
    md.append("")
    for reason in reasons:
        md.append(f"- {reason}")
    md.append("")
    md.append("## Decision rule")
    md.append("")
    md.append("- If Run B fails technically: fix script, do not run Run C.")
    md.append("- If Run B loss is flat/unstable: inspect data/preprocessing.")
    md.append("- If Run B improves ViMedCSS validation and does not strongly degrade VietMed dev: proceed to Run C.")
    md.append("")

    out_md.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(decision, ensure_ascii=False, indent=2))
    print(f"[DONE] {out_md}")
    print(f"[DONE] {out_json}")


if __name__ == "__main__":
    main()

