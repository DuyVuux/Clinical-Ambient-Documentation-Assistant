# Hướng dẫn chạy ASR Benchmark End-to-End

Tài liệu này cung cấp các lệnh cần thiết để thực thi quy trình ASR benchmark cho dự án từ đầu đến cuối. Đảm bảo chạy các lệnh theo đúng trình tự từ bước 1 đến bước 10.

## 1. Setup environment

Thiết lập biến môi trường và kích hoạt môi trường ảo:

```bash
cd "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
export PROJECT_ROOT="$(pwd)"
export PYTHONPATH="$PROJECT_ROOT"

source .venv/bin/activate
```

## 2. Prepare data

Tiến hành tải hoặc import dữ liệu gốc (VietMed/FOSD) vào Data Lake (`bronze` layer):

```bash
python scripts/data_ingestion/ingest_asr_public_day1.py \
  --output_dir data/data_lake/bronze/public
```

## 3. Normalize audio

Chuẩn hóa âm thanh (chuyển đổi tần số lấy mẫu, định dạng mono) và lưu sang `silver` layer:

```bash
python scripts/data_ingestion/normalize_public_audio.py \
  --input_dir data/data_lake/bronze/public/vietmed \
  --output_dir data/data_lake/silver/public/vietmed \
  --manifest_output data/data_lake/silver/asr_manifests/vietmed_v0_1.jsonl
```

## 4. Create train/dev/test split

Tạo các tập dữ liệu huấn luyện, kiểm tra, và đánh giá:

```bash
python scripts/asr_eval/create_asr_splits.py \
  --manifest data/data_lake/silver/asr_manifests/vietmed_v0_1.jsonl \
  --output_dir data/data_lake/silver/asr_manifests/splits
```

## 5. Check leakage

Kiểm tra rò rỉ dữ liệu (data leakage) giữa các tập (để đảm bảo không có audio/transcript nào bị trùng lặp ở tập holdout):

```bash
python scripts/asr_eval/check_split_leakage.py \
  --train data/data_lake/silver/asr_manifests/splits/vietmed_train_candidate_v0_1.jsonl \
  --dev data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --test data/data_lake/evaluation/asr_eval_v0_1/vietmed_test_holdout_v0_1.jsonl
```

## 6. Run PhoWhisper

Đánh giá baseline với mô hình PhoWhisper (có thể thay đổi model thành `base` hoặc `medium`):

```bash
python scripts/asr_eval/run_whisper_transformers.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --model "vinai/PhoWhisper-base" \
  --output experiments/asr/baseline/predictions/dev/phowhisper_base_dev_predictions.jsonl
```

## 7. Run ChunkFormer

Đánh giá baseline với mô hình ChunkFormer (Primary baseline):

```bash
python scripts/asr_eval/run_chunkformer_ctc.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --model khanhld/chunkformer-ctc-large-vie \
  --output experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl
```

## 8. Compute WER/CER

Tính toán sai số từ (WER) và sai số ký tự (CER) so với kết quả tham chiếu:

```bash
python scripts/asr_eval/compute_wer.py \
  --predictions experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl \
  --output experiments/asr/baseline/metrics/dev/chunkformer_dev_metrics.json
```

## 9. Run clinical error analysis

Chạy phân tích các nhóm lỗi thuật ngữ y tế/lâm sàng quan trọng (Missing symptom, Medication error...):

```bash
python scripts/asr_eval/asr_medical_error_analysis.py \
  --predictions experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl \
  --terms experiments/asr/error_analysis/medical_terms_for_asr_check.json \
  --output experiments/asr/error_analysis/dev/chunkformer_dev_medical_errors.json
```

## 10. Export final report

Tổng hợp các kết quả JSON vào một báo cáo kỹ thuật hoàn chỉnh:

```bash
# Tổng hợp các metrics và medical error vào báo cáo benchmark
python scripts/asr_eval/clinical_error_analysis.py \
  --metrics_dir experiments/asr/baseline/metrics \
  --error_dir experiments/asr/error_analysis \
  --output_report experiments/asr/baseline/FINAL_REPORT.md
```
