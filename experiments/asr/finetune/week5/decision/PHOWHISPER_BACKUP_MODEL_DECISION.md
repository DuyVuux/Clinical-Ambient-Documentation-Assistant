# Day 6 Week 5 — PhoWhisper Backup Model Decision

## Objective

Decide whether fine-tuned PhoWhisper-medium can be accepted as backup ASR model v0.1.

## Acceptance criteria

- Dev WER < 20%
- Clinical errors do not increase compared with PhoWhisper-medium baseline
- test_holdout is not used

## Results

| Run | Role | WER | CER | Missing negation | Missing symptom | Medication error | Dose/unit error | Numeric error |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ChunkFormer reference | primary_reference | 12.90% | 12.06% | None | None | None | None | None |
| PhoWhisper-medium baseline | backup_baseline | 24.64% | 19.80% | None | None | None | None | None |
| Run 01 conservative | candidate | 16.57% | 14.64% | None | None | None | None | None |
| Run 02 low-lr | candidate | 18.22% | 16.24% | None | None | None | None | None |

## Decision

Status: **ACCEPT_BACKUP_V0_1**

Selected run: `Run 01 conservative`

Reason: WER < 20% and clinical errors did not increase.

## Next action

- Freeze the selected fine-tuned backup model.
- Prepare final evaluation plan.
- Do not run test_holdout until final model selection protocol is frozen.
