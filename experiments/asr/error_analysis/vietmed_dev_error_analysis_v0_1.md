# VietMed Dev ASR Error Analysis v0.1

## Purpose

Analyze ASR errors that matter clinically, not only average WER.

## Dataset

| Field | Value |
|---|---:|
| Source | VietMed |
| Split | dev |
| Samples | 200 |

## Models analyzed

| Model | Prediction file |
|---|---|
| vinai/PhoWhisper-base | experiments/asr/baseline/predictions/dev/phowhisper_base_dev_predictions.jsonl |
| vinai/PhoWhisper-medium | experiments/asr/baseline/predictions/dev/phowhisper_medium_dev_predictions.jsonl |
| openai/whisper-small | experiments/asr/baseline/predictions/dev/whisper_small_dev_predictions.jsonl |

## Error summary

| Model | Missed Negation | Hallucinated Negation | Missed Medical Term | Hallucinated Medical Term |
|---|---:|---:|---:|---:|
| vinai/PhoWhisper-base | 6 | 3 | 13 | 8 |
| vinai/PhoWhisper-medium | 6 | 6 | 8 | 13 |
| openai/whisper-small | 20 | 4 | 55 | 1 |

## Important examples

### Example 1 — Missed Negation

Reference (openai/whisper-small):
> xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không

Prediction:
> đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó

Risk:
- Nếu mất "không", nghĩa lâm sàng bị đảo.

### Example 2 — Hallucinated Negation (Tự thêm)

Reference (vinai/PhoWhisper-medium):
> với cột sống ngực đâu bởi vì là sao bây giờ nó đã có những cái câu chuyện là tê liên quan đến cả tay nữa thậm chí là cả

Prediction:
> không phải là cổ sống lưng với cổ sống ngực đâu bởi vì là sao bây giờ nó đã có những cái câu chuyện là tê liên quan đến cả tay nữa thậm chí là cả hai

Risk:
- Tự thêm từ phủ định ("không") có thể làm thay đổi hoàn toàn tình trạng bệnh lý và chẩn đoán.

## Decision

The selected ASR candidate should not be based only on WER. It must also reduce:
- negation deletion (bỏ sót từ phủ định)
- negation hallucination (ảo giác từ phủ định)
- missing medical terms (bỏ sót từ khóa y khoa)
- hallucinated medical terms (ảo giác từ khóa y khoa)