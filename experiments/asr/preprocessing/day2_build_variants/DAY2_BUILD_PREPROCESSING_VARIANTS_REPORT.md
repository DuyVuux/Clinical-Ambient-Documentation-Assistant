# Day 2 Week 4 — Build ASR Preprocessing Variants

## Objective

Create versioned audio preprocessing variants for VietMed dev set.

## Variants

| Variant | Input rows | Output rows | Failures | Manifest |
|---|---:|---:|---:|---|
| p03_vad_pad_200ms | 200 | 200 | 0 | `data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p03_vad_pad_200ms.jsonl` |
| p04_vad_pad_300ms | 200 | 200 | 0 | `data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p04_vad_pad_300ms.jsonl` |
| p05_vad_pad_500ms | 200 | 200 | 0 | `data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p05_vad_pad_500ms.jsonl` |

## Guardrails

- Raw audio was not modified.
- Test holdout was not used.
- Each variant has its own manifest.
- Each preprocessed file has checksum metadata.

## Day 2 Notes

VAD-padding variants (`p03`, `p04`, `p05`) were prioritized because Day 1 showed:
- Dev edge_loss_risk: 29/200
- Train edge_loss_risk: 110/600
- too_quiet: 0
- clipping_detected: 0

Therefore, this run focuses on boundary context rather than global loudness normalization.

## Next step

Run `audit_audio_quality.py` on each variant manifest in Day 3.
