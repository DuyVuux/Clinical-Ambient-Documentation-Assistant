# runA_smoke_200 — PhoWhisper ViMedCSS Fine-tuning Report

## Objective

Progressive adaptation from the Week 5 PhoWhisper checkpoint on ViMedCSS subset archives.

## Inputs

- Train archive: `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runA_train_200.tar.gz`
- Eval archive: `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runA_eval_val_100.tar.gz`
- Initial model: `/content/drive/MyDrive/clinical_asr_models/phowhisper_vietmed_week5_checkpoint`

## Config

| Parameter | Value |
|---|---:|
| epochs | 1.0 |
| learning_rate | 5e-06 |
| train rows | 200 |
| eval rows | 100 |
| train skipped | 0 |
| eval skipped | 0 |

## Metrics

```json
{
  "created_at": "2026-06-18T04:16:35.256156+00:00",
  "run_name": "runA_smoke_200",
  "model": "/content/drive/MyDrive/clinical_asr_models/phowhisper_vietmed_week5_checkpoint",
  "train_archive": "/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runA_train_200.tar.gz",
  "eval_archive": "/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runA_eval_val_100.tar.gz",
  "n_train": 200,
  "n_eval": 100,
  "n_train_skipped": 0,
  "n_eval_skipped": 0,
  "train_metrics": {
    "train_runtime": 393.7661,
    "train_samples_per_second": 0.508,
    "train_steps_per_second": 0.033,
    "total_flos": 2.04120981504e+17,
    "train_loss": 27.685562133789062,
    "epoch": 1.0
  },
  "eval_metrics": {
    "test_loss": 1.3697600364685059,
    "test_wer": 0.3013698630136986,
    "test_cer": 0.19297334717895465,
    "test_runtime": 291.6186,
    "test_samples_per_second": 0.343,
    "test_steps_per_second": 0.343
  },
  "wer": 0.3013698630136986,
  "cer": 0.19297334717895465,
  "best_model_dir": "/content/drive/MyDrive/clinical_asr_vimedcss/finetune/runA_smoke_200/best_model"
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
