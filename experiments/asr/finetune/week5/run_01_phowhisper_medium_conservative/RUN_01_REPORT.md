# Run 01 — PhoWhisper-medium Conservative Fine-tune

## Objective

Run a conservative learning-rate fine-tuning experiment for `vinai/PhoWhisper-medium`.

## Config

| Parameter | Value |
|---|---|
| base model | `vinai/PhoWhisper-medium` |
| preprocessing | `p03_safe_hybrid_v0_1` |
| learning rate | `1e-5` |
| epochs | `3` |
| train samples | `600` |
| dev samples | `200` |

## Outputs

- `best_model/`
- `predictions_dev.jsonl`
- `metrics_dev_project_wer.json`
- `medical_errors_dev.json`

## Guardrails

- test_holdout was not used
- dev was not used for training
- transcripts were not edited
