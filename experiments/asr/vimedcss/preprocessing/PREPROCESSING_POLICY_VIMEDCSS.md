# ViMedCSS Preprocessing Policy

## Goal

Prepare ViMedCSS subsets for PhoWhisper progressive fine-tuning without corrupting medical/code-switching content.

## Allowed

- Decode audio to 16kHz mono when materializing subsets.
- Validate duration.
- Exclude broken/empty samples.
- Keep official splits.
- Preserve English medical terms and code-switching terms.
- Write stable JSONL manifests.
- Keep original `segment_text` as reference transcript.

## Not allowed

- Do not train on validation/test/hard.
- Do not normalize away English medical terms.
- Do not use aggressive text normalization before evaluation.
- Do not apply VAD/cropping blindly if audio is already segmented.
- Do not choose checkpoint from test/hard.
- Do not self-split ViMedCSS 60/40.

## Initial suspect filters

```text
duration_seconds < 1.0
duration_seconds > 25.0
num_words <= 1
text_len <= 3
audio missing/unreadable
segment_text missing/empty
```

## Code-switching preservation

Fields such as `cs_terms_list` and `cs_terms_count` must be preserved in run manifests when available.

## Official split usage

| Split | Usage |
|---|---|
| train | training only |
| validation | model selection |
| test | final/reporting only |
| hard | stress/reporting only |
