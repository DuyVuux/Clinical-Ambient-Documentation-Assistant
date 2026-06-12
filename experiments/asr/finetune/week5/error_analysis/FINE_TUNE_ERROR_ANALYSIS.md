# Day 5 Week 5 — Fine-tune Clinical Error Analysis

## Objective

Compare PhoWhisper fine-tuning runs using WER/CER and clinical ASR error metrics.

## Full dev comparison

| Model / Run | Role | WER | CER | Missing negation | Missing symptom | Medication error | Dose/unit error | Numeric error |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ChunkFormer reference | primary_reference | 12.90% | 12.06% | None | None | None | None | None |
| PhoWhisper-medium baseline | backup_baseline | 24.64% | 19.80% | None | None | None | None | None |
| Run 01 conservative | candidate | 16.57% | 14.64% | None | None | None | None | None |
| Run 02 low-lr | candidate | 18.22% | 16.24% | None | None | None | None | None |

## Edge-risk subset comparison

| Model / Run | Edge WER | Edge CER | Edge missing negation | Edge missing symptom |
|---|---:|---:|---:|---:|
| PhoWhisper-medium baseline | 22.60% | 17.39% | None | None |
| Run 01 conservative | 15.74% | 13.96% | None | None |
| Run 02 low-lr | 17.45% | 15.54% | None | None |

## Decision rules

- Accept a fine-tuned backup only if WER < 20% and clinical errors do not increase.
- Reject a checkpoint if WER improves but missing negation/symptom/dose errors increase.
- If WER remains > 22%, Week 6 should focus on more data rather than more hyperparameter tuning.
