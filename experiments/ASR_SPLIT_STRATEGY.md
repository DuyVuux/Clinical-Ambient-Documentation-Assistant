# ASR Split Strategy v0.1

## Target

Reduce WER from current Whisper-small VietMed baseline ~31% to <20%.

## Main target dataset

VietMed medical speech.

## Evaluation rule

- Holdout set must never be used for training.
- Report both strict WER and normalized WER.
- If possible, also report Medical Term Error Rate.

## Splits

### VietMed
- smoke_test: 50 samples
- dev_candidate: 100–200 samples
- test_holdout: 100–200 samples
- train_candidate: remaining labeled samples after governance check

### Common Voice vi
- smoke_test: 100 samples
- train_candidate: validated/train subset only
- role: general Vietnamese robustness

### FOSD
- smoke_test: 50 samples
- train_candidate: optional
- role: general Vietnamese ASR/chunk robustness

## Governance

- Public data stays in Bronze/Silver.
- Public data is not Gold.
- No source with unclear license is used for training.