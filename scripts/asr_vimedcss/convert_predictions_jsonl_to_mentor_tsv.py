#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path


def pick(row, keys, default=""):
    for k in keys:
        v = row.get(k)
        if v is not None and str(v).strip():
            return str(v)
    return default


def clean_cell(text: str) -> str:
    return str(text).replace("\t", " ").replace("\n", " ").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions_jsonl", required=True)
    ap.add_argument("--reference_tsv", required=True)
    ap.add_argument("--prediction_tsv", required=True)
    args = ap.parse_args()

    src = Path(args.predictions_jsonl)
    ref_out = Path(args.reference_tsv)
    hyp_out = Path(args.prediction_tsv)

    if not src.exists():
        raise FileNotFoundError(f"Missing predictions JSONL: {src}")

    ref_out.parent.mkdir(parents=True, exist_ok=True)
    hyp_out.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with src.open("r", encoding="utf-8", errors="replace") as f, \
         ref_out.open("w", encoding="utf-8") as rf, \
         hyp_out.open("w", encoding="utf-8") as hf:
        for line in f:
            line = line.strip()
            if not line:
                continue

            row = json.loads(line)
            sid = pick(row, ["sample_id", "segment_id", "id"], f"sample_{n:06d}")
            ref = pick(row, ["reference_text", "segment_text", "sentence", "text"])
            hyp = pick(row, ["prediction_text", "predicted_text", "prediction", "hypothesis", "hyp"])

            rf.write(f"{clean_cell(sid)}\t{clean_cell(ref)}\n")
            hf.write(f"{clean_cell(sid)}\t{clean_cell(hyp)}\n")
            n += 1

    print(f"[DONE] converted {n} rows")
    print(f"reference_tsv={ref_out}")
    print(f"prediction_tsv={hyp_out}")


if __name__ == "__main__":
    main()
