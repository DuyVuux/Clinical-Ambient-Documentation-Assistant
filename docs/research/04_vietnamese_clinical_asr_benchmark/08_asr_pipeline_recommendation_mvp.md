# 08. Khuyến nghị Cuối cùng & Kiến trúc Pipeline MVP (Final Recommendation)

Dựa trên bằng chứng khoa học, phân tích ngôn ngữ y khoa và rào cản hệ thống, lộ trình hành động thiết thực dành cho CTO, AI Lead và Đội ngũ QA như sau:

## 1. Ngừng ảo tưởng về giải pháp "Plug-and-Play"
Thống nhất trong toàn tổ chức: Hiện tại, **KHÔNG CÓ BẤT KỲ** mô hình ASR tiếng Việt công cộng nào (từ OpenAI, VinAI, hay các viện nghiên cứu) đủ "production-ready" cho Ambient Clinical Documentation. Dùng trực tiếp sẽ gây sai sót y khoa nghiêm trọng.

## 2. Định hình Hướng đi Kiến trúc (Architectural Direction)
*   Sử dụng họ mô hình **Whisper / PhoWhisper (phiên bản Small hoặc Base)** làm nền tảng khởi điểm. (Dù VietASR gọn nhẹ, hệ sinh thái CTranslate2/faster-whisper hiện hỗ trợ lượng hóa và cắt khoảng lặng VAD tốt hơn cho on-premise).
*   Khả năng tự tạo dấu câu tự nhiên của Whisper là lợi thế khổng lồ để cấp input chuẩn xác cho LLM ở tầng sau (tóm tắt hồ sơ).

## 3. Khởi động Chiến dịch Thu thập Dữ liệu Ambient Nội bộ
*   Lập tức thu thập 50-100 giờ âm thanh **Tập dữ liệu Vàng (Golden Dataset)** với micro đa hướng.
*   Phải đảm bảo mô phỏng được tiếng ồn, sự chồng lấp giọng nói và hiện tượng Code-switching Anh-Việt theo đúng Giao thức (SOP) Local Benchmark.

## 4. Thiết lập Pipeline Tinh chỉnh Hiệu quả (Fine-Tuning Strategy)
*   **PEFT / LoRA:** Áp dụng kỹ thuật Tinh chỉnh Hiệu quả Tham số (Parameter-Efficient Fine-Tuning) trên mô hình PhoWhisper-Small/Base.
*   **Bilingual Data Blending:** Trộn một tỷ lệ lớn dữ liệu Code-switching (tiếng Anh y khoa xen tiếng Việt) trong quá trình huấn luyện để giải quyết hiện tượng "quên thảm khốc".
*   **Contextual Biasing:** Cấu hình thiên lệch ngữ cảnh khi giải mã (Decoding) - nạp động danh sách thuốc/xét nghiệm của bệnh viện vào bộ từ vựng (dynamic vocabulary) để ép mô hình chọn tên thuốc thay vì từ thông thường.

## 5. Chuyển dịch Triết lý Đo lường (Metric Paradigm Shift)
*   Loại bỏ hoàn toàn WER khỏi vị trí là KPI cốt lõi. 
*   Áp dụng nghiêm ngặt bộ 3 chỉ số an toàn để nghiệm thu mô hình: **CEER (Tỷ lệ Lỗi Thực thể), NCER (Tỷ lệ Lỗi Phủ định), và SCER (Tỷ lệ Lỗi An toàn Lâm sàng)**.

## 6. Xây dựng Chốt chặn An toàn Cuối cùng (The Ultimate Safeguard)
*   **Thiết kế "Human-in-the-Loop" (Con người trong vòng lặp):** Giao diện UI phải tự động bôi đậm (highlight bằng màu cảnh báo) tất cả các Thực thể Trọng yếu (Tên thuốc, Liều lượng, Từ phủ định).
*   Bác sĩ hoặc y tá bắt buộc phải xác nhận các điểm nghẽn (choke-points) này trước khi đẩy vào Hệ thống Hồ sơ (EMR/HIS). ASR giảm 80% sức gõ phím, 20% thẩm định còn lại là trách nhiệm con người để bảo đảm sinh mạng bệnh nhân.
