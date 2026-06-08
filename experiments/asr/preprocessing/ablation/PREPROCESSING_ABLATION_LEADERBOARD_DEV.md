# Day 4 Week 4 — ASR Preprocessing A/B Test

## Objective

Evaluate whether preprocessing variants reduce ASR errors on the VietMed dev set before applying any preprocessing to train data or fine-tuning.

## Dataset

| Field | Value |
|---|---:|
| Dataset | VietMed |
| Split | dev |
| Samples | 200 |
| Test holdout used? | No |
| Fine-tuning used? | No |

## Model

Primary A/B model:

```text
khanhld/chunkformer-ctc-large-vie
```

## Variants

| Variant | Description | Reason |
|---|---|---|
| original | Current clean audio baseline | Baseline comparison |
| p10_edge_pad_200ms | Add 200ms silence to both edges, no VAD cutting | Safe padding-only candidate |
| p03_vad_pad_200ms | VAD + 200ms padding | VAD-padding candidate |

## A/B Test Results

| Variant | Model | WER | CER | Medical errors | Edge-risk subset WER | Decision |
|---|---|---|---|---|---|---|
| original | ChunkFormer | 12.90% | 12.03% | 7 | 12.18% | baseline |
| p10_edge_pad_200ms | ChunkFormer | 14.49% | 13.56% | 6 | 13.49% | drop (worse WER) |
| p03_vad_pad_200ms | ChunkFormer | 12.90% | 12.06% | 7 | 11.81% | keep (improved edge WER) |

## Decision Rule

- If p10_edge_pad_200ms has WER equal to or lower than original and does not increase clinical errors, choose p10.
- If p03_vad_pad_200ms is clearly better than p10, keep p03 but manually inspect VAD boundary risk.
- If neither variant improves WER or clinical error, keep original preprocessing.
- Do not use test_holdout for this decision.