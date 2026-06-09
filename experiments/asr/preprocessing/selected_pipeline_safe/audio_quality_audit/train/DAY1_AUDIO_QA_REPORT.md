# Day 1 Week 4 — Audio Quality Audit Report

## Input

- Manifest: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl`
- Full JSON report: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/experiments/asr/preprocessing/selected_pipeline_safe/audio_quality_audit/train/audio_quality_report.json`
- Edge-loss risk samples: `/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant/experiments/asr/preprocessing/selected_pipeline_safe/audio_quality_audit/train/edge_loss_risk_samples.jsonl`

## Summary

- Total samples: **600**

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
| long_trailing_silence | 3 | Trailing silence > 1000 ms |
| edge_loss_risk | 95 | First/last 300ms much weaker than middle |

## Numeric summary

| Metric | Min | P10 | Median | Mean | P90 | Max |
|---|---:|---:|---:|---:|---:|---:|
| duration_seconds | 1.0 | 5.0 | 6.0 | 6.0746 | 7.0 | 13.0 |
| rms_db | -27.1889 | -24.562 | -23.5898 | -23.4612 | -22.1894 | -18.8382 |
| peak_db | -9.9342 | -7.0529 | -4.7282 | -4.7489 | -2.1135 | -1.9304 |
| clipping_ratio | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| leading_silence_ms | 0.0 | 0.0 | 0.0 | 28.7667 | 142.0 | 1620.0 |
| trailing_silence_ms | 0.0 | 0.0 | 0.0 | 55.5333 | 220.0 | 4640.0 |
| first_300ms_db | -54.2085 | -29.1327 | -23.6945 | -24.1374 | -20.1393 | -16.2165 |
| last_300ms_db | -120.0 | -38.26 | -25.0393 | -27.4704 | -19.5008 | -12.9499 |
| middle_db | -28.2554 | -24.5974 | -23.6156 | -23.4977 | -22.1889 | -19.0843 |
| min_edge_to_middle_ratio | 0.0 | 0.1661 | 0.6777 | 0.6858 | 1.1352 | 2.4458 |

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
