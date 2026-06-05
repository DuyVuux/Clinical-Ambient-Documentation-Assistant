# ASR Baseline Leaderboard – VietMed Dev v0.1

## Context

Current reported boss baseline:
- Whisper small trained/fine-tuned on VietMed
- WER ~31%
- Note: not directly comparable unless evaluated on the same dev/test split.

Our target:
- WER < 20%

## Dev set

| Field | Value |
|---|---:|
| Dataset | VietMed |
| Split | dev |
| Samples | 200 |
| Train allowed | false |

## Results

| Rank | Model | Strict WER | Normalized WER | Strict CER | Normalized CER | Runtime note | Decision |
|---:|---|---:|---:|---:|---:|---|---|
| 1 | khanhld/chunkformer-ctc-large-vie | 12.90% | 12.90% | 12.03% | 12.03% |  ~1.23s/sample | keep |
| 2 | vinai/PhoWhisper-medium | 24.64% | 21.51% | 19.83% | 19.54% | ~0.42s/sample (T4) | keep |
| 3 | vinai/PhoWhisper-base | 26.75% | 24.11% | 21.05% | 20.73% | ~0.14s/sample (T4) | keep |
| 4 | openai/whisper-small | 58.58% | 53.23% | 46.69% | 44.85% | ~0.26s/sample (T4) | drop |

## Rule

Only top 1-2 models on dev will be evaluated on test_holdout.