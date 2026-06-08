# Day 2 Week 4 — Build ASR Preprocessing Variants

## Objective

Create versioned audio preprocessing variants for VietMed dev set.

## Variants

| Variant | Input rows | Output rows | Failures | Manifest |
|---|---:|---:|---:|---|
| p03_vad_pad_200ms | 600 | 600 | 0 | `data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_train_candidate_p03_vad_pad_200ms.jsonl` |

## Guardrails

- Raw audio was not modified.
- Test holdout was not used.
- Each variant has its own manifest.
- Each preprocessed file has checksum metadata.

## Next step

Run `audit_audio_quality.py` on each variant manifest in Day 3.
