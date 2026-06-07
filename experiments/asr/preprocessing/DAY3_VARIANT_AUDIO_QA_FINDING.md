# Day 3 Week 4 — Variant Audio QA Finding

## Main finding

The initial VAD-padding variants did not clearly solve edge-loss under the current file-edge audio audit.

| Variant | edge_loss_risk | Decision |
|---|---:|---|
| original | 29 | baseline |
| p03_vad_pad_200ms | 27 | weak candidate |
| p04_vad_pad_300ms | 39 | drop under file-edge audit |
| p05_vad_pad_500ms | 35 | drop under file-edge audit |

## Interpretation

The current file-edge metric may be biased against padded audio because it measures the first/last 300ms of the whole file. If a preprocessing variant intentionally adds silence padding, the metric may treat that silence as weak edge energy.

## Updated decision

Before ASR A/B testing, we will:
1. Add padding-only variants p10/p11/p12.
2. Add padding-aware speech-edge audit.
3. Select variants for Day 4 using both file-edge and speech-edge metrics.

## Guardrail

No test_holdout is used.
No fine-tuning is performed.