# ASR Preprocessing Decision v0.1

## Final selected preprocessing

`p03_safe_hybrid_v0_1`

## Meaning

- Default preprocessing: `p03_vad_pad_200ms`
- Risky VAD-truncated samples: fallback to original clean audio
- Raw audio remains unchanged
- Test holdout was not used

## Why not pure p03?

Pure `p03_vad_pad_200ms` improved edge-risk subset WER and preserved full-dev WER, but manual inspection found a small number of samples where VAD might cut beginning/end speech or important words.

## Manual inspection outcome

| Decision | Count |
|---|---:|
| keep_p03 | 3 |
| fallback_original | 4 |
| needs_recheck | 0 |

## Final selected manifests

| Split | Manifest | Rows | Fallback Applied |
|---|---|---|---|
| train | `data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl` | 600 | 4 |
| dev | `data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_safe_v0_1.jsonl` | 200 | 0 |

**Fallback samples (Train)**: `public_vietmed_0152`, `public_vietmed_0176`, `public_vietmed_0894`, `public_vietmed_0972`

## Final Audio Quality Audits (Padding-Aware)

| Split | Samples | Speech Edge Loss Risk Count | Speech Edge Loss Risk Rate | Speech Min Edge to Middle Ratio Mean |
|-------|---------|-----------------------------|----------------------------|--------------------------------------|
| train | 600     | 30                          | 5.0%                       | 0.7910                               |
| dev   | 200     | 11                          | 5.5%                       | 0.7906                               |

## Guardrails

- No test_holdout was used
- No fine-tuning was performed
- WER protocol was not changed
- Manual fallback was applied only to risky samples