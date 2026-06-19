#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4 — Train PhoWhisper from ViMedCSS subset archives.

Archive requirement:
- .tar.gz contains audio files and at least one .jsonl manifest.
- Manifest row should contain an audio field and a text field.

Accepted audio fields:
audio, audio_path, path, file_path, wav_path, local_audio_path

Accepted transcript fields:
segment_text, sentence, text, transcript, transcript_text, reference_text

Outputs:
- best_model/
- predictions_eval.jsonl
- metrics.json
- run_config.json
- FINETUNE_RUNA_SMOKE_REPORT.md or FINETUNE_RUNB_MINI_REPORT.md
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Union

import evaluate
import numpy as np
import torch
import soundfile as sf
import scipy.signal
import math
from datasets import Dataset
from transformers import (
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    WhisperForConditionalGeneration,
    WhisperProcessor,
    set_seed,
)

AUDIO_KEYS = ["audio", "audio_path", "path", "file_path", "wav_path", "local_audio_path"]
TEXT_KEYS = ["segment_text", "sentence", "text", "transcript", "transcript_text", "reference_text"]
ID_KEYS = ["sample_id", "segment_id", "id"]

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            row["_line_no"] = line_no
            rows.append(row)
    return rows

def safe_extract_tar(archive: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            target = (dst / member.name).resolve()
            if not str(target).startswith(str(dst.resolve())):
                raise RuntimeError(f"Unsafe path in tar archive: {member.name}")
        tar.extractall(dst)

def find_manifest(extract_dir: Path) -> Path:
    candidates = sorted(extract_dir.rglob("*.jsonl"))
    if not candidates:
        raise FileNotFoundError(f"No .jsonl manifest found under {extract_dir}")
    preferred = [p for p in candidates if "manifest" in p.name.lower()]
    return preferred[0] if preferred else candidates[0]

def pick_first(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in [None, ""]:
            return value
    return None

def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())

def resolve_audio_path(value: Any, extract_dir: Path, manifest_path: Path) -> Path | None:
    if isinstance(value, dict):
        value = value.get("path") or value.get("audio") or value.get("file")
    if value is None:
        return None
    p = Path(str(value).strip())
    if p.is_absolute() and p.exists():
        return p
    candidates = [manifest_path.parent / p, extract_dir / p, extract_dir / p.name]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = list(extract_dir.rglob(p.name))
    if matches:
        return sorted(matches)[0]
    return extract_dir / p

def normalize_archive_manifest(archive: Path, work_dir: Path, split: str, clean_work_dir: bool) -> tuple[Path, list[dict[str, Any]], list[dict[str, Any]]]:
    extract_dir = work_dir / f"{split}_extracted"
    if clean_work_dir and extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)
    safe_extract_tar(archive, extract_dir)
    manifest_path = find_manifest(extract_dir)
    rows = read_jsonl(manifest_path)
    valid: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for row in rows:
        sample_id = pick_first(row, ID_KEYS) or f"{split}_line_{row.get('_line_no')}"
        audio_value = pick_first(row, AUDIO_KEYS)
        text_value = pick_first(row, TEXT_KEYS)
        audio_path = resolve_audio_path(audio_value, extract_dir, manifest_path)
        sentence = clean_text(text_value)
        reasons = []
        if audio_path is None or not audio_path.exists():
            reasons.append(f"audio_missing:{audio_path}")
        if not sentence:
            reasons.append("text_missing")
        if reasons:
            skipped.append({"sample_id": sample_id, "line_no": row.get("_line_no"), "split": split, "reasons": reasons})
            continue
        valid.append({"sample_id": sample_id, "segment_id": row.get("segment_id"), "audio": str(audio_path), "sentence": sentence, "split": split, "duration_seconds": row.get("duration_seconds"), "cs_terms_count": row.get("cs_terms_count"), "cs_terms_list": row.get("cs_terms_list"), "topic": row.get("topic"), "source_manifest": str(manifest_path)})
    normalized_manifest = work_dir / f"{split}_normalized_manifest.jsonl"
    skipped_manifest = work_dir / f"{split}_skipped.jsonl"
    write_jsonl(normalized_manifest, valid)
    write_jsonl(skipped_manifest, skipped)
    print(f"[INFO] {split}: manifest={manifest_path}")
    print(f"[INFO] {split}: valid={len(valid)} skipped={len(skipped)}")
    return normalized_manifest, valid, skipped

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: WhisperProcessor
    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        label_features = [{"input_ids": f["labels"]} for f in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        bos_token_id = self.processor.tokenizer.bos_token_id
        if bos_token_id is not None and labels.shape[1] > 0:
            if torch.all(labels[:, 0] == bos_token_id).cpu().item():
                labels = labels[:, 1:]
        batch["labels"] = labels
        return batch

def normalize_metric_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip())

def load_audio_array(path: str, target_sr: int) -> tuple[np.ndarray, int]:
    """Load audio without datasets.Audio/torchcodec.

    This avoids torchcodec/FFmpeg compatibility issues on Colab.
    """
    audio, sr = sf.read(path, dtype="float32", always_2d=False)

    if getattr(audio, "ndim", 1) == 2:
        audio = audio.mean(axis=1)

    if int(sr) != int(target_sr):
        g = math.gcd(int(sr), int(target_sr))
        audio = scipy.signal.resample_poly(
            audio,
            int(target_sr) // g,
            int(sr) // g,
        ).astype("float32")
        sr = target_sr

    return audio, sr


def make_prepare_fn(processor: WhisperProcessor, sampling_rate: int):
    def prepare_dataset(batch: dict[str, Any]) -> dict[str, Any]:
        audio_array, sr = load_audio_array(batch["audio"], sampling_rate)
        batch["input_features"] = processor.feature_extractor(
            audio_array,
            sampling_rate=sr,
        ).input_features[0]
        batch["labels"] = processor.tokenizer(batch["sentence"]).input_ids
        return batch
    return prepare_dataset

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_archive", required=True)
    parser.add_argument("--eval_archive", required=True)
    parser.add_argument("--work_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--run_name", required=True)
    parser.add_argument("--epochs", type=float, default=1)
    parser.add_argument("--learning_rate", type=float, default=5e-6)
    parser.add_argument("--warmup_ratio", type=float, default=0.1)
    parser.add_argument("--weight_decay", type=float, default=0.01)
    parser.add_argument("--per_device_train_batch_size", type=int, default=1)
    parser.add_argument("--per_device_eval_batch_size", type=int, default=1)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=8)
    parser.add_argument("--optim", default="adafactor")
    parser.add_argument("--freeze_encoder", action="store_true")
    parser.add_argument("--sampling_rate", type=int, default=16000)
    parser.add_argument("--generation_max_length", type=int, default=225)
    parser.add_argument("--save_total_limit", type=int, default=2)
    parser.add_argument("--logging_steps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--clean_work_dir", action="store_true")
    parser.add_argument("--debug_max_steps", type=int, default=None)
    parser.add_argument("--max_train_samples", type=int, default=None)
    parser.add_argument("--max_eval_samples", type=int, default=None)
    args = parser.parse_args()
    train_archive = Path(args.train_archive)
    eval_archive = Path(args.eval_archive)
    work_dir = Path(args.work_dir)
    output_dir = Path(args.output_dir)
    if not train_archive.exists(): raise FileNotFoundError(f"Missing train archive: {train_archive}")
    if not eval_archive.exists(): raise FileNotFoundError(f"Missing eval archive: {eval_archive}")
    work_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    set_seed(args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    train_manifest, train_rows, train_skipped = normalize_archive_manifest(train_archive, work_dir, "train", args.clean_work_dir)
    eval_manifest, eval_rows, eval_skipped = normalize_archive_manifest(eval_archive, work_dir, "eval", args.clean_work_dir)
    if not train_rows: raise RuntimeError("No valid train rows.")
    if not eval_rows: raise RuntimeError("No valid eval rows.")
    processor = WhisperProcessor.from_pretrained(args.model, language="vi", task="transcribe")
    model = WhisperForConditionalGeneration.from_pretrained(args.model)
    model.config.use_cache = False

    if args.freeze_encoder:
        print("[INFO] Freezing Whisper encoder to reduce VRAM usage.")
        try:
            model.freeze_encoder()
        except Exception:
            for p in model.model.encoder.parameters():
                p.requires_grad = False

    try: model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="vi", task="transcribe")
    except Exception as exc: print(f"[WARN] Could not set forced_decoder_ids: {exc}")
    model.config.suppress_tokens = []
    train_ds = Dataset.from_json(str(train_manifest))
    eval_ds_raw = Dataset.from_json(str(eval_manifest))
    if args.max_train_samples is not None: train_ds = train_ds.select(range(min(args.max_train_samples, len(train_ds))))
    if args.max_eval_samples is not None: eval_ds_raw = eval_ds_raw.select(range(min(args.max_eval_samples, len(eval_ds_raw))))
    eval_meta = [{"sample_id": row["sample_id"], "segment_id": row.get("segment_id"), "reference_text": row["sentence"], "audio": row["audio"], "topic": row.get("topic"), "cs_terms_count": row.get("cs_terms_count")} for row in eval_ds_raw]
    prepare_fn = make_prepare_fn(processor, args.sampling_rate)
    train_ds = train_ds.map(prepare_fn, remove_columns=train_ds.column_names, num_proc=1)
    eval_ds = eval_ds_raw.map(prepare_fn, remove_columns=eval_ds_raw.column_names, num_proc=1)
    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor)
    wer_metric = evaluate.load("wer"); cer_metric = evaluate.load("cer")
    def compute_metrics(pred):
        pred_ids = pred.predictions; label_ids = pred.label_ids
        label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
        pred_str = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
        label_str = processor.tokenizer.batch_decode(label_ids, skip_special_tokens=True)
        pred_norm = [normalize_metric_text(x) for x in pred_str]
        label_norm = [normalize_metric_text(x) for x in label_str]
        return {"wer": wer_metric.compute(predictions=pred_norm, references=label_norm), "cer": cer_metric.compute(predictions=pred_norm, references=label_norm)}
    fp16 = torch.cuda.is_available()
    max_steps = args.debug_max_steps if args.debug_max_steps is not None else -1
    training_args = Seq2SeqTrainingArguments(output_dir=str(output_dir), run_name=args.run_name, per_device_train_batch_size=args.per_device_train_batch_size, per_device_eval_batch_size=args.per_device_eval_batch_size, gradient_accumulation_steps=args.gradient_accumulation_steps, learning_rate=args.learning_rate, warmup_ratio=args.warmup_ratio, weight_decay=args.weight_decay, num_train_epochs=args.epochs, fp16=fp16, gradient_checkpointing=True, eval_strategy="epoch", save_strategy="epoch", logging_steps=args.logging_steps, predict_with_generate=True, generation_max_length=args.generation_max_length, save_total_limit=args.save_total_limit, load_best_model_at_end=True, metric_for_best_model="wer", greater_is_better=False, report_to=[], remove_unused_columns=False, max_steps=max_steps, optim=args.optim)
    trainer = Seq2SeqTrainer(args=training_args, model=model, train_dataset=train_ds, eval_dataset=eval_ds, data_collator=data_collator, compute_metrics=compute_metrics, processing_class=processor.feature_extractor)
    train_output = trainer.train()
    best_model_dir = output_dir / "best_model"
    trainer.save_model(str(best_model_dir))
    processor.save_pretrained(str(best_model_dir))
    pred_output = trainer.predict(eval_ds)
    pred_ids = pred_output.predictions; label_ids = pred_output.label_ids
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
    pred_texts = processor.tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    predictions = []
    for idx, pred_text in enumerate(pred_texts):
        meta = eval_meta[idx]
        predictions.append({"sample_id": meta["sample_id"], "segment_id": meta.get("segment_id"), "run_name": args.run_name, "model": args.model, "audio": meta.get("audio"), "topic": meta.get("topic"), "cs_terms_count": meta.get("cs_terms_count"), "reference_text": meta["reference_text"], "prediction_text": pred_text})
    write_jsonl(output_dir / "predictions_eval.jsonl", predictions)
    metrics = {"created_at": now_iso(), "run_name": args.run_name, "model": args.model, "train_archive": str(train_archive), "eval_archive": str(eval_archive), "n_train": len(train_ds), "n_eval": len(eval_ds), "n_train_skipped": len(train_skipped), "n_eval_skipped": len(eval_skipped), "train_metrics": train_output.metrics, "eval_metrics": pred_output.metrics, "wer": pred_output.metrics.get("test_wer"), "cer": pred_output.metrics.get("test_cer"), "best_model_dir": str(best_model_dir)}
    write_json(output_dir / "metrics.json", metrics)
    write_json(output_dir / "run_config.json", {"run_name": args.run_name, "epochs": args.epochs, "learning_rate": args.learning_rate, "model": args.model, "train_archive": str(train_archive), "eval_archive": str(eval_archive), "work_dir": str(work_dir), "output_dir": str(output_dir)})
    report_name = "FINETUNE_RUN_REPORT.md"
    if "runa" in args.run_name.lower(): report_name = "FINETUNE_RUNA_SMOKE_REPORT.md"
    elif "runb" in args.run_name.lower(): report_name = "FINETUNE_RUNB_MINI_REPORT.md"
    report = f"""# {args.run_name} — PhoWhisper ViMedCSS Fine-tuning Report\n\n## Objective\n\nProgressive adaptation from the Week 5 PhoWhisper checkpoint on ViMedCSS subset archives.\n\n## Inputs\n\n- Train archive: `{train_archive}`\n- Eval archive: `{eval_archive}`\n- Initial model: `{args.model}`\n\n## Config\n\n| Parameter | Value |\n|---|---:|\n| epochs | {args.epochs} |\n| learning_rate | {args.learning_rate} |\n| train rows | {len(train_ds)} |\n| eval rows | {len(eval_ds)} |\n| train skipped | {len(train_skipped)} |\n| eval skipped | {len(eval_skipped)} |\n\n## Metrics\n\n```json\n{json.dumps(metrics, ensure_ascii=False, indent=2)}\n```\n\n## Outputs\n\n- `best_model/`\n- `predictions_eval.jsonl`\n- `metrics.json`\n- `run_config.json`\n\n## Guardrails\n\n- Test/hard splits are not used for checkpoint selection.\n- Run A/B train only from train-derived archives.\n- Validation archive is used for evaluation/model selection only.\n"""
    (output_dir / report_name).write_text(report, encoding="utf-8")
    print(json.dumps({"status": "DONE", "run_name": args.run_name, "output_dir": str(output_dir), "best_model": str(best_model_dir), "predictions": str(output_dir / "predictions_eval.jsonl"), "metrics": str(output_dir / "metrics.json")}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
