# Week 5 Fine-tune Readiness

## Data status

| Split | Samples | Manifest | Preprocessing |
|---|---:|---|---|
| train | 600 | `vietmed_train_preprocessed_selected_safe_v0_1.jsonl` | p03_safe_hybrid_v0_1 |
| dev | 200 | `vietmed_dev_preprocessed_selected_safe_v0_1.jsonl` | p03_safe_hybrid_v0_1 |
| test_holdout | 200 | untouched | not used |

## Current primary inference baseline

`khanhld/chunkformer-ctc-large-vie`

## Fine-tuning candidates

1. `vinai/PhoWhisper-medium`
2. `vinai/PhoWhisper-base`
3. fallback: `openai/whisper-small`

## Week 5 goal

Reduce clinical ASR risk and improve backup/fine-tuned model, especially:
- missing negation
- missing symptom
- medication/dose/unit error
- edge-risk samples

## Guardrails

- Do not train on dev
- Do not train on test_holdout
- Do not select checkpoint by test_holdout
- Keep WER protocol unchanged