# Day 1 Week 4 — Audio Quality Audit Report

## Input

- Manifest: `data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p03_vad_pad_200ms.jsonl`
- Full JSON report: `experiments/asr/preprocessing/audio_quality_audit/variants/p03_vad_pad_200ms/audio_quality_report.json`
- Edge-loss risk samples: `experiments/asr/preprocessing/audio_quality_audit/variants/p03_vad_pad_200ms/edge_loss_risk_samples.jsonl`

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
| edge_loss_risk | 27 | First/last 300ms much weaker than middle |

## Numeric summary

| Metric | Min | P10 | Median | Mean | P90 | Max |
|---|---:|---:|---:|---:|---:|---:|
| duration_seconds | 2.0 | 5.0 | 6.0 | 5.9826 | 7.0 | 8.0 |
| rms_db | -25.6381 | -24.4549 | -23.5104 | -23.3964 | -22.1174 | -19.6592 |
| peak_db | -9.437 | -7.1002 | -4.6405 | -4.5651 | -2.0275 | -1.9995 |
| clipping_ratio | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| leading_silence_ms | 0.0 | 0.0 | 0.0 | 29.4 | 142.0 | 220.0 |
| trailing_silence_ms | 0.0 | 0.0 | 0.0 | 37.3 | 142.0 | 380.0 |
| first_300ms_db | -39.0608 | -29.5045 | -24.0956 | -24.4264 | -19.9689 | -16.8115 |
| last_300ms_db | -58.2152 | -35.5665 | -24.5338 | -26.4539 | -18.5714 | -14.5985 |
| middle_db | -26.2696 | -24.5624 | -23.5638 | -23.4523 | -22.0326 | -19.3779 |
| min_edge_to_middle_ratio | 0.0199 | 0.2237 | 0.7169 | 0.7069 | 1.1394 | 1.9819 |

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
