# Quy trình Fine-tune Tuần 5 — Mô hình dự phòng PhoWhisper

## Mục tiêu

Fine-tune `vinai/PhoWhisper-medium` làm mô hình ASR dự phòng cho giọng nói y khoa lâm sàng tiếng Việt.

## Chỉ tiêu

Chỉ tiêu chính:

- Dev WER < 20%

Chỉ tiêu phụ:

- Không làm tăng các lỗi ASR quan trọng trong lâm sàng:
  - bỏ sót từ phủ định (missing negation)
  - bỏ sót triệu chứng (missing symptom)
  - lỗi thuốc (medication error)
  - lỗi liều lượng/đơn vị (dose/unit error)
  - lỗi chữ số (numeric error)

## Dữ liệu

| Tập dữ liệu | Manifest | Mục đích sử dụng |
|---|---|---|
| train | `data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl` | chỉ dùng để huấn luyện |
| dev | `data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_safe_v0_1.jsonl` | chỉ dùng để đánh giá (validation) |
| test_holdout | không sử dụng | bị cấm sử dụng trong Tuần 5 |

## Tiền xử lý (đã chốt)

`p03_safe_hybrid_v0_1`

## Mô hình

Ứng viên fine-tune:

- `vinai/PhoWhisper-medium`

Baseline tham chiếu:

- `khanhld/chunkformer-ctc-large-vie`

## Chỉ số đánh giá

Các chỉ số ASR:

- Strict WER
- Normalized WER
- Strict CER
- Normalized CER

Các chỉ số an toàn lâm sàng:

- bỏ sót từ phủ định (missing negation)
- bỏ sót triệu chứng (missing symptom)
- lỗi thuốc (medication error)
- lỗi liều lượng/đơn vị (dose/unit error)
- lỗi chữ số (numeric error)

## Các quy tắc bắt buộc (Guardrails)

- Không huấn luyện trên tập dev.
- Không sử dụng tập test_holdout.
- Không chọn checkpoint dựa trên kết quả của tập test_holdout.
- Không chỉnh sửa bản ghi (transcript) thủ công sau khi nhìn thấy lỗi của mô hình.
- Không thay đổi phương pháp chuẩn hóa văn bản (text normalization) sau khi đã chạy baseline.
- Không so sánh các mô hình sử dụng phiên bản tiền xử lý dữ liệu khác nhau.

## Tiêu chí nghiệm thu

Chấp nhận mô hình dự phòng đã fine-tune nếu thỏa mãn:

1. Dev WER < 20%.
2. Các lỗi lâm sàng không tăng so với kết quả baseline của PhoWhisper-medium.
3. Checkpoint được lựa chọn hoàn toàn dựa trên các chỉ số của tập dev.