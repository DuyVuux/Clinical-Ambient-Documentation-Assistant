import json
import argparse
from pathlib import Path

from chunkformer import ChunkFormerModel


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def extract_text(output):
    """
    ChunkFormer output can vary by version.
    This function makes extraction more robust.
    """
    if output is None:
        return ""

    if isinstance(output, str):
        return output.strip()

    if isinstance(output, dict):
        for key in ["text", "transcription", "transcript"]:
            if key in output and isinstance(output[key], str):
                return output[key].strip()

        if "segments" in output and isinstance(output["segments"], list):
            parts = []
            for seg in output["segments"]:
                if isinstance(seg, dict):
                    txt = seg.get("text") or seg.get("transcription") or ""
                    parts.append(txt)
                elif isinstance(seg, str):
                    parts.append(seg)
            return " ".join(parts).strip()

    if isinstance(output, list):
        parts = []
        for item in output:
            parts.append(extract_text(item))
        return " ".join([p for p in parts if p]).strip()

    return str(output).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="khanhld/chunkformer-ctc-large-vie")
    parser.add_argument("--max_samples", type=int, default=None)
    parser.add_argument("--chunk_size", type=int, default=64)
    parser.add_argument("--left_context_size", type=int, default=128)
    parser.add_argument("--right_context_size", type=int, default=128)
    parser.add_argument("--total_batch_duration", type=int, default=1800)
    args = parser.parse_args()

    rows = read_jsonl(Path(args.manifest))
    if args.max_samples:
        rows = rows[:args.max_samples]

    print(f"[INFO] Loading ChunkFormer model: {args.model}")
    model = ChunkFormerModel.from_pretrained(args.model)

    outputs = []

    for i, row in enumerate(rows, start=1):
        audio_path = PROJECT_ROOT / row["clean_audio_path"]

        try:
            result = model.endless_decode(
                audio_path=str(audio_path),
                chunk_size=args.chunk_size,
                left_context_size=args.left_context_size,
                right_context_size=args.right_context_size,
                total_batch_duration=args.total_batch_duration,
                return_timestamps=False
            )
            pred = extract_text(result)
        except Exception as e:
            pred = ""
            print(f"[FAIL] {row['sample_id']}: {e}")

        outputs.append({
            "sample_id": row["sample_id"],
            "model_name": args.model,
            "model_family": "chunkformer_ctc",
            "clean_audio_path": row["clean_audio_path"],
            "reference_text": row.get("transcript_text", ""),
            "prediction_text": pred,
            "split_role": row.get("split_role"),
            "source_name": row.get("source_name"),
            "version": "v0.1.0"
        })

        print(f"[{i}/{len(rows)}] {row['sample_id']}")

    write_jsonl(Path(args.output), outputs)
    print(f"[DONE] wrote predictions to {args.output}")


if __name__ == "__main__":
    main()