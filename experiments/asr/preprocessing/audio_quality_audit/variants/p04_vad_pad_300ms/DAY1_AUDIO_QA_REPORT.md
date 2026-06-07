# Day 1 Week 4 — Audio Quality Audit Report

## Input

- Manifest: `data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p04_vad_pad_300ms.jsonl`
- Full JSON report: `experiments/asr/preprocessing/audio_quality_audit/variants/p04_vad_pad_300ms/audio_quality_report.json`
- Edge-loss risk samples: `experiments/asr/preprocessing/audio_quality_audit/variants/p04_vad_pad_300ms/edge_loss_risk_samples.jsonl`

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
| long_leading_silence | 0 | Leading silence > 1000 ms |
| long_trailing_silence | 0 | Trailing silence > 1000 ms |
| edge_loss_risk | 39 | First/last 300ms much weaker than middle |

## Numeric summary

| Metric | Min | P10 | Median | Mean | P90 | Max |
|---|---:|---:|---:|---:|---:|---:|
| duration_seconds | 2.0 | 5.0 | 6.0 | 6.0023 | 7.0 | 8.0 |
| rms_db | -25.7133 | -24.4601 | -23.5104 | -23.4089 | -22.1308 | -19.6592 |
| peak_db | -9.437 | -7.1002 | -4.6405 | -4.5651 | -2.0275 | -1.9988 |
| clipping_ratio | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| leading_silence_ms | 0.0 | 0.0 | 0.0 | 34.8 | 140.0 | 320.0 |
| trailing_silence_ms | 0.0 | 0.0 | 0.0 | 35.8 | 104.0 | 460.0 |
| first_300ms_db | -57.4425 | -33.4128 | -24.6081 | -26.2312 | -20.012 | -16.8115 |
| last_300ms_db | -62.0708 | -32.9173 | -24.474 | -26.1481 | -18.5714 | -14.5985 |
| middle_db | -25.7194 | -24.5624 | -23.5767 | -23.4472 | -22.0326 | -19.4182 |
| min_edge_to_middle_ratio | 0.0124 | 0.1275 | 0.6935 | 0.667 | 1.1338 | 1.9819 |

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
