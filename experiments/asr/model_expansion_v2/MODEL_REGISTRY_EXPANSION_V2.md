# Model Registry Expansion v2

## Purpose

Extend ASR benchmark with additional Vietnamese ASR models before further fine-tuning.

## Fixed evaluation data

| Split | Path | Samples | Purpose |
|---|---|---:|---|
| dev | data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl | 200 | model comparison |
| test_holdout | data/data_lake/evaluation/asr_eval_v0_1/vietmed_test_holdout_v0_1.jsonl | 200 | final confirmation only |

## Models

| Model ID | Source | Architecture | License | Intended benchmark role | Status |
|---|---|---|---|---|---|
| dangvansam/viet-asr | GitHub | NeMo/QuartzNet CTC | Apache-2.0 | lightweight legacy baseline | planned |
| nguyenvulebinh/ViStreamASR | GitHub/PyPI | streaming ASR / U2-style | MIT | real-time streaming candidate | planned |
| hynt/Zipformer-30M-RNNT-6000h | Hugging Face | ZipFormer RNNT ONNX | CC-BY-NC-ND-4.0 | fast CPU RNNT candidate | planned |

## Guardrails

- Do not use test_holdout for model selection.
- All models use the same WER protocol.
- All predictions must use the shared JSONL format.
- Runtime must be measured.
- Medical error analysis must be run for every model.