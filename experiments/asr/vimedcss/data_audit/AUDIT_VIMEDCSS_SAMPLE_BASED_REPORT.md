# ViMedCSS Sample-based Data Audit Report

## Objective

Audit existing ViMedCSS manifests before subset creation and progressive fine-tuning.

This phase does not train models, does not materialize audio, and does not use GPU.

## Outputs

- `vimedcss_audit_summary.csv`
- `vimedcss_audit_samples.csv`
- `vimedcss_suspect_samples.csv`
- `vimedcss_topic_summary.csv`
- `vimedcss_cs_term_summary.csv`
- `vimedcss_schema_examples.json`
- `vimedcss_audit_summary.json`

## Split summary

| Split | Rows | Total hours | Mean duration | Median duration | Mean words | Mean CS terms | Suspect samples | Suspect rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 11832 | 24.3036 | 7.3946 | 7.0 | 26.4129 | 1.0407 | 11832 | 1.0 |
| validation | 1714 | 3.5681 | 7.4942 | 7.0 | 26.0146 | 1.0583 | 1714 | 1.0 |
| test | 1614 | 3.3889 | 7.5589 | 7.0 | 26.855 | 1.0502 | 1614 | 1.0 |
| hard | 658 | 1.3828 | 7.5653 | 7.0 | 25.0213 | 1.152 | 658 | 1.0 |

## Manifest paths

| Split | Manifest |
|---|---|
| train | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_train_raw.jsonl` |
| validation | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_validation_raw.jsonl` |
| test | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_test_raw.jsonl` |
| hard | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_hard_raw.jsonl` |

## Field presence

Counts below show how many rows have non-empty values for each expected field.

### train

| Field | Present rows |
|---|---:|
| `segment_id` | 11832 |
| `audio` | 11832 |
| `duration_seconds` | 11832 |
| `segment_text` | 11832 |
| `cs_terms_list` | 11832 |
| `cs_terms_count` | 11832 |
| `topic` | 11832 |
| `original_video_link` | 11832 |
| `original_video_title` | 11832 |
| `start_time` | 11832 |
| `end_time` | 11832 |

### validation

| Field | Present rows |
|---|---:|
| `segment_id` | 1714 |
| `audio` | 1714 |
| `duration_seconds` | 1714 |
| `segment_text` | 1714 |
| `cs_terms_list` | 1714 |
| `cs_terms_count` | 1714 |
| `topic` | 1714 |
| `original_video_link` | 1714 |
| `original_video_title` | 1714 |
| `start_time` | 1714 |
| `end_time` | 1714 |

### test

| Field | Present rows |
|---|---:|
| `segment_id` | 1614 |
| `audio` | 1614 |
| `duration_seconds` | 1614 |
| `segment_text` | 1614 |
| `cs_terms_list` | 1614 |
| `cs_terms_count` | 1614 |
| `topic` | 1614 |
| `original_video_link` | 1614 |
| `original_video_title` | 1614 |
| `start_time` | 1614 |
| `end_time` | 1614 |

### hard

| Field | Present rows |
|---|---:|
| `segment_id` | 658 |
| `audio` | 658 |
| `duration_seconds` | 658 |
| `segment_text` | 658 |
| `cs_terms_list` | 658 |
| `cs_terms_count` | 658 |
| `topic` | 658 |
| `original_video_link` | 658 |
| `original_video_title` | 658 |
| `start_time` | 658 |
| `end_time` | 658 |

## Suspect reasons

| Reason | Count |
|---|---:|
| `duration_mismatch_start_end_gt_1s` | 15818 |
| `too_few_words_le_1` | 3 |
| `duration_too_long_gt_25s` | 3 |

## Schema examples

Saved to:

```text
/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/data_audit/vimedcss_schema_examples.json
```

## Decision guidance

Proceed to Phase 2 if:

```text
1. Raw manifests are present.
2. audio and segment_text fields exist.
3. Suspect samples are identified, not silently ignored.
4. Official splits are preserved.
```

Do not proceed to training if:

```text
1. train/validation/test/hard manifests are missing.
2. segment_text is missing for many rows.
3. audio field is missing for many rows.
4. suspect rate is extremely high and unexplained.
```

## Next phase

Phase 2 should create run manifests and subset archives for Run 0, Run A, Run B, and Run C.

Recommended next script:

```text
scripts/vimedcss/02_create_vimedcss_run_manifests_and_archives.py
```
