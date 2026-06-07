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


def load_audio(audio_path: Path):
    samples, sample_rate = sf.read(str(audio_path), dtype="float32")
    if len(samples.shape) > 1:
        samples = samples[:, 0]
    return samples, sample_rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--encoder", required=True)
    parser.add_argument("--decoder", required=True)
    parser.add_argument("--joiner", required=True)
    parser.add_argument("--tokens", required=True)
    parser.add_argument("--max_samples", type=int, default=None)
    args = parser.parse_args()

    import sherpa_onnx

    recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=args.encoder,
        decoder=args.decoder,
        joiner=args.joiner,
        tokens=args.tokens,
        num_threads=2,
        sample_rate=16000,
        feature_dim=80,
        decoding_method="greedy_search"
    )

    rows = read_jsonl(Path(args.manifest))
    if args.max_samples:
        rows = rows[:args.max_samples]

    outputs = []

    for i, row in enumerate(rows, start=1):
        audio_path = PROJECT_ROOT / row["clean_audio_path"]
        ref = row.get("transcript_text", "")
        duration = get_duration(audio_path)

        start = time.perf_counter()
        failed = False
        error = None

        try:
            samples, sample_rate = load_audio(audio_path)
            if sample_rate != 16000:
                raise ValueError(f"Expected 16kHz audio, got {sample_rate}")

            stream = recognizer.create_stream()
            stream.accept_waveform(16000, samples)
            recognizer.decode_stream(stream)
            pred = stream.result.text.strip()
        except Exception as e:
            pred = ""
            failed = True
            error = str(e)

        runtime = time.perf_counter() - start
        rtf = runtime / duration if duration > 0 else None

        outputs.append({
            "sample_id": row["sample_id"],
            "model_name": "hynt/Zipformer-30M-RNNT-6000h",
            "clean_audio_path": row["clean_audio_path"],
            "reference_text": ref,
            "prediction_text": pred,
            "runtime_seconds": runtime,
            "audio_duration_seconds": duration,
            "rtf": rtf,
            "split_role": row.get("split_role", "dev"),
            "source_name": row.get("source_name", "VietMed"),
            "license_status": "cc-by-nc-nd-4.0",
            "allowed_use": ["evaluation", "reference_only"],
            "failed": failed,
            "error": error,
            "version": "v0.1.0"
        })

        print(f"[{i}/{len(rows)}] {row['sample_id']} rtf={rtf} failed={failed}")

    write_jsonl(Path(args.output), outputs)


if __name__ == "__main__":
    main()