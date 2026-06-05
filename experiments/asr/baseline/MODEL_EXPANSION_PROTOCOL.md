# Day 5 Model Expansion Protocol

## Goal

Expand ASR benchmark with non-Whisper models:

1. khanhld/chunkformer-ctc-large-vie
2. XLSR-53-Viet from VietMed/MultiMed author if checkpoint is available

## Dataset

Use VietMed dev only:

- data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl
- N = 200

Do not use test_holdout today.

## Metrics

- strict WER
- normalized WER
- strict CER
- normalized CER
- medical ASR error analysis

## Important

ChunkFormer and XLSR/Wav2Vec2 are CTC models.
Do not use Whisper generate_kwargs such as:
- language = vi
- task = transcribe

## Decision rule

A model is selected for Week 4 only if:
- normalized WER is competitive
- negation / medication / dose errors are acceptable
- runtime is feasible on local machine
- license/governance status is acceptable for internal use