# Week 6 Execution Readiness Check

## Decision

**PASS_WITH_WARNINGS**

## Context

- Project root: `.`
- ViMedCSS root: `experiments/asr/vimedcss`
- Drive root: `.`
- Week 5 checkpoint: `experiments/asr/finetune/week5/run_01_phowhisper_medium_conservative/best_model`

## Hard failures

No hard failures.

## Warnings

- `manifest_missing_audio_column:train`
- `manifest_missing_segment_text:train`
- `manifest_missing_audio_column:validation`
- `manifest_missing_segment_text:validation`
- `manifest_missing_audio_column:test`
- `manifest_missing_segment_text:test`
- `manifest_missing_audio_column:hard`
- `manifest_missing_segment_text:hard`
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
| `data_audit/dataset_inventory.json` | present | 0.0227 |
| `data_audit/split_inventory.md` | present | 0.0 |

## Raw manifests

| Split | Status | Rows | Has audio | Has segment_text | Has duration | Has cs_terms_count | Path |
|---|---|---:|---|---|---|---|---|
| train | present | 11832 | False | False | True | False | `experiments/asr/vimedcss/manifests/raw/vimedcss_train_raw.jsonl` |
| validation | present | 1 | False | False | False | False | `experiments/asr/vimedcss/manifests/raw/vimedcss_validation_raw.jsonl` |
| test | present | 1614 | False | False | True | False | `experiments/asr/vimedcss/manifests/raw/vimedcss_test_raw.jsonl` |
| hard | present | 658 | False | False | True | False | `experiments/asr/vimedcss/manifests/raw/vimedcss_hard_raw.jsonl` |

## Drive check

| Item | Value |
|---|---|
| path | `.` |
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
