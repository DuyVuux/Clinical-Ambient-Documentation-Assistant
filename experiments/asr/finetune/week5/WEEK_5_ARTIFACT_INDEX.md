# Week 5 Report — PhoWhisper Fine-tuning for Backup ASR

## 1. Objective

Fine-tune `vinai/PhoWhisper-medium` as a backup ASR model for Vietnamese clinical speech.

## 2. Frozen preprocessing

`p03_safe_hybrid_v0_1`

This preprocessing was selected after Week 4 because pure `p03_vad_pad_200ms` improved edge-risk WER but manual inspection found a small number of VAD-risk samples. The final safe hybrid keeps p03 by default and falls back to original audio for risky samples.

## 3. Data

| Split | Samples | Manifest | Usage |
|---|---:|---|---|
| train | 600 | `vietmed_train_preprocessed_selected_safe_v0_1.jsonl` | training |
| dev | 200 | `vietmed_dev_preprocessed_selected_safe_v0_1.jsonl` | validation |
| test_holdout | 200 | not used | forbidden in Week 5 |

## 4. Baseline safe dev

| Model | Role | WER | CER | Clinical errors |
|---|---|---:|---:|---|
| ChunkFormer | primary reference | TBD | TBD | TBD |
| PhoWhisper-medium | backup baseline | TBD | TBD | TBD |

## 5. Fine-tune runs

| Run | Config | WER | CER | Decision |
|---|---|---:|---:|---|
| run 01 | conservative, lr=1e-5, 3 epochs | TBD | TBD | TBD |
| run 02 | low-lr, lr=5e-6, 5 epochs | TBD | TBD | TBD |

## 6. Clinical error analysis

| Run | Missing negation | Missing symptom | Medication error | Dose/unit error | Numeric error |
|---|---:|---:|---:|---:|---:|
| baseline | TBD | TBD | TBD | TBD | TBD |
| run 01 | TBD | TBD | TBD | TBD | TBD |
| run 02 | TBD | TBD | TBD | TBD | TBD |

## 7. Backup model decision

See:

`experiments/asr/finetune/week5/decision/PHOWHISPER_BACKUP_MODEL_DECISION.md`

Final status:

`TBD`

## 8. Week 6 next step

TBD.

## 9. Guardrails

- test_holdout was not used.
- dev was not used for training.
- preprocessing was not changed.
- transcripts were not manually edited after seeing model outputs.