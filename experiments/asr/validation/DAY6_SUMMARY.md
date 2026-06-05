# Day 6 Summary — ASR Validation

## 1. Completed checks

| Work item | Status | Result |
|---|---|---|
| Split leakage check | PASS | No overlap between train/dev/test |
| ChunkFormer dev rerun | PASS | WER 12.9007%, CER 12.0328% |
| Medical error analysis | PASS | 3 models compared, clinical risks evaluated |
| Manual audit | PASS | 30 samples, 3 models, clinical errors audited |
| Test readiness | PASS | ChunkFormer confirmed for test_holdout |

## 2. Reproducibility result

ChunkFormer rerun on 200 dev samples:

| Metric | Value |
|---|---:|
| Strict WER | 12.9007% |
| Normalized WER | 12.9007% |
| Strict CER | 12.0328% |
| Normalized CER | 12.0328% |

This matches the Day 5 leaderboard.

## 3. Model roles

| Model | Role |
|---|---|
| khanhld/chunkformer-ctc-large-vie | primary model for test_holdout |
| vinai/PhoWhisper-medium | backup and Week 4 fine-tune candidate |
| vinai/PhoWhisper-base | lightweight backup and optional fine-tune candidate |
| openai/whisper-small | dropped |

## 4. Day 7 plan

Medical error analysis and manual audit have **PASSED**. All readiness checks are complete. The confirmed plan for Day 7 is:
- [ ] Run ChunkFormer once on `test_holdout`
- [ ] Compute strict and normalized WER/CER
- [ ] Run medical error analysis on test result
- [ ] Finalize Week 3 report and Model Selection Decision