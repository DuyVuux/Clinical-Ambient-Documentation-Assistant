# Day 5 Report — ASR Model Expansion

## 1. Purpose

Expand ASR benchmark beyond Whisper/PhoWhisper by testing:

1. khanhld/chunkformer-ctc-large-vie

## 2. Dataset

| Field | Value |
|---|---:|
| Dataset | VietMed |
| Split | dev |
| Samples | 200 |
| Train allowed | false |
| Test holdout used? | no |

## 3. Why these models?

### ChunkFormer CTC Large Vie

Vietnamese ASR model trained/fine-tuned on large public Vietnamese speech data. Useful as a strong non-Whisper baseline.

## 4. Implementation notes

- ChunkFormer uses `chunkformer` package and `ChunkFormerModel`.
- It does not use Whisper `generate_kwargs`.

## 5. Results

| Model | Strict WER | Normalized WER | Strict CER | Normalized CER |
|---|---:|---:|---:|---:|
| khanhld/chunkformer-ctc-large-vie | 12.90% | 12.90% | 12.03% | 12.03% |

## 6. Medical error analysis

| Model | Negation missing | Symptom missing | Medication errors | Dose/unit errors | Numeric errors |
|---|---:|---:|---:|---:|---:|
| khanhld/chunkformer-ctc-large-vie | 7 | 7 | 0 | 1 | 0 |

## 7. Decision

- [x] Keep ChunkFormer as candidate
- [ ] Drop ChunkFormer
- [x] Proceed to fine-tune Week 4

## 8. Risks

- ChunkFormer license is non-commercial.
- CTC output style may differ from Whisper output style, so normalized WER is essential.
- WER alone is not enough; clinical-critical error groups must be checked.