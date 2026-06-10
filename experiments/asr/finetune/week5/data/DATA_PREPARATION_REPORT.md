# Day 2 Week 5 — PhoWhisper Fine-tune Data Preparation

## Objective

Prepare train/dev manifests for fine-tuning `vinai/PhoWhisper-medium`.

## Frozen preprocessing

`p03_safe_hybrid_v0_1`

## Input manifests

| Split | Input manifest |
|---|---|
| train | `data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl` |
| dev | `data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_safe_v0_1.jsonl` |

## Summary

| Split | Rows | Skipped | Manual fallback | Mean duration | Mean words | Output |
|---|---:|---:|---:|---:|---:|---|
| train | 600 | 0 | 4 | 6.0746 | 25.45 | `experiments/asr/finetune/week5/data/train_manifest_for_phowhisper.jsonl` |
| dev | 200 | 0 | 0 | 5.9826 | 25.735 | `experiments/asr/finetune/week5/data/dev_manifest_for_phowhisper.jsonl` |

## Detailed Duration (Seconds)

| Split | Min | p10 | Median | p90 | Max |
|---|---:|---:|---:|---:|---:|
| train | 1.0 | 5.0 | 6.0 | 7.0 | 13.0 |
| dev | 2.0 | 5.0 | 6.0 | 7.0 | 8.0 |

## Detailed Transcript Word Count

| Split | Min | Median | Max |
|---|---:|---:|---:|
| train | 1 | 27.0 | 39 |
| dev | 9 | 27.0 | 39 |

## Guardrails Enforced

- Transcript text was minimally whitespace-cleaned only.
- No semantic transcript editing was performed.
- test_holdout was not used.
- The output uses absolute local audio paths for HuggingFace loading.

## Output schema

Each row contains:

```json
{
  "sample_id": "...",
  "audio": "/absolute/path/to/audio.wav",
  "sentence": "...",
  "language": "vi",
  "task": "transcribe",
  "split": "train/dev",
  "preprocessing_version": "p03_safe_hybrid_v0_1"
}
```