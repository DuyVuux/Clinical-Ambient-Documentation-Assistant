# Medical ASR Error Report — Day 6

## 1. Purpose

Báo cáo này so sánh 3 model ASR không chỉ theo WER/CER, mà còn theo các lỗi có rủi ro lâm sàng:

- mất phủ định;
- sai triệu chứng;
- sai thuốc;
- sai liều/đơn vị;
- sai dị ứng;
- sai red flag.

## 2. Models compared

| Model | Strict WER | Normalized WER | Strict CER | Normalized CER | Runtime | Role |
|---|---:|---:|---:|---:|---|---|
| khanhld/chunkformer-ctc-large-vie | 12.90% | 12.90% | 12.03% | 12.03% | ~1.23s/sample | Primary |
| vinai/PhoWhisper-medium | 24.64% | 21.51% | 19.83% | 19.54% | ~0.42s/sample | Strong backup |
| vinai/PhoWhisper-base | 26.75% | 24.11% | 21.05% | 20.73% | ~0.14s/sample | Lightweight backup |

## 3. Error taxonomy

| Error category | Why it matters |
|---|---|
| Negation | Mất "không/chưa" có thể đảo nghĩa lâm sàng |
| Symptom | Bỏ sót triệu chứng làm note thiếu thông tin |
| Medication | Sai tên thuốc ảnh hưởng ghi chép điều trị |
| Dose/unit | Sai 500mg/50mg là lỗi nguy hiểm |
| Allergy | Bỏ sót dị ứng là lỗi critical |
| Red flag | Bỏ sót đau ngực/khó thở/sốt cao gây rủi ro safety |

## 4. Summary table

Bảng dưới đây tổng hợp số lượng từ khoá y khoa bị bỏ sót (missing) của từng nhóm và số lượng file audio (samples) bị đánh dấu có rủi ro nghiêm trọng (critical/high missing error):

| Model | Negation missing | Symptom missing | Medication missing | Dose/unit missing | Allergy missing | Red flag missing | Clinical risk note |
|---|---:|---:|---:|---:|---:|---:|---|
| ChunkFormer | 7 | 7 | 0 | 1 | 0 | 0 | 7 critical/high samples |
| PhoWhisper-medium | 7 | 7 | 0 | 1 | 0 | 0 | 7 critical/high samples |
| PhoWhisper-base | 6 | 9 | 0 | 1 | 0 | 0 | 6 critical/high samples |

## 5. Interpretation

### ChunkFormer

- **Chất lượng chung (WER):** Đạt WER tốt nhất trong 3 models (12.90%).
- **Lỗi y khoa (Clinical Errors):** Số lượng lỗi tương đương với PhoWhisper-medium (7 mẫu lỗi critical/high). Model này bỏ sót 7 từ phủ định và 7 triệu chứng, 1 lỗi liên quan đến liều lượng.
- **Đánh giá:** Mặc dù WER thấp hơn đáng kể so với PhoWhisper-medium, số lỗi y khoa critical là tương đương. Điều này cho thấy ChunkFormer xuất sắc hơn ở các từ ngữ thông thường, nhưng khi đối diện với các từ khóa y khoa quan trọng (như từ phủ định), model vẫn cần được cải thiện bằng fine-tuning.

### PhoWhisper-medium

- **Chất lượng chung (WER):** WER chưa đạt mục tiêu (21.51%).
- **Lỗi y khoa (Clinical Errors):** Mức độ bỏ sót từ phủ định và triệu chứng hoàn toàn giống ChunkFormer (7 phủ định, 7 triệu chứng, 1 liều lượng).
- **Đánh giá:** Tỷ lệ lỗi y khoa critical tương đương ChunkFormer mặc dù WER cao hơn gần gấp đôi. Điều này phản ánh ưu thế của họ mô hình Whisper về tính Robust trong việc nhận diện một số keyword, nhưng do lỗi word-level lớn nên vẫn không thể cạnh tranh với ChunkFormer về tổng thể.

### PhoWhisper-base

- **Chất lượng chung (WER):** WER cao nhất (24.11%).
- **Lỗi y khoa (Clinical Errors):** Lỗi bỏ sót từ phủ định (6) ít hơn một chút, nhưng lỗi bỏ sót triệu chứng cao nhất (9). 
- **Đánh giá:** Phù hợp làm giải pháp dự phòng nhẹ (lightweight fallback).

## 6. Decision

- **Primary Model:** Chọn **ChunkFormer** để chạy `test_holdout` ở ngày 7. Lý do: ChunkFormer có độ chính xác ngôn ngữ tổng quát (WER) vượt trội, trong khi rủi ro y khoa (clinical risk) tương đương PhoWhisper-medium.
- **Tiền đề cho Fine-Tuning:** Số lượng lỗi phủ định (negation missing) vẫn còn xuất hiện. Đây sẽ là trọng tâm để cải tiến (thêm trọng số vào data y khoa, text augmentation) ở các bước tiếp theo.
- **Backup Model:** Sử dụng mô hình PhoWhisper (base/medium) làm fallback option trong các môi trường triển khai bị hạn chế tài nguyên phần cứng.