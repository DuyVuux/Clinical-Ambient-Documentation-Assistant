# ASR Target

## Business / mentor target

Current baseline:
- Model: Whisper small fine-tuned/trained on VietMed
- Reported WER: ~31%

Target:
- Achieve WER < 20% using any model.

## Our assumption

The primary benchmark is a frozen VietMed medical speech holdout set.

## Reporting rule

We will report:
1. Strict WER
2. Normalized WER
3. Medical Term Error Rate if term labels/dictionary are available

## Candidate models

1. PhoWhisper-base
2. PhoWhisper-large
3. ChunkFormer-large-vie
4. Whisper-medium / Whisper-large-v3
5. Fine-tuned PhoWhisper-small/base on VietMed train

## Safety note

WER alone is not enough for clinical ASR. We also track:
- medical term errors
- number errors
- negation errors
- medication/dose errors