import json
import argparse
from pathlib import Path

import torch
import soundfile as sf
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


PROJECT_ROOT = Path("/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant")


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


def load_audio_16k(path: Path):
    audio, sr = sf.read(str(path))

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        sr = 16000

    return audio, sr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--model", required=True, help="HF model id or local checkpoint path")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max_samples", type=int, default=None)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"[INFO] Loading processor/model: {args.model}")
    processor = Wav2Vec2Processor.from_pretrained(args.model)
    model = Wav2Vec2ForCTC.from_pretrained(args.model)
    model.to(device)
    model.eval()

    rows = read_jsonl(Path(args.manifest))
    if args.max_samples:
        rows = rows[:args.max_samples]

    outputs = []

    for i, row in enumerate(rows, start=1):
        audio_path = PROJECT_ROOT / row["clean_audio_path"]

        try:
            audio, sr = load_audio_16k(audio_path)

            inputs = processor(
                audio,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            )

            input_values = inputs.input_values.to(device)

            with torch.no_grad():
                logits = model(input_values).logits

            pred_ids = torch.argmax(logits, dim=-1)
            pred = processor.batch_decode(pred_ids)[0].strip()

        except Exception as e:
            pred = ""
            print(f"[FAIL] {row['sample_id']}: {e}")

        outputs.append({
            "sample_id": row["sample_id"],
            "model_name": args.model,
            "model_family": "wav2vec2_xlsr_ctc",
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