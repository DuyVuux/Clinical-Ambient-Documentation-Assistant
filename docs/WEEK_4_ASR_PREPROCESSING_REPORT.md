# Week 4 Report — ASR Data Preprocessing

## 1. Objective

Week 4 focused on audio preprocessing before fine-tuning.

## 2. Day 1 — Audio QA

Train/dev showed significant edge-loss risk but no global loudness or clipping problem.

| Split | Samples | edge_loss_risk | too_quiet | clipping |
|---|---:|---:|---:|---:|
| train | 600 | 110 | 0 | 0 |
| dev | 200 | 29 | 0 | 0 |

## 3. Day 2 — Preprocessing variants

Variants tested:
- p03_vad_pad_200ms
- p04_vad_pad_300ms
- p05_vad_pad_500ms
- p10_edge_pad_200ms
- p11_edge_pad_300ms
- p12_edge_pad_500ms

## 4. Day 3 — Audio QA for variants

VAD/padding variants were audited using both file-edge and padding-aware speech-edge metrics.

## 5. Day 4 — ASR A/B test

Compared:
- original
- p10_edge_pad_200ms
- p03_vad_pad_200ms

## 6. Day 5 — Clinical error analysis

Result:
- p10 worsened full-dev WER and edge-risk WER
- p03 preserved full-dev WER and improved edge-risk WER
- p03 did not increase clinical errors

## 7. Day 6 — Manual inspection and safe hybrid

Manual inspection found a small number of VAD-risk samples.
Fallback to original audio was applied to 4 train samples, leaving dev unmodified.

Final decision:
`p03_safe_hybrid_v0_1`

**Final Audio Quality (Padding-Aware)**:
- Train (600 samples): 30 speech edge loss risk (5.0%)
- Dev (200 samples): 11 speech edge loss risk (5.5%)

## 8. Final deliverables

- selected safe train manifest (`vietmed_train_preprocessed_selected_safe_v0_1.jsonl`, 600 samples)
- selected safe dev manifest (`vietmed_dev_preprocessed_selected_safe_v0_1.jsonl`, 200 samples)
- preprocessing decision
- manual inspection result
- Week 5 fine-tune readiness

## 9. Next step

Proceed to Week 5 fine-tuning/evaluation using selected safe manifests.