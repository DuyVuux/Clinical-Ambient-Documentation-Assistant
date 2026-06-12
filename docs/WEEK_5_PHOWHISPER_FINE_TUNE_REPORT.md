# BÁO CÁO TINH CHỈNH MÔ HÌNH PHOWHISPER (TUẦN 5)
**Dự án:** Clinical Ambient Documentation Assistant  
**Giai đoạn:** Tuần 5 - Thử nghiệm Fine-Tuning  
**Mô hình cơ sở:** `vinai/PhoWhisper-medium`  
**Phiên bản mô hình đích:** `PhoWhisper Backup Model v0.1`

---

## 1. Tóm tắt thực thi (Executive Summary)

Trong khuôn khổ Tuần 5 của dự án, quy trình tinh chỉnh (fine-tuning) đã được tiến hành trên mô hình ngôn ngữ tiếng Việt `vinai/PhoWhisper-medium`. Việc lựa chọn mô hình này dựa trên các đánh giá rủi ro lâm sàng và lợi thế vượt trội về tốc độ xử lý thời gian thực (runtime ~0.42s/sample) so với các kiến trúc CTC truyền thống. 

Mục tiêu cốt lõi của đợt thử nghiệm này là thiết lập và xác thực một mô hình ASR dự phòng (backup model) an toàn, đáp ứng các tiêu chuẩn y khoa nghiêm ngặt, đồng thời tối ưu hóa khả năng nhận diện chính xác các thực thể lâm sàng (Medical Entities) thông qua phương pháp học có giám sát (supervised learning) trên tập dữ liệu y khoa tiếng Việt (Vietmed). Kết quả tinh chỉnh cho thấy mô hình đạt được chỉ số Word Error Rate (WER) ở mức **16.57%**, đáp ứng xuất sắc tiêu chí chấp nhận (< 20%) và không ghi nhận sự gia tăng nào về lỗi lâm sàng.

## 2. Cấu hình tập dữ liệu (Dataset Configuration)

Quy trình tinh chỉnh sử dụng các phân mảnh dữ liệu đã qua xử lý nghiêm ngặt nhằm đảm bảo tính nhất quán của miền dữ liệu (domain consistency) và ngăn ngừa tuyệt đối hiện tượng rò rỉ dữ liệu (data leakage).

- **Chiến lược tiền xử lý:** Cấu hình `p03_safe_hybrid_v0_1`.
- **Tập huấn luyện (Training Set):** `vietmed_train_preprocessed_selected_safe_v0_1` (Quy mô: 600 mẫu).
- **Tập kiểm định (Development Set):** `vietmed_dev_preprocessed_selected_safe_v0_1` (Quy mô: 200 mẫu).

**Nguyên tắc bảo toàn dữ liệu:** Toàn bộ bản sao văn bản (transcripts) được giữ nguyên vẹn ở trạng thái thô chưa qua chỉnh sửa thủ công (transcripts were not edited). Điều này nhằm duy trì tính toàn vẹn của môi trường thử nghiệm và đánh giá chính xác năng lực nội tại của mô hình đối với dữ liệu thực tế.

## 3. Thiết kế thử nghiệm (Experimental Design)

Hai kịch bản tinh chỉnh (runs) độc lập đã được triển khai nhằm đối chuẩn và đánh giá độ nhạy của tham số tốc độ học (learning rate) cũng như số chu kỳ huấn luyện (epochs) đối với khả năng hội tụ của kiến trúc PhoWhisper-medium.

### 3.1. Thử nghiệm 01 (Run 01): Cấu hình Conservative
- **Mục tiêu:** Thử nghiệm học sâu với tốc độ hội tụ tiêu chuẩn, hướng tới sự ổn định của trọng số.
- **Tốc độ học (Learning Rate):** `1e-5`
- **Số chu kỳ (Epochs):** `3`
- **Khối lượng dữ liệu:** 600 mẫu (Train) / 200 mẫu (Dev)
- **Đầu ra (Artifacts):** `best_model/`, `predictions_dev.jsonl`, `metrics_dev_project_wer.json`, `medical_errors_dev.json`.

### 3.2. Thử nghiệm 02 (Run 02): Cấu hình Low-LR
- **Mục tiêu:** Thử nghiệm học sâu với tốc độ hội tụ chậm nhằm phân tích và hạn chế hiện tượng quên thảm họa (catastrophic forgetting).
- **Tốc độ học (Learning Rate):** `5e-6`
- **Số chu kỳ (Epochs):** `5`
- **Khối lượng dữ liệu:** 600 mẫu (Train) / 200 mẫu (Dev)
- **Đầu ra (Artifacts):** Tương tự cấu hình Run 01.

## 4. Đánh giá hiệu năng và Kết quả (Performance Evaluation & Results)

Mô hình tinh chỉnh được đánh giá tự động hóa hoàn toàn trên tập Dev với các tiêu chí khắt khe về từ vựng và ngữ cảnh y khoa.

### 4.1. Bảng đối chuẩn kết quả (Benchmarking Results)

| Thử nghiệm (Run) | Vai trò (Role) | WER | CER | Lỗi phủ định (Missing Negation) | Lỗi triệu chứng (Missing Symptom) |
|---|---|:---:|:---:|:---:|:---:|
| **ChunkFormer (Reference)** | Primary Reference | 12.90% | 12.06% | Không có | Không có |
| **PhoWhisper-medium (Baseline)** | Backup Baseline | 24.64% | 19.80% | Không có | Không có |
| **Run 01 (Conservative)** | **Candidate 1** | **16.57%** | **14.64%** | **Không có** | **Không có** |
| **Run 02 (Low-LR)** | Candidate 2 | 18.22% | 16.24% | Không có | Không có |

*Lưu ý: Không ghi nhận lỗi về thuốc (Medication error), liều lượng/đơn vị (Dose/unit error) hay số liệu (Numeric error) trong toàn bộ các ứng viên đánh giá.*

### 4.2. Hàng rào bảo vệ và tuân thủ (Guardrails & Compliance)

Để đảm bảo tính minh bạch và độ tin cậy của quy trình đánh giá, các nguyên tắc sau đã được áp dụng triệt để:

1. **Cô lập dữ liệu đánh giá (Data Isolation):** Tập dữ liệu kiểm thử (Test Holdout) hoàn toàn không được sử dụng trong quá trình huấn luyện hay can thiệp vào bộ chọn checkpoint.
2. **Ngăn chặn rò rỉ (Zero Leakage):** Tập Dev chỉ đóng vai trò đánh giá và tính toán metric, hoàn toàn không cung cấp gradient cho việc cập nhật trọng số huấn luyện.
3. **Kiểm định lâm sàng (Clinical Validation):** Chỉ số lỗi lâm sàng (Clinical error metrics) được kiểm tra tự động trước khi xác nhận chọn lựa mô hình, đảm bảo tính mạng bệnh nhân không bị ảnh hưởng bởi lỗi của AI (đặc biệt liên quan đến phủ định và triệu chứng).

## 5. Quyết định lựa chọn và Định hướng ứng dụng (Decision & Intended Use)

Dựa trên kết quả đo lường thực nghiệm và bộ tiêu chí chấp nhận (Acceptance Criteria):
- **WER < 20%**
- **Không gia tăng rủi ro lâm sàng** so với mô hình cơ sở.

**QUYẾT ĐỊNH (DECISION): ACCEPT_BACKUP_V0_1**
- **Mô hình được chọn:** `Run 01 (Conservative)`
- **Lý do:** WER đạt 16.57% (thấp hơn so với Run 02 là 18.22%), cải thiện đáng kể so với baseline (24.64%) và duy trì tỉ lệ lỗi lâm sàng ở mức 0.

### Định hướng ứng dụng (Intended Use)
Phiên bản **PhoWhisper Backup Model v0.1** sẽ đóng vai trò làm ASR Model dự phòng cho phân hệ nhận dạng giọng nói trong lĩnh vực y khoa tiếng Việt. Mô hình này được thiết kế để đồng hành cùng mô hình chính (Primary Model - ChunkFormer) trong hệ thống Clinical Ambient Documentation Assistant nhằm bảo vệ luồng dữ liệu liên tục trong trường hợp hệ thống chính gặp sự cố quá tải.

## 6. Kế hoạch tiếp theo (Next Actions)

1. **Đóng băng phiên bản (Freeze Model):** Lưu trữ và khóa cấu hình checkpoint của mô hình dự phòng `Run 01` đã được tinh chỉnh.
2. **Hoàn thiện giao thức kiểm thử (Finalize Evaluation Plan):** Tuyệt đối không khởi chạy đánh giá trên tập `test_holdout` cho đến khi toàn bộ giao thức lựa chọn mô hình chung được phê duyệt ở cấp độ kiến trúc hệ thống (Week 6).
3. **Tích hợp Pipeline (Pipeline Integration):** Đưa mô hình dự phòng vào pipeline đánh giá tổng thể (Week 6) để đối chuẩn hiệu năng hệ thống trên các ca lâm sàng có tính phức tạp cao ngoài môi trường thực tế.

---
*Báo cáo được trích xuất và tổng hợp tự động dựa trên nhật ký hệ thống (Run 01, Run 02 & Model Card v0.1) vào hệ thống quản lý tri thức của dự án.*
