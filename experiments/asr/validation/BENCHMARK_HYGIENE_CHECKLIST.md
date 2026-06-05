# Benchmark Hygiene Checklist — Day 6

## Split integrity

- [x] train_candidate = 600
- [x] dev = 200
- [x] test_holdout = 200
- [x] train/dev/test sample_id không trùng
- [x] test_holdout chưa dùng để chọn model
- [x] dev chỉ dùng cho leaderboard/model selection

## Data integrity

- [x] Tất cả clean_audio_path tồn tại
- [x] Transcript text không rỗng
- [x] Audio đã chuẩn hóa 16kHz mono wav
- [x] Có checksum cho audio
- [x] Không sửa transcript sau khi thấy prediction

## Metric integrity

- [x] Cùng WER script cho mọi model
- [x] Cùng text normalization cho mọi model
- [x] Báo cáo cả Strict WER và Normalized WER
- [x] Không so dev WER với test WER như cùng một loại metric

## Model integrity

- [x] ChunkFormer chạy bằng script CTC/HF ASR phù hợp
- [x] Không truyền Whisper generate_kwargs cho CTC model
- [x] Whisper/PhoWhisper chạy bằng script Whisper riêng
- [x] Log runtime được ghi lại

## Status

Overall status: PASS