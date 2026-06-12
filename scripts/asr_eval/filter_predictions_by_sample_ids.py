#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--sample_ids_jsonl", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--id_field", default="sample_id")

    args = parser.parse_args()

    pred_path = Path(args.predictions)
    ids_path = Path(args.sample_ids_jsonl)
    out_path = Path(args.output)

    id_rows = read_jsonl(ids_path)
    sample_ids = {
        r[args.id_field]
        for r in id_rows
        if args.id_field in r
    }

    pred_rows = read_jsonl(pred_path)
    subset = [
        r
        for r in pred_rows
        if r.get(args.id_field) in sample_ids
    ]

    write_jsonl(out_path, subset)

    print("sample_ids:", len(sample_ids))
    print("pred_rows:", len(pred_rows))
    print("subset_rows:", len(subset))
    print("output:", out_path)


if __name__ == "__main__":
    main()