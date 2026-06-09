# Day 2 Week 5 — PhoWhisper Fine-tune Data Preparation: train

## Objective

Prepare a PhoWhisper-ready JSONL manifest from the frozen selected safe ASR manifest.

## Input / Output

- Input manifest: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl`
- Output manifest: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/experiments/asr/finetune/week5/data/train_manifest_for_phowhisper.jsonl`
- Split: `train`
- Expected preprocessing: `p03_safe_hybrid_v0_1`

## Summary

| Metric | Value |
|---|---:|
| Output rows | 600 |
| Skipped rows | 0 |
| Manual fallback applied | 4 |

## Preprocessing versions

| Version | Count |
|---|---:|
| `p03_safe_hybrid_v0_1` | 600 |

## Duration summary

| Metric | Seconds |
|---|---:|
| min | 1.0 |
| p10 | 5.0 |
| median | 6.0 |
| mean | 6.0746 |
| p90 | 7.0 |
| max | 13.0 |

## Transcript word count

| Metric | Words |
|---|---:|
| min | 1 |
| median | 27.0 |
| mean | 25.45 |
| max | 39 |

## Skipped reasons

No skipped rows.

## Guardrails

- Transcript text was minimally whitespace-cleaned only.
- No semantic transcript editing was performed.
- test_holdout was not used.
- The output uses absolute local audio paths for HuggingFace loading.
