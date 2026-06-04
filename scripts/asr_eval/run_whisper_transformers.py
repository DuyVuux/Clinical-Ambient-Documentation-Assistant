import json
import argparse
from pathlib import Path

import torch
from transformers import pipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def read_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--max_samples", type=int, default=None)
    args = parser.parse_args()

    if args.device == "auto":
        device = 0 if torch.cuda.is_available() else -1
    else:
        device = int(args.device)

    asr = pipeline(
        "automatic-speech-recognition",
        model=args.model,
        device=device,
        generate_kwargs={
            "language": "vi",
            "task": "transcribe"
        }
    )

    rows = read_jsonl(args.manifest)
    if args.max_samples:
        rows = rows[:args.max_samples]

    outputs = []

    for i, row in enumerate(rows, start=1):
        audio_path = PROJECT_ROOT / row["clean_audio_path"]
        ref = row.get("transcript_text", "")

        try:
            result = asr(str(audio_path))
            pred = result["text"].strip()
        except Exception as e:
            pred = ""
            print(f"[FAIL] {row['sample_id']}: {e}")

        outputs.append({
            "sample_id": row["sample_id"],
            "model_name": args.model,
            "clean_audio_path": row["clean_audio_path"],
            "reference_text": ref,
            "prediction_text": pred,
            "split_role": row.get("split_role"),
            "source_name": row.get("source_name"),
            "version": "v0.1.0"
        })

        print(f"[{i}/{len(rows)}] {row['sample_id']}")

    write_jsonl(args.output, outputs)


if __name__ == "__main__":
    main()