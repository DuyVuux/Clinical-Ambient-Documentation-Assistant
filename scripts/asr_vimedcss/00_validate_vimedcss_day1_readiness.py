#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Week 6 Day 1 — ViMedCSS execution readiness validator.

This script checks:
- professional module-based skeleton
- no day-based experiment folders
- inventory/report preservation
- raw manifests presence
- Week 5 checkpoint presence
- Drive path readiness
- lightweight local policy

It writes:
- reports/WEEK6_EXECUTION_READINESS_CHECK.md
- reports/WEEK6_EXECUTION_READINESS_CHECK.json
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PROJECT_ROOT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def status(exists: bool) -> str:
    return "present" if exists else "missing"


def file_size_mb(path: Path) -> float | None:
    if not path.exists() or not path.is_file():
        return None
    return round(path.stat().st_size / (1024 * 1024), 4)


def count_jsonl_rows(path: Path, max_scan: int | None = None) -> int | None:
    if not path.exists() or not path.is_file():
        return None

    count = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                count += 1
                if max_scan is not None and count >= max_scan:
                    # We need exact count for small files, but manifests are still OK to count fully.
                    # Keeping this hook for future huge files.
                    pass
    return count


def read_first_jsonl(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None

    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    return {"_error": "invalid_jsonl_first_row"}
    return None


def detect_manifest_path(vimedcss_root: Path, split: str) -> Path:
    raw_path = vimedcss_root / "manifests" / "raw" / f"vimedcss_{split}_raw.jsonl"
    legacy_path = vimedcss_root / "manifests" / f"vimedcss_{split}_raw.jsonl"

    if raw_path.exists():
        return raw_path
    return legacy_path


def check_checkpoint(path: Path) -> dict[str, Any]:
    expected_any_model_file = [
        "model.safetensors",
        "pytorch_model.bin",
    ]
    expected_support_files = [
        "config.json",
        "generation_config.json",
        "preprocessor_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
    ]

    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "status": status(path.exists()),
        "files": {},
        "has_model_weights": False,
    }

    if not path.exists():
        return result

    for name in expected_support_files:
        p = path / name
        result["files"][name] = status(p.exists())

    for name in expected_any_model_file:
        p = path / name
        result["files"][name] = status(p.exists())
        if p.exists():
            result["has_model_weights"] = True

    if result["has_model_weights"]:
        result["status"] = "present"
    else:
        result["status"] = "incomplete"

    return result


def check_drive_path(drive_root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(drive_root),
        "exists": drive_root.exists(),
        "status": status(drive_root.exists()),
        "writable": False,
        "created_or_verified": False,
    }

    try:
        drive_root.mkdir(parents=True, exist_ok=True)
        probe = drive_root / ".week6_write_probe"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink(missing_ok=True)
        result["writable"] = True
        result["created_or_verified"] = True
        result["status"] = "present_writable"
    except Exception as exc:
        result["status"] = "not_writable_or_not_mounted"
        result["error"] = str(exc)

    return result


def list_day_based_folders(vimedcss_root: Path) -> list[str]:
    suspicious = []

    for path in vimedcss_root.rglob("*"):
        if not path.is_dir():
            continue

        name = path.name.lower()
        rel = path.relative_to(vimedcss_root)

        if name.startswith("day") or name in {"week6", "day1_setup", "day2_data_audit"}:
            suspicious.append(str(rel))

    return sorted(suspicious)


def build_readiness(project_root: Path, drive_root: Path, week5_checkpoint: Path) -> dict[str, Any]:
    vimedcss_root = project_root / "experiments" / "asr" / "vimedcss"

    core_dirs = [
        "data_audit",
        "manifests",
        "manifests/raw",
        "manifests/run0",
        "manifests/runA",
        "manifests/runB",
        "manifests/runC",
        "manifests/runD_optional",
        "manifests/forgetting_eval",
        "preprocessing",
        "preprocessing/subset_archives",
        "preprocessing/materialized_subsets",
        "baseline",
        "baseline/run0_original_phowhisper",
        "baseline/run0_week5_checkpoint",
        "finetune",
        "finetune/runA_smoke_200",
        "finetune/runB_mini_1000",
        "finetune/runC_balanced_4h",
        "finetune/runD_medium_8h_optional",
        "final_model",
        "final_model/selected_model",
        "reports",
    ]

    required_reports = [
        "reports/DAY1_VIMEDCSS_INVENTORY_REPORT.md",
        "reports/VIMEDCSS_TASK_BRIEF.md",
        "reports/COLAB_CPU_GPU_PROTOCOL.md",
        "reports/DRIVE_STORAGE_POLICY.md",
        "reports/TTS_DATA_REQUEST_MESSAGE.md",
        "preprocessing/PREPROCESSING_POLICY_VIMEDCSS.md",
    ]

    optional_inventory = [
        "data_audit/dataset_inventory.json",
        "data_audit/split_inventory.md",
    ]

    dir_checks = {
        d: status((vimedcss_root / d).exists())
        for d in core_dirs
    }

    report_checks = {
        r: {
            "status": status((vimedcss_root / r).exists()),
            "size_mb": file_size_mb(vimedcss_root / r),
        }
        for r in required_reports
    }

    optional_checks = {
        r: {
            "status": status((vimedcss_root / r).exists()),
            "size_mb": file_size_mb(vimedcss_root / r),
        }
        for r in optional_inventory
    }

    split_names = ["train", "validation", "test", "hard"]
    manifest_checks: dict[str, Any] = {}

    for split in split_names:
        path = detect_manifest_path(vimedcss_root, split)
        first = read_first_jsonl(path)
        columns = sorted(first.keys()) if isinstance(first, dict) and "_error" not in first else []
        manifest_checks[split] = {
            "path": str(path),
            "status": status(path.exists()),
            "rows": count_jsonl_rows(path),
            "size_mb": file_size_mb(path),
            "first_row_columns": columns,
            "has_audio_column": "audio" in columns,
            "has_text_column_segment_text": "segment_text" in columns,
            "has_duration_seconds": "duration_seconds" in columns,
            "has_cs_terms_count": "cs_terms_count" in columns,
        }

    drive_check = check_drive_path(drive_root)
    checkpoint_check = check_checkpoint(week5_checkpoint)
    day_based_folders = list_day_based_folders(vimedcss_root)

    hard_failures: list[str] = []
    warnings: list[str] = []

    for d, st in dir_checks.items():
        if st != "present":
            hard_failures.append(f"missing_dir:{d}")

    # Existing inventory report was explicitly expected by the plan, but if missing it can be regenerated.
    if report_checks["reports/DAY1_VIMEDCSS_INVENTORY_REPORT.md"]["status"] != "present":
        warnings.append("missing_existing_inventory_report:reports/DAY1_VIMEDCSS_INVENTORY_REPORT.md")

    for r in [
        "reports/VIMEDCSS_TASK_BRIEF.md",
        "reports/COLAB_CPU_GPU_PROTOCOL.md",
        "reports/DRIVE_STORAGE_POLICY.md",
        "preprocessing/PREPROCESSING_POLICY_VIMEDCSS.md",
    ]:
        if report_checks[r]["status"] != "present":
            hard_failures.append(f"missing_required_report:{r}")

    for split, chk in manifest_checks.items():
        if chk["status"] != "present":
            warnings.append(f"missing_raw_manifest:{split}")
        else:
            if not chk["has_audio_column"]:
                warnings.append(f"manifest_missing_audio_column:{split}")
            if not chk["has_text_column_segment_text"]:
                warnings.append(f"manifest_missing_segment_text:{split}")

    if checkpoint_check["status"] != "present":
        warnings.append("week5_checkpoint_missing_or_incomplete")

    if drive_check["status"] != "present_writable":
        warnings.append("drive_root_not_writable_or_not_mounted")

    if day_based_folders:
        warnings.append("day_based_folders_detected")

    decision = "PASS"
    if hard_failures:
        decision = "FAIL"
    elif warnings:
        decision = "PASS_WITH_WARNINGS"

    return {
        "created_at": now_iso(),
        "project_root": str(project_root),
        "vimedcss_root": str(vimedcss_root),
        "drive_root": str(drive_root),
        "week5_checkpoint": str(week5_checkpoint),
        "decision": decision,
        "hard_failures": hard_failures,
        "warnings": warnings,
        "core_dirs": dir_checks,
        "required_reports": report_checks,
        "optional_inventory": optional_checks,
        "raw_manifests": manifest_checks,
        "drive": drive_check,
        "week5_checkpoint_check": checkpoint_check,
        "day_based_folders_detected": day_based_folders,
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append("# Week 6 Execution Readiness Check")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"**{data['decision']}**")
    lines.append("")
    lines.append("## Context")
    lines.append("")
    lines.append(f"- Project root: `{data['project_root']}`")
    lines.append(f"- ViMedCSS root: `{data['vimedcss_root']}`")
    lines.append(f"- Drive root: `{data['drive_root']}`")
    lines.append(f"- Week 5 checkpoint: `{data['week5_checkpoint']}`")
    lines.append("")

    lines.append("## Hard failures")
    lines.append("")
    if data["hard_failures"]:
        for item in data["hard_failures"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("No hard failures.")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if data["warnings"]:
        for item in data["warnings"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("No warnings.")
    lines.append("")

    lines.append("## Core skeleton")
    lines.append("")
    lines.append("| Path | Status |")
    lines.append("|---|---|")
    for path, st in data["core_dirs"].items():
        lines.append(f"| `{path}` | {st} |")
    lines.append("")

    lines.append("## Required reports / policies")
    lines.append("")
    lines.append("| Artifact | Status | Size MB |")
    lines.append("|---|---|---:|")
    for path, info in data["required_reports"].items():
        lines.append(f"| `{path}` | {info['status']} | {info['size_mb']} |")
    lines.append("")

    lines.append("## Optional inventory artifacts")
    lines.append("")
    lines.append("| Artifact | Status | Size MB |")
    lines.append("|---|---|---:|")
    for path, info in data["optional_inventory"].items():
        lines.append(f"| `{path}` | {info['status']} | {info['size_mb']} |")
    lines.append("")

    lines.append("## Raw manifests")
    lines.append("")
    lines.append("| Split | Status | Rows | Has audio | Has segment_text | Has duration | Has cs_terms_count | Path |")
    lines.append("|---|---|---:|---|---|---|---|---|")
    for split, info in data["raw_manifests"].items():
        lines.append(
            f"| {split} | {info['status']} | {info['rows']} | "
            f"{info['has_audio_column']} | {info['has_text_column_segment_text']} | "
            f"{info['has_duration_seconds']} | {info['has_cs_terms_count']} | "
            f"`{info['path']}` |"
        )
    lines.append("")

    lines.append("## Drive check")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("|---|---|")
    for key, value in data["drive"].items():
        lines.append(f"| {key} | `{value}` |")
    lines.append("")

    lines.append("## Week 5 checkpoint check")
    lines.append("")
    lines.append(f"- Status: **{data['week5_checkpoint_check']['status']}**")
    lines.append(f"- Has model weights: `{data['week5_checkpoint_check']['has_model_weights']}`")
    lines.append("")
    lines.append("| File | Status |")
    lines.append("|---|---|")
    for name, st in data["week5_checkpoint_check"].get("files", {}).items():
        lines.append(f"| `{name}` | {st} |")
    lines.append("")

    lines.append("## Day-based folder policy")
    lines.append("")
    if data["day_based_folders_detected"]:
        lines.append("Day-based folders detected. Consider removing or archiving them:")
        lines.append("")
        for item in data["day_based_folders_detected"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("No day-based folders detected.")
    lines.append("")

    lines.append("## Next step")
    lines.append("")
    if data["decision"] == "PASS":
        lines.append("Proceed to Phase 1: sample-based data audit.")
    elif data["decision"] == "PASS_WITH_WARNINGS":
        lines.append("Proceed only after reviewing warnings. Missing raw manifests can be generated on Colab CPU if inventory already exists.")
    else:
        lines.append("Fix hard failures before continuing.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_root", default=str(DEFAULT_PROJECT_ROOT))
    parser.add_argument("--drive_root", default="/content/drive/MyDrive/clinical_asr_vimedcss")
    parser.add_argument(
        "--week5_checkpoint",
        default=None,
        help="Path to Week 5 PhoWhisper checkpoint. Defaults to project week5 run_01 best_model.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root)
    if args.week5_checkpoint:
        week5_checkpoint = Path(args.week5_checkpoint)
    else:
        week5_checkpoint = (
            project_root
            / "experiments/asr/finetune/week5/run_01_phowhisper_medium_conservative/best_model"
        )

    drive_root = Path(args.drive_root)
    vimedcss_root = project_root / "experiments/asr/vimedcss"

    data = build_readiness(
        project_root=project_root,
        drive_root=drive_root,
        week5_checkpoint=week5_checkpoint,
    )

    reports_dir = vimedcss_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    json_path = reports_dir / "WEEK6_EXECUTION_READINESS_CHECK.json"
    md_path = reports_dir / "WEEK6_EXECUTION_READINESS_CHECK.md"

    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(data), encoding="utf-8")

    print(json.dumps(
        {
            "decision": data["decision"],
            "hard_failures": data["hard_failures"],
            "warnings": data["warnings"],
            "markdown": str(md_path),
            "json": str(json_path),
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
