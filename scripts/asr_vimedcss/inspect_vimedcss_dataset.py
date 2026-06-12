#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

from datasets import load_dataset


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def find_audio_column(columns: list[str]) -> str | None:
    candidates = ["audio", "wav", "path", "audio_path", "file", "speech"]
    for c in candidates:
        if c in columns:
            return c
    return None


def find_text_column(columns: list[str]) -> str | None:
    candidates = ["text", "sentence", "transcript", "transcription", "normalized_text"]
    for c in candidates:
        if c in columns:
            return c
    return None


def audio_duration_from_row(row: dict, audio_col: str | None) -> float | None:
    if not audio_col or audio_col not in row:
        return None

    audio = row[audio_col]

    if isinstance(audio, dict):
        arr = audio.get("array")
        sr = audio.get("sampling_rate")
        if arr is not None and sr:
            return len(arr) / float(sr)

    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_id", default="tensorxt/ViMedCSS")
    parser.add_argument("--output_dir", default="experiments/asr/vimedcss")
    parser.add_argument("--max_preview", type=int, default=5)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    manifest_dir = out_dir / "manifests"
    audit_dir = out_dir / "data_audit"
    report_dir = out_dir / "reports"

    print(f"[INFO] Loading dataset: {args.dataset_id}")
    ds = load_dataset(args.dataset_id)

    inventory = {
        "dataset_id": args.dataset_id,
        "created_at": now_iso(),
        "splits": {},
    }

    md_lines = []
    md_lines.append("# Day 1 — ViMedCSS Dataset Inventory")
    md_lines.append("")
    md_lines.append(f"Dataset: `{args.dataset_id}`")
    md_lines.append("")
    md_lines.append("| Split | Rows | Columns | Audio column | Text column |")
    md_lines.append("|---|---:|---|---|---|")

    for split_name, split_ds in ds.items():
        columns = list(split_ds.column_names)
        audio_col = find_audio_column(columns)
        text_col = find_text_column(columns)

        rows_out = []
        durations = []
        empty_text = 0

        for idx, row in enumerate(split_ds):
            text = row.get(text_col, "") if text_col else ""
            if not isinstance(text, str) or not text.strip():
                empty_text += 1

            duration = audio_duration_from_row(row, audio_col)
            if duration is not None:
                durations.append(duration)

            audio_info = row.get(audio_col) if audio_col else None
            audio_path = None
            sampling_rate = None

            if isinstance(audio_info, dict):
                audio_path = audio_info.get("path")
                sampling_rate = audio_info.get("sampling_rate")

            rows_out.append({
                "sample_id": f"vimedcss_{split_name}_{idx:06d}",
                "dataset_id": args.dataset_id,
                "split": split_name,
                "row_index": idx,
                "audio_col": audio_col,
                "text_col": text_col,
                "audio_path": audio_path,
                "sampling_rate": sampling_rate,
                "duration_seconds": duration,
                "text": text,
                "created_at": now_iso(),
            })

        manifest_path = manifest_dir / f"vimedcss_{split_name}_raw.jsonl"
        write_jsonl(manifest_path, rows_out)

        duration_summary = {
            "count_with_duration": len(durations),
            "total_hours": sum(durations) / 3600 if durations else None,
            "min_seconds": min(durations) if durations else None,
            "max_seconds": max(durations) if durations else None,
            "mean_seconds": sum(durations) / len(durations) if durations else None,
        }

        inventory["splits"][split_name] = {
            "num_rows": len(split_ds),
            "columns": columns,
            "audio_col": audio_col,
            "text_col": text_col,
            "empty_text": empty_text,
            "manifest_path": str(manifest_path),
            "duration_summary": duration_summary,
            "preview": [
                {k: str(split_ds[i][k])[:300] for k in columns}
                for i in range(min(args.max_preview, len(split_ds)))
            ],
        }

        md_lines.append(
            f"| `{split_name}` | {len(split_ds)} | `{columns}` | `{audio_col}` | `{text_col}` |"
        )

    write_json(audit_dir / "dataset_inventory.json", inventory)
    (audit_dir / "split_inventory.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    (report_dir / "DAY1_VIMEDCSS_INVENTORY_REPORT.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("[DONE] inventory written")
    print(audit_dir / "dataset_inventory.json")


if __name__ == "__main__":
    main()