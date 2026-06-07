# Day 1 Week 4 — Audio Quality Audit Report

## Input

- Manifest: `/content/Clinical-Ambient-Documentation-Assistant/data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1_colab.jsonl`
- Full JSON report: `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/preprocessing/audio_quality_audit/dev/audio_quality_report.json`
- Edge-loss risk samples: `/content/Clinical-Ambient-Documentation-Assistant/experiments/asr/preprocessing/audio_quality_audit/dev/edge_loss_risk_samples.jsonl`

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
| long_leading_silence | 1 | Leading silence > 1000 ms |
| long_trailing_silence | 1 | Trailing silence > 1000 ms |
| edge_loss_risk | 29 | First/last 300ms much weaker than middle |

## Numeric summary

| Metric | Min | P10 | Median | Mean | P90 | Max |
|---|---:|---:|---:|---:|---:|---:|
| duration_seconds | 2.0 | 5.0 | 6.0 | 6.055 | 7.0 | 8.0 |
| rms_db | -25.8437 | -24.4872 | -23.5146 | -23.4399 | -22.1308 | -19.6592 |
| peak_db | -9.437 | -7.1002 | -4.6405 | -4.5651 | -2.0275 | -1.9988 |
| clipping_ratio | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| leading_silence_ms | 0.0 | 0.0 | 0.0 | 39.2 | 100.0 | 1200.0 |
| trailing_silence_ms | 0.0 | 0.0 | 0.0 | 28.7 | 100.0 | 1100.0 |
| first_300ms_db | -120.0 | -32.7584 | -24.4763 | -26.3862 | -20.012 | -16.8115 |
| last_300ms_db | -70.7543 | -32.008 | -24.3013 | -25.3452 | -18.5648 | -14.5985 |
| middle_db | -26.1301 | -24.5932 | -23.6086 | -23.4906 | -22.0911 | -19.8363 |
| min_edge_to_middle_ratio | 0.0 | 0.2228 | 0.7114 | 0.6939 | 1.1338 | 1.9819 |

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
