# Day 1 Week 4 — Audio Quality Audit Report

## Input

- Manifest: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p12_edge_pad_500ms.jsonl`
- Full JSON report: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/experiments/asr/preprocessing/audio_quality_audit/variants/p12_edge_pad_500ms/audio_quality_report.json`
- Edge-loss risk samples: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/experiments/asr/preprocessing/audio_quality_audit/variants/p12_edge_pad_500ms/edge_loss_risk_samples.jsonl`

## Summary

- Total samples: **200**

## Warning counts

| Warning | Count | Meaning |
|---|---:|---|
| non_16khz | 0 | Audio is not 16kHz |
| non_mono | 0 | Audio is not mono |
| too_short | 0 | Duration < 1 second |
| long_audio_may_need_chunking | 0 | Duration > 30 seconds |
| too_quiet | 0 | RMS < -35 dB |
| too_loud | 0 | RMS > -10 dB |
| peak_near_0db_clipping_risk | 0 | Peak near 0 dB |
| clipping_detected | 0 | Many samples close to +/-1 |
| long_leading_silence | 4 | Leading silence > 1000 ms |
| long_trailing_silence | 1 | Trailing silence > 1000 ms |
| edge_loss_risk | 200 | First/last 300ms much weaker than middle |

## Numeric summary

| Metric | Min | P10 | Median | Mean | P90 | Max |
|---|---:|---:|---:|---:|---:|---:|
| duration_seconds | 3.0 | 6.0 | 7.0 | 7.055 | 8.0 | 9.0 |
| rms_db | -26.5132 | -25.1838 | -24.2635 | -24.1184 | -22.7633 | -20.451 |
| peak_db | -9.437 | -7.1002 | -4.6405 | -4.5651 | -2.0275 | -1.9988 |
| clipping_ratio | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| leading_silence_ms | 500.0 | 500.0 | 500.0 | 539.2 | 600.0 | 1700.0 |
| trailing_silence_ms | 500.0 | 500.0 | 500.0 | 528.7 | 600.0 | 1600.0 |
| first_300ms_db | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 |
| last_300ms_db | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 |
| middle_db | -26.124 | -24.7472 | -23.8483 | -23.7245 | -22.3792 | -19.9934 |
| min_edge_to_middle_ratio | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Interpretation

- `edge_loss_risk` suggests the beginning or ending of the utterance is much weaker than the middle.
- `long_leading_silence` and `long_trailing_silence` suggest VAD/silence trimming may help.
- `too_quiet` suggests loudness normalization or light compression may help.
- `clipping_detected` suggests normalization/compression must be careful because the signal may already be distorted.

## Recommended next step

Create preprocessing variants and evaluate them on the dev set:

- `p00_format_only`
- `p01_loudnorm`
- `p02_compressor_loudnorm`
- `p03_vad_pad_200ms`
- `p04_vad_pad_300ms`
- `p05_vad_pad_500ms`
