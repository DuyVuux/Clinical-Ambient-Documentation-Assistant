# ASR Adapter Interface

Every ASR adapter must accept:

```bash
--manifest <path>
--output <path>
--max_samples <int optional>
```

Every adapter must output JSONL:

```json
{
  "sample_id": "...",
  "model_name": "...",
  "model_family": "...", 
  "clean_audio_path": "...",
  "reference_text": "...",
  "prediction_text": "...",
  "split_role": "dev_candidate",
  "source_name": "VietMed",
  "version": "v0.1.0"
}
```

*Lưu ý:* Các chỉ số hiệu năng như `runtime_seconds`, `audio_duration_seconds`, `rtf` (Real-Time Factor) có thể được track riêng lẻ hoặc ghi đè tùy vào rule của pipeline đánh giá, không bắt buộc phải nằm trong file prediction JSONL trừ khi có thay đổi convention mới.

If a model fails on a sample:

```json
{
  "prediction_text": "",
  "error": "exception message",
  "failed": true
}
```