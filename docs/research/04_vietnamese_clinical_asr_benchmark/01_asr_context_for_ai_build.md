# 01. Bối cảnh Phát triển AI: ASR trong Môi trường Lâm sàng (ASR Context for AI Build)

## 1. Tóm tắt Thực thi (Executive Summary)

Việc đánh giá cảnh quan của các mô hình Nhận dạng Tiếng nói Tự động (ASR) tiếng Việt cho ứng dụng **Ghi nhận Tài liệu Lâm sàng Tự động (Ambient Clinical Documentation)** chỉ ra những định hướng chiến lược sau:

*   **Sự thiếu hụt dữ liệu lâm sàng "Ambient" công cộng:** Mặc dù có các bộ dữ liệu quy mô lớn (VietMed, ViMedCSS), hầu hết được thu trong điều kiện kiểm soát. Không có bộ dữ liệu công cộng nào phản ánh chính xác môi trường thu âm đa hướng tại phòng khám ồn ào ở Việt Nam.
*   **Thách thức cốt lõi từ hiện tượng Chuyển mã (Code-Switching):** Bác sĩ Việt Nam thường pha trộn tiếng Anh y khoa (ví dụ: "chụp MRI"). Các mô hình hàng đầu (PhoWhisper, Whisper-Large-v3) gặp lỗi nghiêm trọng (CS-WER lên tới 46.69% – 62.55%). Bắt buộc phải tiến hành tinh chỉnh nội bộ (fine-tuning).
*   **Sự vô hiệu của chỉ số WER:** Tỷ lệ Lỗi Từ (WER) tổng quát không tương quan với độ an toàn lâm sàng. Việc sai lệch con số liều lượng hoặc từ phủ định có thể gây tử vong. Định hướng kiểm chứng bắt buộc phải dùng **Tỷ lệ Lỗi Thực thể Trọng yếu (CEER)**.
*   **Đánh giá ứng viên Mô hình:** PhoWhisper và VietASR (68M tham số) là hai hướng đi sáng giá về chất lượng tiếng Việt. Tuy nhiên, khả năng bảo toàn thuật ngữ y tế phức tạp cần được kiểm tra trên dữ liệu thực tế.
*   **Kiến trúc Triển khai:** Whisper gốc chậm và ngốn VRAM. Việc áp dụng kiến trúc `faster-whisper` kết hợp `CTranslate2` là bắt buộc để tăng tốc 4x, hỗ trợ lượng hóa (quantization), và triển khai cục bộ (on-premise) đảm bảo bảo mật.
*   **Rủi ro Ảo giác (Hallucination):** Kiến trúc Encoder-Decoder (Whisper) dễ sinh văn bản ảo giác khi gặp khoảng lặng/nhiễu. Cần tích hợp bộ lọc Phát hiện Hoạt động Giọng nói (VAD) khắt khe.
*   **Chỉ định Hướng đi Tiếp theo:** Xây dựng một đường ống (pipeline) **Tinh chỉnh Hiệu quả Tham số (PEFT)** dựa trên PhoWhisper hoặc Whisper-Large-v3.

## 2. Bằng chứng về ASR trong Môi trường Y tế và Lâm sàng (Medical and Clinical ASR Evidence)

Phát triển hệ thống Ambient Clinical Documentation đối mặt với các rào cản kỹ thuật khắc nghiệt:

### 2.1. Đặc điểm Âm học của Môi trường Ambient
*   Sử dụng micro đa hướng gắn xa người nói (1-3 mét), tạo ra **hiện tượng âm vang (reverberation)**.
*   Hiệu ứng **"tiệc cocktail" (cocktail party effect)**: Tiếng nói hòa lẫn tiếng ồn (quạt, thiết bị y tế, hành lang).
*   Nghiên cứu quốc tế cho thấy ASR thương mại trong môi trường này có WER trung bình ~39%, không thể chấp nhận được nếu áp dụng trực tiếp.

### 2.2. Đặc tính Hội thoại Bác sĩ - Bệnh nhân
*   Hội thoại tự nhiên không theo ngữ pháp chuẩn: Bệnh nhân ngập ngừng, lặp từ, nói xen ngang. Bác sĩ nói nhanh, chuyển đổi giọng điệu đột ngột.
*   Hệ thống yêu cầu nhận diện người nói (**Speaker Diarization**) liên tục để phân định đúng tiền sử.

### 2.3. Sự Phức tạp của Thuật ngữ Y khoa và Chuyển mã
*   Ngôn ngữ y khoa pha trộn Hán-Việt, từ mượn Pháp, và tiếng Anh hiện đại.
*   Khi bác sĩ chêm tiếng Anh vào câu tiếng Việt (Code-switching), các ASR gặp sự cố diện rộng.

### 2.4. Rủi ro Lỗi Dịch mã Trọng yếu (Safety-Critical Errors)
*   Mọi lỗi ASR lâm sàng đều có thể dẫn đến kiện tụng/tử vong. Tỷ lệ Lỗi Thuật ngữ Y khoa (MTER) luôn cao hơn lỗi từ thông thường.
*   Mô hình Language Model nội tại có xu hướng "ép" từ hiếm thành từ phổ thông có âm tương tự. Tùy chỉnh mô hình cho miền lâm sàng có thể giảm WER tới 54%, nhưng lỗi liều lượng/phủ định vẫn cần giám sát của con người.
