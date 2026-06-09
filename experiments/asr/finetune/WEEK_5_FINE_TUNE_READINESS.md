# Chuẩn bị Fine-tune Tuần 5

## Tình trạng dữ liệu

| Tập (Split) | Số mẫu | Manifest | Tiền xử lý |
|---|---:|---|---|
| train | 600 | `vietmed_train_preprocessed_selected_safe_v0_1.jsonl` | p03_safe_hybrid_v0_1 |
| dev | 200 | `vietmed_dev_preprocessed_selected_safe_v0_1.jsonl` | p03_safe_hybrid_v0_1 |
| test_holdout | 200 | chưa đụng tới | không dùng |

## Baseline suy luận chính hiện tại

`khanhld/chunkformer-ctc-large-vie`

## Các ứng viên Fine-tune

1. `vinai/PhoWhisper-medium`
2. `vinai/PhoWhisper-base`
3. Phương án dự phòng: `openai/whisper-small`

## Mục tiêu Tuần 5

Giảm thiểu rủi ro ASR lâm sàng và cải thiện mô hình fine-tune/dự phòng, đặc biệt chú trọng:
- Lỗi bỏ sót từ phủ định (missing negation)
- Lỗi bỏ sót triệu chứng (missing symptom)
- Lỗi sai tên thuốc/liều lượng/đơn vị
- Các mẫu có rủi ro cận biên (edge-risk samples)
- Mục tiêu Normalized WER: < 20% trên tập `dev` đối với mô hình đã fine-tune.

## Nguyên tắc An toàn (Guardrails)

- Không huấn luyện (train) trên tập `dev`
- Không huấn luyện (train) trên tập `test_holdout`
- Không lựa chọn checkpoint dựa trên kết quả của tập `test_holdout`
- Đảm bảo tuyệt đối không rò rỉ dữ liệu (Kiểm tra chéo `sample_id` giữa các tập).

## Chiến lược Fine-tuning & Cơ sở hạ tầng

### 1. Phương pháp Huấn luyện
- **Phương pháp**: Ưu tiên sử dụng PEFT (Parameter-Efficient Fine-Tuning) với LoRA (Low-Rank Adaptation) cho các mô hình Whisper để tối ưu VRAM và hạn chế hiện tượng học quên (catastrophic forgetting), hoặc đóng băng (freeze) bộ mã hóa đặc trưng (feature encoder).
- **Độ chính xác (Precision)**: Sử dụng mixed precision (`fp16` hoặc `bf16`) để tối ưu bộ nhớ.

### 2. Siêu tham số (Gợi ý khởi tạo ban đầu)
- **Learning Rate**: ~1e-5 đến 1e-4 kết hợp với linear scheduler và warmup steps.
- **Batch Size**: Tùy thuộc vào giới hạn VRAM GPU (ví dụ: batch size 8 hoặc 16 kết hợp gradient accumulation).
- **Epochs**: Bắt đầu với 3-5 epochs; theo dõi `eval_loss` để tránh overfitting.
- **Optimizer**: AdamW.

### 3. Quy trình Đánh giá (Evaluation) trong quá trình Huấn luyện
- Thực hiện đánh giá trên tập `dev` theo các chu kỳ bước (step intervals) hoặc sau mỗi epoch.
- **Chỉ số chính**: `WER` và `CER`.
- **Ràng buộc Bắt buộc**: Phải áp dụng đúng hàm Chuẩn hóa Văn bản (Text Normalization) đã dùng ở Benchmark Tuần 3 trước khi tính toán các chỉ số trong lúc eval.
- Chỉ lưu lại các checkpoint tốt nhất dựa trên Normalized WER của tập `dev`.

## Đánh giá An toàn Lâm sàng (Sau Huấn luyện)

Sau khi chọn được checkpoint, mô hình fine-tune BẮT BUỘC phải trải qua quy trình kiểm tra Taxonomy Lỗi Lâm sàng:
- **Kiểm tra Rủi ro Nghiêm trọng (Critical Risk)**: Đảm bảo không làm suy giảm khả năng nhận diện từ phủ định hoặc dị ứng so với baseline.
- **Kiểm tra Rủi ro Cao (High Risk)**: Xác minh độ chính xác của tên thuốc, liều lượng/đơn vị, và các triệu chứng cảnh báo nguy hiểm (red-flag).
- Thực hiện kiểm tra chéo thủ công (manual sanity check) trên các mẫu edge-risk để đảm bảo mô hình không gặp ảo giác (hallucinate) các dữ kiện lâm sàng sau khi fine-tune.

## Checklist Trước khi Bấm chạy (Pre-Flight Kickoff)

- [ ] **Phần cứng**: Xác minh tình trạng GPU và bộ nhớ trống (ví dụ: T4/A10G/A100).
- [ ] **Môi trường**: Xác nhận các thư viện `transformers`, `peft`, `accelerate`, `datasets`, và `jiwer` đã được cập nhật và tương thích.
- [ ] **Smoke Test**: Chạy thử một vòng huấn luyện ảo (ví dụ: 10 mẫu trong 1 epoch) để bắt các lỗi tràn bộ nhớ (OOM) hoặc lỗi cú pháp (syntax errors).
- [ ] **Đồng bộ Metric**: Xác minh lại logic chuẩn hóa văn bản trong callback `compute_metrics` trùng khớp hoàn toàn với script đánh giá của Tuần 3.
- [ ] **Theo dõi (Observability)**: Xác nhận Weights & Biases (WandB) hoặc TensorBoard đã được cấu hình để vẽ biểu đồ loss và WER.