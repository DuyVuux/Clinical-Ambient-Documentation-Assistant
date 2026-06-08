#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT_DEFAULT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def normalize_selected_row(row: dict, split_name: str, selected_variant: str) -> dict:
    preprocessed_audio_path = (
        row.get("preprocessed_audio_path")
        or row.get("clean_audio_path")
        or row.get("audio")
    )

    if not preprocessed_audio_path:
        raise ValueError(f"Missing preprocessed audio path for sample_id={row.get('sample_id')}")

    output = {
        **row,
        "split_name": split_name,
        "selected_preprocessing": True,
        "selected_preprocessing_version": selected_variant,
        "preprocessing_version": selected_variant,
        "preprocessed_audio_path": preprocessed_audio_path,
        "clean_audio_path": preprocessed_audio_path,
        "selected_manifest_created_at": now_iso(),
        "selected_manifest_created_by": "Duy",
        "selected_manifest_version": "v0.1.0",
    }

    if split_name == "train":
        output["split_role"] = "train_candidate"
        output["train_allowed"] = True
    elif split_name == "dev":
        output["split_role"] = "dev_candidate"
        output["train_allowed"] = False

    return output


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--train_p03_manifest", required=True)
    parser.add_argument("--dev_p03_manifest", required=True)
    parser.add_argument("--output_train_selected", required=True)
    parser.add_argument("--output_dev_selected", required=True)
    parser.add_argument("--project_root", default=str(PROJECT_ROOT_DEFAULT))
    parser.add_argument("--selected_variant", default="p03_vad_pad_200ms")

    args = parser.parse_args()

    project_root = Path(args.project_root)

    train_manifest = Path(args.train_p03_manifest)
    dev_manifest = Path(args.dev_p03_manifest)
    out_train = Path(args.output_train_selected)
    out_dev = Path(args.output_dev_selected)

    if not train_manifest.is_absolute():
        train_manifest = project_root / train_manifest
    if not dev_manifest.is_absolute():
        dev_manifest = project_root / dev_manifest
    if not out_train.is_absolute():
        out_train = project_root / out_train
    if not out_dev.is_absolute():
        out_dev = project_root / out_dev

    train_rows = read_jsonl(train_manifest)
    dev_rows = read_jsonl(dev_manifest)

    selected_train = [
        normalize_selected_row(row, "train", args.selected_variant)
        for row in train_rows
    ]

    selected_dev = [
        normalize_selected_row(row, "dev", args.selected_variant)
        for row in dev_rows
    ]

    write_jsonl(out_train, selected_train)
    write_jsonl(out_dev, selected_dev)

    print(f"[DONE] train selected rows: {len(selected_train)} -> {out_train}")
    print(f"[DONE] dev selected rows: {len(selected_dev)} -> {out_dev}")


if __name__ == "__main__":
    main()