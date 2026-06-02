# 10. Khoảng trống Nghiên cứu & Rủi ro Hệ thống (Context for AI Build: Gaps & Risks)

Phần này tổng hợp bối cảnh những khoảng trống nghiên cứu và rủi ro tiền ẩn lớn nhất, nhằm định hướng cho quá trình tinh chỉnh và phát triển mô hình ASR (AI Build) an toàn.

## 1. Sự "Tắt tiếng" của Dữ liệu Y tế Môi trường Ồn (The Ambient Clinical Data Gap)
*   **Rủi ro:** Sự chênh lệch phân phối (distributional mismatch). Các bộ dữ liệu tiếng Việt hiện tại (như VietMed) đa phần được thu âm rất rõ ràng, tĩnh lặng (điện thoại, podcast). 
*   **Hậu quả:** Khi mang mô hình huấn luyện từ dữ liệu này vào phòng cấp cứu ồn ào (tiếng vọng, còi báo động), hiệu suất mô hình sẽ sụp đổ (catastrophic degradation).
*   **Hành động:** Đội ngũ bắt buộc phải tự thân mô phỏng và thu thập dữ liệu "Ambient" tại hiện trường.

## 2. Lời nguyền của Hiện tượng Chuyển mã (Code-Switching Penalty / Catastrophic Forgetting)
*   **Rủi ro:** Khi tinh chỉnh sâu một mô hình đa ngôn ngữ (Whisper) thành mô hình thuần Việt (PhoWhisper), mô hình xảy ra hiện tượng "quên thảm khốc" (catastrophic forgetting).
*   **Hậu quả:** Mô hình quên cách biểu diễn các thuật ngữ tiếng Anh y khoa (Medical English islands). Ví dụ: "sưng tấy ở abdomen" bị ép thành từ Việt vô nghĩa "áp đô men".
*   **Hành động:** Buộc phải trộn dữ liệu song ngữ (bilingual data blending) trong quá trình tinh chỉnh nội bộ.

## 3. Hội chứng Tôn sùng WER (Over-reliance on WER Risk)
*   **Rủi ro:** Các kỹ sư theo đuổi việc hạ thấp Tỷ lệ Lỗi Từ (WER) tổng quát.
*   **Hậu quả:** Tối ưu hóa WER có xu hướng "san phẳng" các từ hiếm (tên biệt dược) và thay bằng các từ bình dân nghe tương tự để tối đa xác suất ngôn ngữ. Điều này biến ASR thành một "cỗ máy nói dối mượt mà", cực kỳ nguy hiểm trong y khoa.
*   **Hành động:** Chuyển sang sử dụng các bộ chỉ số đo lường tập trung vào thực thể an toàn (CEER, NCER).

## 4. Bóng ma của Ảo giác Y khoa (Medical Hallucination Risk)
*   **Rủi ro:** Cấu trúc tự hồi quy (autoregressive) của mô hình Encoder-Decoder (như Whisper).
*   **Hậu quả:** Khi gặp nhiễu hoặc bác sĩ im lặng để gõ máy tính, hệ thống tự động "bịa" ra các câu không có thật để lấp chỗ trống. Nguy cơ ASR "tự kê thêm thuốc" vào hồ sơ là có thật.
*   **Hành động:** Sử dụng kiến trúc (như `faster-whisper`) tích hợp bộ lọc VAD (Voice Activity Detection) cực kỳ khắt khe trước khâu giải mã để loại bỏ khoảng lặng/nhiễu.
