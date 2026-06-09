# Báo cáo Đánh giá Baseline Safe Dev — Ngày 1 Tuần 5

## Mục tiêu

Đánh giá lại (re-baseline) các mô hình ASR chính và dự phòng trên tập dữ liệu tiền xử lý an toàn đã đóng băng.

## Tiền xử lý (đã đóng băng)

`p03_safe_hybrid_v0_1`

## Dữ liệu

| Tập dữ liệu | Manifest | Số lượng mẫu |
|---|---|---:|
| dev | `vietmed_dev_preprocessed_selected_safe_v0_1.jsonl` | 200 |

## Mô hình

| Mô hình | Vai trò |
|---|---|
| `khanhld/chunkformer-ctc-large-vie` | Mô hình tham chiếu chính (baseline) |
| `vinai/PhoWhisper-medium` | Mô hình mục tiêu để fine-tune |

## Kết quả

| Mô hình | WER | CER | Lỗi thiếu từ phủ định | Lỗi thiếu triệu chứng | Lỗi tên thuốc | Lỗi liều/đơn vị | Quyết định |
|---|---:|---:|---:|---:|---:|---:|---|
| ChunkFormer | 12.90% | 12.06% | 7 | 7 | 0 | 1 | Tham chiếu |
| PhoWhisper-medium | 24.64% | 19.80% | 7 | 7 | 0 | 3 | Mục tiêu fine-tune |

## Phân tích kết quả

- **WER/CER:** Mô hình ChunkFormer (baseline) đang cho kết quả rất tốt với WER 12.90%. Trong khi đó, PhoWhisper-medium hiện tại có WER là 24.64%, còn cách mục tiêu đề ra (WER < 20%) khoảng 4.64%.
- **Lỗi lâm sàng:** Về khả năng nhận diện các thuật ngữ y tế, cả hai mô hình đều bỏ sót một số lượng từ phủ định (7 trường hợp) và triệu chứng (7 trường hợp) như nhau. Tuy nhiên, PhoWhisper-medium có số lỗi liên quan đến liều lượng/đơn vị nhiều hơn (3 lỗi so với 1 lỗi của ChunkFormer). Cả hai mô hình đều không có lỗi liên quan đến tên thuốc trong tập dev này.

**Định hướng tiếp theo:** Cần tiến hành fine-tune mô hình PhoWhisper-medium để cải thiện độ chính xác tổng thể (giảm WER xuống dưới 20%) và cần đặc biệt chú ý không làm tăng các lỗi liên quan đến y tế, đặc biệt là lỗi liều lượng/đơn vị đang cao hơn so với baseline.

## Mục tiêu Fine-tune

PhoWhisper-medium cần đạt được:

- WER < 20%
- Không làm tăng số lượng các lỗi lâm sàng so với mô hình baseline (ChunkFormer).

## Các nguyên tắc an toàn (Guardrails)

- Không sử dụng tập `test_holdout` trong quá trình này.
- Chưa tiến hành fine-tune trên bất kỳ mô hình nào trong Ngày 1.
- Quy trình tiền xử lý được giữ nguyên, không thay đổi so với đã chốt.