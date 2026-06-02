# 07. Ma trận Quyết định Đề xuất (Recommended Decision Matrix)

Để ra quyết định lựa chọn mô hình một cách khách quan, Đội ngũ Lãnh đạo Công nghệ (CTO, AI Lead, PM) nên sử dụng Ma trận Chấm điểm có Trọng số (Weighted Scoring Matrix). 
Các ứng viên được chấm từ 1 (Rất kém) đến 5 (Xuất sắc) cho từng tiêu chí, sau đó nhân với trọng số.

*(Bảng dưới đây là điểm đánh giá sơ bộ dựa trên phân tích học thuật. Kỹ sư AI bắt buộc cập nhật lại 2 tiêu chí đầu tiên sau khi chạy Local Benchmark).*

| Tiêu chí Đánh giá (Criteria) | Trọng số | Lý luận phân bổ Trọng số | Điểm Sơ bộ: Whisper Large-v3 | Điểm Sơ bộ: PhoWhisper (Large) | Điểm Sơ bộ: VietASR (68M) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tỷ lệ Lỗi Thực thể Trọng yếu (CEER)** | **25%** | Quyết định sự sống còn dự án. Nhận sai thuốc/chỉ định = không thể triển khai (pháp lý). | *Chờ số liệu Local Benchmark* | *Chờ số liệu Local Benchmark* | *Chờ số liệu Local Benchmark* |
| **Độ chính xác Code-switching (Thuốc/Liều/Dị ứng)** | **20%** | Bác sĩ Việt Nam liên tục pha trộn tiếng Anh y khoa (Code-switching). | **4** (Nhận diện tiếng Anh tốt) | **2.5** (Quên thảm khốc: CS-WER 62.55%) | **2.5** (CS-WER cao 58.38%) |
| **Bảo mật & Tính khả thi Triển khai Cục bộ (On-prem)** | **15%** | Dữ liệu chứa PHI, bắt buộc chạy máy chủ bệnh viện, cấm gọi API mở. | **2** (Cần GPU đắt đỏ, 1.5B params) | **2** (Cần GPU đắt đỏ, tương tự) | **5** (Siêu nhẹ 68M, chạy máy biên) |
| **WER/CER Tiếng Việt Tổng quát** | **10%** | Giúp hồ sơ mạch lạc, tuy nhiên lỗi từ phụ không gây hậu quả lâm sàng. | **3** (Tốt nhưng hay vấp phương ngữ) | **5** (SOTA hiện hành cho tiếng Việt) | **4** (Vượt trội Whisper Large trên thực tế) |
| **Khả năng Tinh chỉnh (Fine-tuning Feasibility)** | **10%** | Không mô hình nào sẵn sàng ngay, tính dễ áp dụng LoRA/PEFT là điểm cộng. | **3** (Nặng nề, tốn kém tài nguyên) | **4** (Cộng đồng Hugging Face hỗ trợ mạnh) | **3** (Cần tìm hiểu công cụ huấn luyện Zipformer) |
| **Tốc độ Suy luận (Latency)** | **10%** | Hồ sơ bệnh án cần tạo ra ngay (near real-time). | **2** (Chậm nếu không tối ưu) | **3** (Cần faster-whisper/CTranslate2) | **5** (Rất nhanh nhờ nhỏ gọn) |
| **Chi phí Vận hành (Deployment Cost)** | **10%** | Ảnh hưởng đến khả năng scale kinh doanh. | **1** (GPU rất đắt) | **2** (Tương đương) | **5** (Tiết kiệm mạnh chi phí cứng) |
