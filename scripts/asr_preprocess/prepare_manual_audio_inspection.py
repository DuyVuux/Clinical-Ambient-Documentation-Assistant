#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import shutil
from pathlib import Path


PROJECT_ROOT_DEFAULT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def safe_copy(src: str, dst: Path) -> str:
    src_path = Path(src)
    if not src_path.exists():
        return "missing"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst)
    return "copied"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--risky_jsonl", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--project_root", default=str(PROJECT_ROOT_DEFAULT))
    args = parser.parse_args()

    project_root = Path(args.project_root)

    risky_jsonl = Path(args.risky_jsonl)
    if not risky_jsonl.is_absolute():
        risky_jsonl = project_root / risky_jsonl

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    rows = read_jsonl(risky_jsonl)

    report_lines = []
    report_lines.append("# Manual VAD Risk Inspection Package")
    report_lines.append("")
    report_lines.append("| Sample | Original | P03 selected | Delta | Decision |")
    report_lines.append("|---|---|---|---:|---|")

    for row in rows:
        sample_id = row["sample_id"]

        sample_dir = output_dir / sample_id
        original_dst = sample_dir / f"{sample_id}_original.wav"
        p03_dst = sample_dir / f"{sample_id}_p03_selected.wav"
        metadata_dst = sample_dir / f"{sample_id}_metadata.json"

        original_status = safe_copy(row.get("source_clean_audio_path", ""), original_dst)
        p03_status = safe_copy(row.get("selected_audio_path", ""), p03_dst)

        metadata_dst.write_text(
            json.dumps(row, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        report_lines.append(
            f"| {sample_id} | {original_status} | {p03_status} | "
            f"{row.get('duration_delta_seconds')} | pending |"
        )

    report_path = output_dir / "MANUAL_INSPECTION_README.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"items: {len(rows)}")
    print(f"output_dir: {output_dir}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()