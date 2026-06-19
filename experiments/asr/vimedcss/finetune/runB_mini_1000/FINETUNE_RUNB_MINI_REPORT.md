# runB_mini_1000 — PhoWhisper ViMedCSS Fine-tuning Report

## Objective

Progressive adaptation from the Week 5 PhoWhisper checkpoint on ViMedCSS subset archives.

## Inputs

- Train archive: `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runB_train_1000.tar.gz`
- Eval archive: `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runB_eval_val_200.tar.gz`
- Initial model: `/content/drive/MyDrive/clinical_asr_models/phowhisper_vietmed_week5_checkpoint`

## Config

| Parameter | Value |
|---|---:|
| epochs | 2.0 |
| learning_rate | 5e-06 |
| train rows | 1000 |
| eval rows | 200 |
| train skipped | 0 |
| eval skipped | 0 |

## Metrics

```json
{
  "created_at": "2026-06-18T05:29:16.913530+00:00",
  "run_name": "runB_mini_1000",
  "model": "/content/drive/MyDrive/clinical_asr_models/phowhisper_vietmed_week5_checkpoint",
  "train_archive": "/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runB_train_1000.tar.gz",
  "eval_archive": "/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runB_eval_val_200.tar.gz",
  "n_train": 1000,
  "n_eval": 200,
  "n_train_skipped": 0,
  "n_eval_skipped": 0,
  "train_metrics": {
    "train_runtime": 2864.8398,
    "train_samples_per_second": 0.698,
    "train_steps_per_second": 0.087,
    "total_flos": 2.04120981504e+18,
    "train_loss": 4.941062538146973,
    "epoch": 2.0
  },
  "eval_metrics": {
    "test_loss": 0.513576090335846,
    "test_wer": 0.2284843869002285,
    "test_cer": 0.1494648478488982,
    "test_runtime": 579.4349,
    "test_samples_per_second": 0.345,
    "test_steps_per_second": 0.345
  },
  "wer": 0.2284843869002285,
  "cer": 0.1494648478488982,
  "best_model_dir": "/content/drive/MyDrive/clinical_asr_vimedcss/finetune/runB_mini_1000/best_model"
}
```

## Outputs

- `best_model/`
- `predictions_eval.jsonl`
- `metrics.json`
- `run_config.json`

## Guardrails

- Test/hard splits are not used for checkpoint selection.
- Run A/B train only from train-derived archives.
- Validation archive is used for evaluation/model selection only.
