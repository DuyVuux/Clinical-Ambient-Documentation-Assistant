# Phase 3 — Run 0 ViMedCSS Baseline Report

## Objective

Measure the Week 5 VietMed PhoWhisper checkpoint on ViMedCSS subsets before ViMedCSS fine-tuning. This is baseline only; no training is performed.

## Results

| Model | Eval set | Samples | Strict WER | Strict CER | Normalized WER | Normalized CER | Runtime/sample | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Week5 checkpoint | validation 200 | 200 | 32.48% | 22.26% | 25.49% | 19.98% | 3.2256 | model-selection baseline |
| Week5 checkpoint | hard 200 | 200 | 38.60% | 25.14% | 31.13% | 22.55% | 3.3751 | reporting/stress only |
| Week5 checkpoint | test 200 | missing | TBD | TBD | TBD | TBD | TBD | reporting-only if executed |
| Original PhoWhisper | validation 200 | missing | TBD | TBD | TBD | TBD | TBD | optional comparison |

## Metric files

| Model | Eval set | Status | Metrics path |
|---|---|---|---|
| Week5 checkpoint | validation 200 | present | `/content/drive/MyDrive/clinical_asr_vimedcss/baseline/run0_week5_checkpoint/metrics_val_200.json` |
| Week5 checkpoint | hard 200 | present | `/content/drive/MyDrive/clinical_asr_vimedcss/baseline/run0_week5_checkpoint/metrics_hard_200.json` |
| Week5 checkpoint | test 200 | missing | `/content/drive/MyDrive/clinical_asr_vimedcss/baseline/run0_week5_checkpoint/metrics_test_200.json` |
| Original PhoWhisper | validation 200 | missing | `/content/drive/MyDrive/clinical_asr_vimedcss/baseline/run0_original_phowhisper/metrics_val_200.json` |

## Interpretation

Use validation 200 as the main Run 0 baseline for comparing Run A/B/C. Hard 200 is reporting/stress only. Test 200, if executed, is reporting-only and must not be used to choose hyperparameters or checkpoints.

## Gate to Phase 4

Proceed to Run A only if validation baseline completed, predictions/metrics exist, audio path resolution worked, and predictions are not systematically empty.

## Drive root

`/content/drive/MyDrive/clinical_asr_vimedcss`
