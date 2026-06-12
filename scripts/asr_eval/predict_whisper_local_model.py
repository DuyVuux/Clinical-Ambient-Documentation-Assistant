#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run inference using a saved local Whisper/PhoWhisper model.

This script does NOT train.
It only loads a saved model directory and predicts on a JSONL manifest.

Expected manifest row:
{
  "sample_id": "...",
  "audio": "/path/to/audio.wav",
  "sentence": "reference transcript",
  ...
}

Output prediction row:
{
  "sample_id": "...",
  "model_name": "...",
  "run_name": "...",
  "preprocessing_version": "...",
  "audio": "...",
  "reference_text": "...",
  "prediction_text": "..."
}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import librosa
import torch
from transformers import WhisperForConditionalGeneration, WhisperProcessor


PROJECT_ROOT_DEFAULT = Path(
    "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
)


def resolve_path(path_value: str, project_root: Path) -> Path:
    p = Path(path_value)

    if p.is_absolute():
        return p

    return project_root / p


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def get_audio_path(row: dict[str, Any]) -> str:
    candidate_keys = [
        "audio",
        "audio_path",
        "clean_audio_path",
        "preprocessed_audio_path",
    ]

    for key in candidate_keys:
        value = row.get(key)

        if isinstance(value, str) and value.strip():
            return value

    raise KeyError(
        "Cannot find audio path in row. Expected one of: "
        + ", ".join(candidate_keys)
    )


def get_reference_text(row: dict[str, Any]) -> str:
    candidate_keys = [
        "sentence",
        "reference_text",
        "text",
        "transcript",
    ]

    for key in candidate_keys:
        value = row.get(key)

        if isinstance(value, str):
            return value

    return ""


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument("--run_name", required=True)
    parser.add_argument("--language", default="vi")
    parser.add_argument("--task", default="transcribe")
    parser.add_argument("--sampling_rate", type=int, default=16000)
    parser.add_argument("--max_length", type=int, default=225)
    parser.add_argument("--device", type=str, default=None, help="Force device (e.g. cpu or cuda)")

    parser.add_argument(
        "--project_root",
        default=str(PROJECT_ROOT_DEFAULT),
    )

    args = parser.parse_args()

    project_root = Path(args.project_root)

    model_dir = resolve_path(args.model_dir, project_root)
    manifest_path = resolve_path(args.manifest, project_root)
    output_path = resolve_path(args.output, project_root)

    if not model_dir.exists():
        raise FileNotFoundError(f"model_dir not found: {model_dir}")

    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")

    print(f"[INFO] model_dir: {model_dir}")
    print(f"[INFO] manifest:  {manifest_path}")
    print(f"[INFO] output:    {output_path}")

    if args.device:
        device = args.device
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] device: {device}")

    processor = WhisperProcessor.from_pretrained(
        str(model_dir),
        language=args.language,
        task=args.task,
    )

    model = WhisperForConditionalGeneration.from_pretrained(str(model_dir))
    model.to(device)
    model.eval()

    if device == "cuda":
        model = model.half()

    try:
        forced_decoder_ids = processor.get_decoder_prompt_ids(
            language=args.language,
            task=args.task,
        )
        model.config.forced_decoder_ids = forced_decoder_ids
    except Exception as exc:
        print(f"[WARN] Could not set forced_decoder_ids: {exc}")
        forced_decoder_ids = None

    rows = read_jsonl(manifest_path)
    prediction_rows = []

    print(f"[INFO] number of rows: {len(rows)}")

    for idx, row in enumerate(rows, start=1):
        sample_id = row.get("sample_id", f"sample_{idx}")
        audio_path_value = get_audio_path(row)
        audio_path = resolve_path(audio_path_value, project_root)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio not found for sample_id={sample_id}: {audio_path}"
            )

        audio_array, sr = librosa.load(
            str(audio_path),
            sr=args.sampling_rate,
            mono=True,
        )

        inputs = processor.feature_extractor(
            audio_array,
            sampling_rate=args.sampling_rate,
            return_tensors="pt",
        )

        input_features = inputs.input_features.to(device)

        if device == "cuda":
            input_features = input_features.half()

        with torch.no_grad():
            try:
                generated_ids = model.generate(
                    input_features,
                    max_length=args.max_length,
                    forced_decoder_ids=forced_decoder_ids,
                )
            except TypeError:
                generated_ids = model.generate(
                    input_features,
                    max_length=args.max_length,
                )

        prediction_text = processor.tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]

        prediction_rows.append(
            {
                "sample_id": sample_id,
                "model_name": str(model_dir),
                "run_name": args.run_name,
                "preprocessing_version": row.get("preprocessing_version"),
                "audio": str(audio_path),
                "reference_text": get_reference_text(row),
                "prediction_text": prediction_text,
            }
        )

        if idx % 20 == 0 or idx == len(rows):
            print(f"[INFO] predicted {idx}/{len(rows)}")

    write_jsonl(output_path, prediction_rows)

    print(f"[DONE] wrote predictions: {output_path}")


if __name__ == "__main__":
    main()