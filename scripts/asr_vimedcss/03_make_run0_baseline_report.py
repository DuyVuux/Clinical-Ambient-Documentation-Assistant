#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def pct(v: Any) -> str:
    if v is None:
        return "TBD"
    try:
        return f"{float(v) * 100:.2f}%"
    except Exception:
        return "TBD"

def row(model: str, eval_set: str, path: Path, notes: str) -> dict[str, Any]:
    m = read_json(path)
    if m is None:
        return {"model": model, "eval_set": eval_set, "samples": "missing", "wer": "TBD", "cer": "TBD", "nwer": "TBD", "ncer": "TBD", "runtime": "TBD", "notes": notes, "status": "missing", "path": str(path)}
    return {"model": model, "eval_set": eval_set, "samples": m.get("n_prepared"), "wer": pct(m.get("strict_wer")), "cer": pct(m.get("strict_cer")), "nwer": pct(m.get("normalized_wer")), "ncer": pct(m.get("normalized_cer")), "runtime": m.get("runtime_seconds_per_sample"), "notes": notes, "status": "present", "path": str(path)}

def render(rows: list[dict[str, Any]], drive_root: Path) -> str:
    lines = []
    lines.append("# Phase 3 — Run 0 ViMedCSS Baseline Report\n")
    lines.append("## Objective\n")
    lines.append("Measure the Week 5 VietMed PhoWhisper checkpoint on ViMedCSS subsets before ViMedCSS fine-tuning. This is baseline only; no training is performed.\n")
    lines.append("## Results\n")
    lines.append("| Model | Eval set | Samples | Strict WER | Strict CER | Normalized WER | Normalized CER | Runtime/sample | Notes |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(f"| {r['model']} | {r['eval_set']} | {r['samples']} | {r['wer']} | {r['cer']} | {r['nwer']} | {r['ncer']} | {r['runtime']} | {r['notes']} |")
    lines.append("\n## Metric files\n")
    lines.append("| Model | Eval set | Status | Metrics path |")
    lines.append("|---|---|---|---|")
    for r in rows:
        lines.append(f"| {r['model']} | {r['eval_set']} | {r['status']} | `{r['path']}` |")
    lines.append("\n## Interpretation\n")
    lines.append("Use validation 200 as the main Run 0 baseline for comparing Run A/B/C. Hard 200 is reporting/stress only. Test 200, if executed, is reporting-only and must not be used to choose hyperparameters or checkpoints.\n")
    lines.append("## Gate to Phase 4\n")
    lines.append("Proceed to Run A only if validation baseline completed, predictions/metrics exist, audio path resolution worked, and predictions are not systematically empty.\n")
    lines.append("## Drive root\n")
    lines.append(f"`{drive_root}`\n")
    return "\n".join(lines)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--drive_root", required=True)
    ap.add_argument("--output_report", required=True)
    args = ap.parse_args()
    drive = Path(args.drive_root)
    rows = [
        row("Week5 checkpoint", "validation 200", drive / "baseline/run0_week5_checkpoint/metrics_val_200.json", "model-selection baseline"),
        row("Week5 checkpoint", "hard 200", drive / "baseline/run0_week5_checkpoint/metrics_hard_200.json", "reporting/stress only"),
        row("Week5 checkpoint", "test 200", drive / "baseline/run0_week5_checkpoint/metrics_test_200.json", "reporting-only if executed"),
        row("Original PhoWhisper", "validation 200", drive / "baseline/run0_original_phowhisper/metrics_val_200.json", "optional comparison"),
    ]
    out = Path(args.output_report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(rows, drive), encoding="utf-8")
    print(json.dumps({"status": "DONE", "output_report": str(out), "rows": rows}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
