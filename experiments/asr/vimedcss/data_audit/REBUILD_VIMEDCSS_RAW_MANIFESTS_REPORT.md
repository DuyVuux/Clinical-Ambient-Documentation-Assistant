# ViMedCSS Raw Manifest Rebuild Report

## Objective

Rebuild raw manifests directly from HuggingFace `tensorxt/ViMedCSS` because previous local raw manifests were incomplete or dummy.

## Summary

| Split | Rows | Missing audio | Missing segment_text | Missing duration | Audio col | Text col | Output |
|---|---:|---:|---:|---:|---|---|---|
| train | 11832 | 0 | 0 | 0 | `audio` | `segment_text` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_train_raw.jsonl` |
| validation | 1714 | 0 | 0 | 0 | `audio` | `segment_text` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_validation_raw.jsonl` |
| test | 1614 | 0 | 0 | 0 | `audio` | `segment_text` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_test_raw.jsonl` |
| hard | 658 | 0 | 0 | 0 | `audio` | `segment_text` | `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/vimedcss/manifests/raw/vimedcss_hard_raw.jsonl` |

## Decision

Raw manifests are usable for Phase 1 sample-based audit.
