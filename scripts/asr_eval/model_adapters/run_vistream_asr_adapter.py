import json
import time
import argparse
from pathlib import Path

import soundfile as sf

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


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


def get_duration(audio_path: Path) -> float:
    info = sf.info(str(audio_path))
    return float(info.frames) / float(info.samplerate)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max_samples", type=int, default=None)
    args = parser.parse_args()

    from ViStreamASR import StreamingASR

    rows = read_jsonl(Path(args.manifest))
    if args.max_samples:
        rows = rows[:args.max_samples]

    asr = StreamingASR()
    outputs = []

    for i, row in enumerate(rows, start=1):
        audio_path = PROJECT_ROOT / row["clean_audio_path"]
        ref = row.get("transcript_text", "")
        duration = get_duration(audio_path)

        start = time.perf_counter()
        pred_parts = []
        failed = False
        error = None

        try:
            for result in asr.stream_from_file(str(audio_path)):
                if result.get("final"):
                    text = result.get("text", "").strip()
                    if text:
                        pred_parts.append(text)
            pred = " ".join(pred_parts).strip()
        except Exception as e:
            pred = ""
            failed = True
            error = str(e)

        runtime = time.perf_counter() - start
        rtf = runtime / duration if duration > 0 else None

        outputs.append({
            "sample_id": row["sample_id"],
            "model_name": "nguyenvulebinh/ViStreamASR",
            "clean_audio_path": row["clean_audio_path"],
            "reference_text": ref,
            "prediction_text": pred,
            "runtime_seconds": runtime,
            "audio_duration_seconds": duration,
            "rtf": rtf,
            "split_role": row.get("split_role", "dev"),
            "source_name": row.get("source_name", "VietMed"),
            "failed": failed,
            "error": error,
            "version": "v0.1.0"
        })

        print(f"[{i}/{len(rows)}] {row['sample_id']} rtf={rtf} failed={failed}")

    write_jsonl(Path(args.output), outputs)


if __name__ == "__main__":
    main()