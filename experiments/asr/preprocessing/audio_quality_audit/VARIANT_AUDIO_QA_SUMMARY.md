# Day 3 Week 4 — Variant Audio QA Summary

## Objective

Audit VAD-padding preprocessing variants before ASR A/B testing.

## Padding-Aware Edge Loss Comparison

This table compares the old metric (file edge) against the new metric (speech edge).
`speech_edge_loss_risk` ignores inserted silence padding and measures energy at the actual speech start/end.

| Variant | N | file_edge_loss_risk | speech_edge_loss_risk | Difference |
|---|---:|---:|---:|---:|
| original | 200 | 29 | N/A | N/A |
| p03_vad_pad_200ms | 200 | 27 | N/A | N/A |
| p04_vad_pad_300ms | 200 | 39 | N/A | N/A |
| p05_vad_pad_500ms | 200 | 35 | N/A | N/A |

## Baseline

- Baseline original dev edge_loss_risk: **29**

## Warning comparison

| Variant | N | edge_loss_risk | long_leading_silence | long_trailing_silence | too_quiet | clipping | too_short | mean_duration | mean_edge_ratio | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| original | 200 | 29 | 1 | 1 | 0 | 0 | 0 | 6.055 | 0.6939 | neutral_no_edge_improvement |
| p03_vad_pad_200ms | 200 | 27 | 0 | 0 | 0 | 0 | 0 | 5.9826 | 0.7069 | keep_candidate_edge_improved |
| p04_vad_pad_300ms | 200 | 39 | 0 | 0 | 0 | 0 | 0 | 6.0023 | 0.667 | drop_edge_worse |
| p05_vad_pad_500ms | 200 | 35 | 0 | 0 | 0 | 0 | 0 | 6.0266 | 0.6807 | drop_edge_worse |

**Định nghĩa metric:**
- `file_edge_loss_risk` = metric cũ, đo đầu/cuối file
- `speech_edge_loss_risk` = metric mới, bỏ qua phần silence padding rồi mới đo đầu/cuối speech

**Ý tưởng metric mới:**

Với mỗi audio:

1. Tìm `speech_start` bằng ngưỡng năng lượng frame RMS.
2. Tìm `speech_end`.
3. Đo 300ms đầu tiên sau `speech_start`.
4. Đo 300ms cuối cùng trước `speech_end`.
5. So với middle speech region.

Như vậy nếu bạn thêm 300ms silence ở đầu, metric mới sẽ không phạt phần silence đó.

## Interpretation rules

- Keep a variant if `edge_loss_risk` decreases and no new serious warning appears.
- Drop a variant if it creates clipping, too-short audio, format regression, or worse edge-loss.
- If all VAD variants fail to reduce edge-loss, create padding-only variants next.

## Next step

Select top 1–3 variants for Day 4 ASR A/B test on VietMed dev.
