# ASR Model Validation Plan

## Context

Target: WER < 20%

Day 5 dev leaderboard:

| Rank | Model | Strict WER | Normalized WER | Strict CER | Normalized CER | Decision |
|---:|---|---:|---:|---:|---:|---|
| 1 | khanhld/chunkformer-ctc-large-vie | 12.90% | 12.90% | 12.03% | 12.03% | keep |
| 2 | vinai/PhoWhisper-medium | 24.64% | 21.51% | 19.83% | 19.54% | keep |
| 3 | vinai/PhoWhisper-base | 26.75% | 24.11% | 21.05% | 20.73% | keep |
| 4 | openai/whisper-small | 58.58% | 53.23% | 46.69% | 44.85% | drop |

## Day 6 objective

Validate whether ChunkFormer result is reliable enough to run on test_holdout on Day 7.

## Day 6 tasks

1. Freeze Day 5 artifacts.
2. Check train/dev/test leakage.
3. Verify WER computation and text normalization.
4. Run medical ASR error analysis.
5. Manual audit of high-risk samples.
6. Prepare Day 7 test-holdout run.
7. Decide whether fine-tuning is still needed.