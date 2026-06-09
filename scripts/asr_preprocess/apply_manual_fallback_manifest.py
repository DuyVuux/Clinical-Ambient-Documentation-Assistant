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


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_review_csv(path: Path) -> dict[str, dict]:
    review = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            review[row["sample_id"]] = row
    return review


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--selected_manifest", required=True)
    parser.add_argument("--review_csv", required=True)
    parser.add_argument("--output_manifest", required=True)
    parser.add_argument("--project_root", default=str(PROJECT_ROOT_DEFAULT))
    args = parser.parse_args()

    project_root = Path(args.project_root)

    selected_manifest = Path(args.selected_manifest)
    review_csv = Path(args.review_csv)
    output_manifest = Path(args.output_manifest)

    if not selected_manifest.is_absolute():
        selected_manifest = project_root / selected_manifest
    if not review_csv.is_absolute():
        review_csv = project_root / review_csv
    if not output_manifest.is_absolute():
        output_manifest = project_root / output_manifest

    rows = read_jsonl(selected_manifest)
    review = read_review_csv(review_csv)

    out = []
    fallback_count = 0

    for row in rows:
        sample_id = str(row.get("sample_id", ""))
        decision = review.get(sample_id, {}).get("decision")

        if decision == "fallback_original":
            source_original = row.get("source_clean_audio_path")

            if not source_original:
                raise ValueError(f"Missing source_clean_audio_path for fallback sample {sample_id}")

            row = {
                **row,
                "manual_fallback_applied": True,
                "manual_fallback_reason": review[sample_id].get("reason"),
                "fallback_from_preprocessing": row.get("preprocessing_version"),
                "preprocessing_version": "p03_safe_hybrid_v0_1",
                "selected_preprocessing_version": "p03_safe_hybrid_v0_1",
                "preprocessed_audio_path": source_original,
                "clean_audio_path": source_original,
            }
            fallback_count += 1
        else:
            row = {
                **row,
                "manual_fallback_applied": False,
                "preprocessing_version": "p03_safe_hybrid_v0_1",
                "selected_preprocessing_version": "p03_safe_hybrid_v0_1",
            }

        out.append(row)

    write_jsonl(output_manifest, out)

    print(f"rows: {len(out)}")
    print(f"fallback_count: {fallback_count}")
    print(f"output: {output_manifest}")


if __name__ == "__main__":
    main()