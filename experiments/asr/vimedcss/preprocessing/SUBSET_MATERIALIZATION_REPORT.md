# ViMedCSS Subset Materialization Report

## Objective

Create run manifests and subset archives for ViMedCSS progressive fine-tuning.

## Mode

- manifests_only: `False`
- allow_missing_audio: `True`
- skip_runD: `True`

## Raw and eligible counts

| Split | Raw rows | Eligible rows |
|---|---:|---:|
| train | 11832 | 11828 |
| validation | 1714 | 1712 |
| test | 1614 | 1614 |
| hard | 658 | 658 |

- Suspect IDs loaded from Phase 1: `6`

## Generated subsets

| Subset | Rows | Hours | Manifest | Local archive | Drive archive | Copied audio | Missing audio | Mode |
|---|---:|---:|---|---|---|---:|---:|---|
| `run0_eval_val_200` | 200 | 0.4042 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/run0/run0_eval_val_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/run0_eval_val_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/run0_eval_val_200.tar.gz` | 200 | 0 | materialized_archive |
| `run0_eval_hard_200` | 200 | 0.4347 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/run0/run0_eval_hard_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/run0_eval_hard_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/run0_eval_hard_200.tar.gz` | 200 | 0 | materialized_archive |
| `run0_eval_test_200` | 200 | 0.4269 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/run0/run0_eval_test_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/run0_eval_test_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/run0_eval_test_200.tar.gz` | 200 | 0 | materialized_archive |
| `runA_train_200` | 200 | 0.4294 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runA/runA_train_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runA_train_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runA_train_200.tar.gz` | 200 | 0 | materialized_archive |
| `runA_eval_val_100` | 100 | 0.2156 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runA/runA_eval_val_100.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runA_eval_val_100.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runA_eval_val_100.tar.gz` | 100 | 0 | materialized_archive |
| `runB_train_1000` | 1000 | 2.1031 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runB/runB_train_1000.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runB_train_1000.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runB_train_1000.tar.gz` | 1000 | 0 | materialized_archive |
| `runB_eval_val_200` | 200 | 0.4158 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runB/runB_eval_val_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runB_eval_val_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runB_eval_val_200.tar.gz` | 200 | 0 | materialized_archive |
| `runB_eval_hard_200` | 200 | 0.4133 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runB/runB_eval_hard_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runB_eval_hard_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runB_eval_hard_200.tar.gz` | 200 | 0 | materialized_archive |
| `runC_train_4h` | 1938 | 4.0014 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runC/runC_train_4h.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runC_train_4h.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runC_train_4h.tar.gz` | 1938 | 0 | materialized_archive |
| `runC_eval_val_200` | 200 | 0.3989 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runC/runC_eval_val_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runC_eval_val_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runC_eval_val_200.tar.gz` | 200 | 0 | materialized_archive |
| `runC_eval_hard_200` | 200 | 0.4317 | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/runC/runC_eval_hard_200.jsonl` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/preprocessing/subset_archives/runC_eval_hard_200.tar.gz` | `/content/drive/MyDrive/clinical_asr_vimedcss/subset_archives/runC_eval_hard_200.tar.gz` | 200 | 0 | materialized_archive |

## Run C selection policy

| Group | Target ratio | Source split | Purpose |
|---|---:|---|---|
| High code-switching | 60–70% | train only | Adapt English medical terms |
| Normal medical Vietnamese | 20–30% | train only | Preserve Vietnamese medical ASR |
| Moderate noisy/hard-like | ~10% | train only | Robustness without broken samples |

Hard split is not used for training. Hard-like examples are selected from train split only.

## Guardrails

- No validation/test/hard samples are used for training.
- Run D is not created in Phase 2.
- Suspect samples from Phase 1 are excluded by default.
- Training should not read directly from Drive. Copy archive to `/content`, extract, then train.

## Next phase

Proceed to Phase 3 Run 0 baseline only after the Week 5 checkpoint warning is resolved.
