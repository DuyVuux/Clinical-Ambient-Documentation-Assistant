# Model Selection Decision — Day 6

## 1. Dev leaderboard

| Model | Strict WER | Normalized WER | Runtime | Role |
|---|---:|---:|---|---|
| khanhld/chunkformer-ctc-large-vie | 12.90% | 12.90% | ~1.23s/sample | primary |
| vinai/PhoWhisper-medium | 24.64% | 21.51% | ~0.42s/sample | strong backup |
| vinai/PhoWhisper-base | 26.75% | 24.11% | ~0.14s/sample | lightweight backup |
| openai/whisper-small | 58.58% | 53.23% | ~0.26s/sample | drop |

## 2. Reproducibility

ChunkFormer dev rerun:

| Metric | Value |
|---|---:|
| n_samples | 200 |
| strict WER | 12.9007% |
| normalized WER | 12.9007% |
| strict CER | 12.0328% |
| normalized CER | 12.0328% |

Result:
- PASS

## 3. Leakage check

Result:
- PASS

## 4. Medical error analysis

Kết quả từ báo cáo phân tích rủi ro lâm sàng tự động (Automated Clinical Error Analysis):

| Model | Clinical error status | Note |
|---|---|---|
| ChunkFormer | **7** critical/high missing errors | Số lượng lỗi nguy hiểm tương đương PhoWhisper-medium, nhưng có chỉ số ngôn ngữ tổng quát (WER) tốt hơn rất nhiều. Lỗi chủ yếu tập trung ở việc bỏ sót từ phủ định (7) và triệu chứng (7). |
| PhoWhisper-medium | **7** critical/high missing errors | Thể hiện sự ổn định (robustness) của họ Whisper trong việc nhận diện keyword y khoa, tuy nhiên sai số word-level tổng quát lớn. Bỏ sót 7 từ phủ định và 7 triệu chứng. |
| PhoWhisper-base | **6** critical/high missing errors | Số lượng lỗi mất từ phủ định ít hơn một chút (6) nhưng bỏ sót triệu chứng nghiêm trọng nhất (9). |

## 5. Runtime / deployment trade-off

| Model | Advantage | Disadvantage |
|---|---|---|
| ChunkFormer | Best WER (12.90%), vượt xa target < 20% | Runtime chậm nhất (~1.23s/sample), kiến trúc CTC đòi hỏi pipeline xử lý riêng, cần rà soát kỹ compliance/license (CC BY-NC 4.0). |
| PhoWhisper-medium | Runtime nhanh (~0.42s/sample), hệ sinh thái Whisper hỗ trợ tốt | WER (21.51%) chưa đạt mục tiêu (< 20%) ở dạng zero-shot, cần fine-tuning. |
| PhoWhisper-base | Runtime cực nhanh (~0.14s/sample), tối ưu phần cứng | WER cao nhất (24.11%), độ chính xác chưa đáp ứng y khoa. |
| Whisper-small | Đóng vai trò baseline đối chứng | WER quá cao (53.23%) trên dữ liệu tiếng Việt. |

## 6. Decision

**Primary Model (Dành cho Test Holdout Ngày 7):**
- **`khanhld/chunkformer-ctc-large-vie`**: Được chọn làm mô hình đánh giá cuối cùng nhờ đạt mức WER xuất sắc 12.90%. Dù vẫn tồn tại lỗi lâm sàng (mất từ phủ định), hiệu suất ngôn ngữ tổng quát vượt trội giúp giảm thiểu công sức hậu kiểm (post-editing) cho bác sĩ.

**Backup & Fine-Tuning Candidates (Dành cho Tuần 4):**
- **`vinai/PhoWhisper-medium`**: Là ứng cử viên số một cho quá trình Fine-tuning. Với nền tảng kiến trúc Seq2Seq mạnh mẽ, runtime tốt và khả năng bắt keyword lâm sàng tương đương ChunkFormer, mô hình này có tiềm năng lớn nếu được tinh chỉnh chuyên sâu trên miền y khoa.
- **`vinai/PhoWhisper-base`**: Được giữ lại dưới vai trò "lightweight fallback" cho các môi trường triển khai edge-device.

**Dropped:**
- **`openai/whisper-small`**

## 7. Rationale

Quyết định lựa chọn ChunkFormer làm mô hình chính phản ánh chiến lược ưu tiên **độ chính xác tổng thể (Overall Accuracy)** trong giai đoạn đánh giá ban đầu, đảm bảo văn bản trích xuất ít lỗi ngữ nghĩa thông thường nhất. Tuy nhiên, rủi ro về y khoa (như mất từ phủ định) chỉ ra rằng không có mô hình nào đạt "Zero Clinical Risk" ở trạng thái off-the-shelf. 

Do đó, lộ trình tiếp theo bắt buộc phải bao gồm quy trình Fine-Tuning có trọng số (weighted loss) tập trung vào các thực thể y khoa (Medical Entities: Negation, Symptom, Medication, Red Flag), với ứng viên sáng giá là họ mô hình PhoWhisper nhờ lợi thế tuyệt đối về tốc độ xử lý thời gian thực (Real-time factor).