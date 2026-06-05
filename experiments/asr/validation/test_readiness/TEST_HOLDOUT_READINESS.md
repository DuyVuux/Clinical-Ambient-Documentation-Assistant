# Test Holdout Readiness — Day 6

## Candidate selected for Day 7 test

Primary:
- khanhld/chunkformer-ctc-large-vie

Backup:
- vinai/PhoWhisper-medium

Lightweight backup:
- vinai/PhoWhisper-base

## Why ChunkFormer is selected

- Best dev WER: 12.90%
- Target: <20%
- Reproducibility: PASS
- Leakage check: PASS
- Medical error analysis: PASS
- Manual audit: PASS

## Why PhoWhisper-medium is not selected as primary yet

- Normalized WER = 21.51%, still above <20 target.
- However, it is close to target and faster than ChunkFormer.
- It should be considered for fine-tuning in Week 4.

## Why PhoWhisper-base is retained

- Normalized WER = 24.11%, above target.
- Runtime is fastest among kept models.
- It may be useful as lightweight baseline/fine-tune candidate.

## Day 7 allowed action

- [ ] Run ChunkFormer once on test_holdout
- [ ] Compute strict WER / normalized WER
- [ ] Compute strict CER / normalized CER
- [ ] Run medical error analysis on test result
- [ ] Do not choose model by test result among many models

## Day 7 conditional action

Only run PhoWhisper-medium on test if:
- ChunkFormer fails medically,
- ChunkFormer fails deployment/license constraints,
- or mentor explicitly asks for Whisper-family comparison.

Do not run PhoWhisper-base on test unless specifically needed for lightweight deployment comparison.

## Not allowed

- [x] Do not run all models on test and choose the best.
- [x] Do not tune normalization after seeing test result.
- [x] Do not train on test.
- [x] Do not manually fix test predictions.