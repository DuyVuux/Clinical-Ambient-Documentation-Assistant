#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
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


def resolve_path(path_value: str | None, project_root: Path) -> str:
    if not path_value:
        return ""
    p = Path(path_value)
    if p.is_absolute():
        return str(p)
    return str(project_root / p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--output_jsonl", required=True)
    parser.add_argument("--project_root", default=str(PROJECT_ROOT_DEFAULT))
    parser.add_argument("--shrink_threshold", type=float, default=0.8)
    args = parser.parse_args()

    project_root = Path(args.project_root)

    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = project_root / manifest

    rows = read_jsonl(manifest)

    risky = []

    for row in rows:
        sample_id = row.get("sample_id")

        orig = row.get("original_duration_seconds")
        proc = row.get("processed_duration_seconds")

        cfg = row.get("preprocessing_config", {})
        vad_fallback = cfg.get("vad_fallback", False)

        shrink_risky = False
        duration_delta = None
        shrink_ratio = None

        if isinstance(orig, (int, float)) and isinstance(proc, (int, float)) and orig > 0:
            duration_delta = proc - orig
            shrink_ratio = proc / orig
            shrink_risky = proc < orig * args.shrink_threshold

        if vad_fallback or shrink_risky:
            risky.append({
                "sample_id": sample_id,
                "split_role": row.get("split_role"),
                "transcript_text": row.get("transcript_text", ""),
                "source_clean_audio_path": resolve_path(row.get("source_clean_audio_path"), project_root),
                "selected_audio_path": resolve_path(row.get("preprocessed_audio_path") or row.get("clean_audio_path"), project_root),
                "original_duration_seconds": orig,
                "processed_duration_seconds": proc,
                "duration_delta_seconds": duration_delta,
                "shrink_ratio": shrink_ratio,
                "vad_fallback": vad_fallback,
                "vad_reason": cfg.get("vad_reason"),
                "speech_start_sample": cfg.get("speech_start_sample"),
                "speech_end_sample": cfg.get("speech_end_sample"),
                "trim_start_sample": cfg.get("trim_start_sample"),
                "trim_end_sample": cfg.get("trim_end_sample"),
                "kept_ratio": cfg.get("kept_ratio"),
                "review_decision": "pending_manual_review",
                "recommended_action": "inspect_original_vs_p03",
            })

    output_csv = Path(args.output_csv)
    output_jsonl = Path(args.output_jsonl)

    if not output_csv.is_absolute():
        output_csv = project_root / output_csv
    if not output_jsonl.is_absolute():
        output_jsonl = project_root / output_jsonl

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    with output_jsonl.open("w", encoding="utf-8") as f:
        for item in risky:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "sample_id",
            "split_role",
            "original_duration_seconds",
            "processed_duration_seconds",
            "duration_delta_seconds",
            "shrink_ratio",
            "vad_fallback",
            "vad_reason",
            "source_clean_audio_path",
            "selected_audio_path",
            "transcript_text",
            "review_decision",
            "recommended_action",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in risky:
            writer.writerow({k: item.get(k) for k in fieldnames})

    print(f"rows: {len(rows)}")
    print(f"risky: {len(risky)}")
    print(f"csv: {output_csv}")
    print(f"jsonl: {output_jsonl}")


if __name__ == "__main__":
    main()