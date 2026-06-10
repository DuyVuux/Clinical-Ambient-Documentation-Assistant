#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fine-tune PhoWhisper/Whisper Seq2Seq model from JSONL manifests.
Input manifest row format:
{
  "sample_id": "...",
  "audio": "/abs/path/to/audio.wav",
  "sentence": "...",
  "language": "vi",
  "task": "transcribe",
  "split": "train"
}
Main outputs:
- HuggingFace checkpoints
- predictions_dev.jsonl
- metrics_dev.json
- RUN_REPORT.md
Example: python scripts/asr_eval/finetune_phowhisper_seq2seq.py \
  --config experiments/asr/finetune/week5/configs/run_01_phowhisper_medium_conservative.json
"""
from __future__ import annotations
import argparse
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

import evaluate
import numpy as np
import torch
from datasets import Audio, Dataset
from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    set_seed,
)

# Automatically resolve project root based on the script's location (works on Local & Colab)
PROJECT_ROOT_DEFAULT = Path(__file__).resolve().parent.parent.parent

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def resolve_path(path_value: str, project_root: Path) -> Path:
    p = Path(path_value)
    if p.is_absolute():
        return p
    return project_root / p

def load_jsonl_dataset(manifest_path: Path, project_root: Path, sampling_rate: int = 16000) -> Dataset:
    dataset = Dataset.from_json(str(manifest_path))
    
    # Map absolute local paths to correct project_root paths
    def fix_path(example):
        old_path = example["audio"]
        if "data/data_lake" in old_path:
            rel_part = old_path[old_path.find("data/data_lake"):]
            example["audio"] = str(project_root / rel_part)
        return example
        
    dataset = dataset.map(fix_path)
    dataset = dataset.cast_column("audio", Audio(sampling_rate=sampling_rate))
    return dataset

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: WhisperProcessor

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        
        # Remove BOS token if tokenizer added it consistently.
        if labels.shape[1] > 0:
            bos_token_id = self.processor.tokenizer.bos_token_id
            if bos_token_id is not None and torch.all(labels[:, 0] == bos_token_id).cpu().item():
                labels = labels[:, 1:]
        
        batch["labels"] = labels
        return batch

def build_prepare_fn(processor: WhisperProcessor):
    def prepare_dataset(batch: dict[str, Any]) -> dict[str, Any]:
        audio = batch["audio"]
        inputs = processor.feature_extractor(
            audio["array"], sampling_rate=audio["sampling_rate"]
        )
        batch["input_features"] = inputs.input_features[0]
        labels = processor.tokenizer(batch["sentence"]).input_ids
        batch["labels"] = labels
        return batch
    return prepare_dataset

def normalize_for_metric(text: str) -> str:
    # Minimal normalization for metric display only.
    # Your official WER script can still be used afterward for strict/normalized WER.
    return " ".join(text.strip().split())

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--project_root", default=str(PROJECT_ROOT_DEFAULT))
    parser.add_argument("--max_train_samples", type=int, default=None)
    parser.add_argument("--max_eval_samples", type=int, default=None)
    parser.add_argument("--debug_max_steps", type=int, default=None)
    args = parser.parse_args()
    
    project_root = Path(args.project_root)
    config_path = resolve_path(args.config, project_root)
    cfg = read_json(config_path)
    
    output_dir = resolve_path(cfg["output_dir"], project_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    seed = int(cfg.get("seed", 42))
    set_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    train_manifest = resolve_path(cfg["train_manifest"], project_root)
    dev_manifest = resolve_path(cfg["dev_manifest"], project_root)
    
    if not train_manifest.exists():
        raise FileNotFoundError(f"Train manifest not found: {train_manifest}")
    if not dev_manifest.exists():
        raise FileNotFoundError(f"Dev manifest not found: {dev_manifest}")
    
    if cfg.get("test_holdout_used") is True:
        raise ValueError("test_holdout_used is true. This is forbidden in Week 5.")
        
    model_name = cfg["base_model"]
    language = cfg.get("language", "vi")
    task = cfg.get("task", "transcribe")
    
    print(f"[INFO] Loading processor/model: {model_name}")
    processor = WhisperProcessor.from_pretrained(
        model_name, language=language, task=task,
    )
    model = WhisperForConditionalGeneration.from_pretrained(model_name)
    
    # Force Vietnamese transcription prompt if supported.
    try:
        model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(
            language=language, task=task,
        )
    except Exception as exc:
        print(f"[WARN] Could not set forced_decoder_ids: {exc}")
        
    model.config.suppress_tokens = []
    
    train_ds = load_jsonl_dataset(train_manifest, project_root)
    dev_ds = load_jsonl_dataset(dev_manifest, project_root)
    
    if args.max_train_samples is not None:
        train_ds = train_ds.select(range(min(args.max_train_samples, len(train_ds))))
    if args.max_eval_samples is not None:
        dev_ds = dev_ds.select(range(min(args.max_eval_samples, len(dev_ds))))
        
    raw_dev_rows = [
        {
            "sample_id": row["sample_id"],
            "reference_text": row["sentence"],
            "audio": row["audio"],
            "preprocessing_version": row.get("preprocessing_version"),
        }
        for row in dev_ds
    ]
    
    prepare_fn = build_prepare_fn(processor)
    print("[INFO] Preparing train dataset...")
    train_ds = train_ds.map(
        prepare_fn, remove_columns=train_ds.column_names, num_proc=1,
    )
    print("[INFO] Preparing dev dataset...")
    dev_ds_prepared = dev_ds.map(
        prepare_fn, remove_columns=dev_ds.column_names, num_proc=1,
    )
    
    data_collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)
    wer_metric = evaluate.load("wer")
    cer_metric = evaluate.load("cer")
    
    def compute_metrics(pred):
        pred_ids = pred.predictions
        label_ids = pred.label_ids
        label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
        pred_str = processor.tokenizer.batch_decode(
            pred_ids, skip_special_tokens=True,
        )
        label_str = processor.tokenizer.batch_decode(
            label_ids, skip_special_tokens=True,
        )
        pred_norm = [normalize_for_metric(x) for x in pred_str]
        label_norm = [normalize_for_metric(x) for x in label_str]
        wer = wer_metric.compute(predictions=pred_norm, references=label_norm)
        cer = cer_metric.compute(predictions=pred_norm, references=label_norm)
        return {
            "wer": wer,
            "cer": cer,
        }
        
    fp16 = bool(cfg.get("fp16", True)) and torch.cuda.is_available()
    max_steps = args.debug_max_steps if args.debug_max_steps is not None else -1
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        per_device_train_batch_size=int(cfg.get("per_device_train_batch_size", 1)),
        per_device_eval_batch_size=int(cfg.get("per_device_eval_batch_size", 1)),
        gradient_accumulation_steps=int(cfg.get("gradient_accumulation_steps", 8)),
        learning_rate=float(cfg.get("learning_rate", 1e-5)),
        warmup_ratio=float(cfg.get("warmup_ratio", 0.1)),
        num_train_epochs=float(cfg.get("epochs", 3)),
        weight_decay=float(cfg.get("weight_decay", 0.01)),
        gradient_checkpointing=bool(cfg.get("gradient_checkpointing", True)),
        fp16=fp16,
        eval_strategy=cfg.get("eval_strategy", "epoch"),
        save_strategy=cfg.get("save_strategy", "epoch"),
        logging_steps=int(cfg.get("logging_steps", 10)),
        predict_with_generate=bool(cfg.get("predict_with_generate", True)),
        generation_max_length=int(cfg.get("generation_max_length", 225)),
        save_total_limit=int(cfg.get("save_total_limit", 2)),
        load_best_model_at_end=True,
        metric_for_best_model=cfg.get("metric_for_best_model", "wer"),
        greater_is_better=bool(cfg.get("greater_is_better", False)),
        report_to=[],
        remove_unused_columns=False,
        max_steps=max_steps,
    )
    
    trainer = Seq2SeqTrainer(
        args=training_args,
        model=model,
        train_dataset=train_ds,
        eval_dataset=dev_ds_prepared,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        processing_class=processor.feature_extractor,
    )
    
    print("[INFO] Starting training...")
    train_result = trainer.train()
    trainer.save_model(str(output_dir / "best_model"))
    processor.save_pretrained(str(output_dir / "best_model"))
    
    print("[INFO] Predicting dev set...")
    pred_output = trainer.predict(dev_ds_prepared)
    pred_ids = pred_output.predictions
    label_ids = pred_output.label_ids
    label_ids[label_ids == -100] = processor.tokenizer.pad_token_id
    pred_texts = processor.tokenizer.batch_decode(
        pred_ids, skip_special_tokens=True,
    )
    ref_texts = processor.tokenizer.batch_decode(
        label_ids, skip_special_tokens=True,
    )
    
    prediction_rows = []
    for i, pred_text in enumerate(pred_texts):
        raw = raw_dev_rows[i]
        prediction_rows.append({
            "sample_id": raw["sample_id"],
            "model_name": model_name,
            "run_name": cfg["run_name"],
            "preprocessing_version": raw.get("preprocessing_version"),
            "audio": raw["audio"],
            "reference_text": raw["reference_text"],
            "prediction_text": pred_text,
        })
        
    predictions_path = output_dir / "predictions_dev.jsonl"
    write_jsonl(predictions_path, prediction_rows)
    
    metrics = {
        "run_name": cfg["run_name"],
        "base_model": model_name,
        "preprocessing_version": cfg.get("preprocessing_version"),
        "train_manifest": str(train_manifest),
        "dev_manifest": str(dev_manifest),
        "n_train": len(train_ds),
        "n_dev": len(dev_ds_prepared),
        "train_result": train_result.metrics,
        "eval_metrics_from_trainer": pred_output.metrics,
        "test_holdout_used": False,
    }
    write_json(output_dir / "metrics_dev.json", metrics)
    
    report = []
    report.append(f"# {cfg['run_name']} — Fine-tune Report")
    report.append("")
    report.append("## Config")
    report.append("")
    report.append(f"- Base model: `{model_name}`")
    report.append(f"- Preprocessing: `{cfg.get('preprocessing_version')}`")
    report.append(f"- Train rows: {len(train_ds)}")
    report.append(f"- Dev rows: {len(dev_ds_prepared)}")
    report.append(f"- Learning rate: {cfg.get('learning_rate')}")
    report.append(f"- Epochs: {cfg.get('epochs')}")
    report.append("")
    report.append("## Trainer metrics")
    report.append("")
    report.append("```json")
    report.append(json.dumps(pred_output.metrics, ensure_ascii=False, indent=2))
    report.append("```")
    report.append("")
    report.append("## Guardrails")
    report.append("")
    report.append("- test_holdout was not used.")
    report.append("- dev was used only for validation.")
    report.append("- transcripts were not edited.")
    report.append("")
    (output_dir / "RUN_01_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    
    print(f"[DONE] predictions: {predictions_path}")
    print(f"[DONE] metrics: {output_dir / 'metrics_dev.json'}")
    print(f"[DONE] model: {output_dir / 'best_model'}")

if __name__ == "__main__":
    main()