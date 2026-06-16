# Week 6 Execution Readiness Check

## Decision

**PASS_WITH_WARNINGS**

## Context

- Project root: `/content/Clinical-Ambient-Documentation-Assistant`
- ViMedCSS root: `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss`
- Drive root: `/content/drive/MyDrive/clinical_asr_vimedcss`
- Week 5 checkpoint: `/content/drive/MyDrive/clinical_asr_models/phowhisper_vietmed_week5_checkpoint`

## Hard failures

No hard failures.

## Warnings

- `week5_checkpoint_missing_or_incomplete`

## Core skeleton

| Path | Status |
|---|---|
| `data_audit` | present |
| `manifests` | present |
| `manifests/raw` | present |
| `manifests/run0` | present |
| `manifests/runA` | present |
| `manifests/runB` | present |
| `manifests/runC` | present |
| `manifests/runD_optional` | present |
| `manifests/forgetting_eval` | present |
| `preprocessing` | present |
| `preprocessing/subset_archives` | present |
| `preprocessing/materialized_subsets` | present |
| `baseline` | present |
| `baseline/run0_original_phowhisper` | present |
| `baseline/run0_week5_checkpoint` | present |
| `finetune` | present |
| `finetune/runA_smoke_200` | present |
| `finetune/runB_mini_1000` | present |
| `finetune/runC_balanced_4h` | present |
| `finetune/runD_medium_8h_optional` | present |
| `final_model` | present |
| `final_model/selected_model` | present |
| `reports` | present |

## Required reports / policies

| Artifact | Status | Size MB |
|---|---|---:|
| `reports/DAY1_VIMEDCSS_INVENTORY_REPORT.md` | present | 0.0009 |
| `reports/VIMEDCSS_TASK_BRIEF.md` | present | 0.0012 |
| `reports/COLAB_CPU_GPU_PROTOCOL.md` | present | 0.0012 |
| `reports/DRIVE_STORAGE_POLICY.md` | present | 0.001 |
| `reports/TTS_DATA_REQUEST_MESSAGE.md` | present | 0.0008 |
| `preprocessing/PREPROCESSING_POLICY_VIMEDCSS.md` | present | 0.0012 |

## Optional inventory artifacts

| Artifact | Status | Size MB |
|---|---|---:|
| `data_audit/dataset_inventory.json` | missing | None |
| `data_audit/split_inventory.md` | missing | None |

## Raw manifests

| Split | Status | Rows | Has audio | Has segment_text | Has duration | Has cs_terms_count | Path |
|---|---|---:|---|---|---|---|---|
| train | present | 11832 | True | True | True | True | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_train_raw.jsonl` |
| validation | present | 1714 | True | True | True | True | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_validation_raw.jsonl` |
| test | present | 1614 | True | True | True | True | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_test_raw.jsonl` |
| hard | present | 658 | True | True | True | True | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_hard_raw.jsonl` |

## Drive check

| Item | Value |
|---|---|
| path | `/content/drive/MyDrive/clinical_asr_vimedcss` |
| exists | `True` |
| status | `present_writable` |
| writable | `True` |
| created_or_verified | `True` |

## Week 5 checkpoint check

- Status: **missing**
- Has model weights: `False`

| File | Status |
|---|---|

## Day-based folder policy

No day-based folders detected.

## Next step

Proceed only after reviewing warnings. Missing raw manifests can be generated on Colab CPU if inventory already exists.
