# 03. Tổng quan về Benchmark ASR Tiếng Việt (Vietnamese ASR Benchmark Review)

Hệ sinh thái dữ liệu Nhận dạng Tiếng nói Tự động (ASR) tiếng Việt đã phát triển bùng nổ. Tuy nhiên, việc đánh giá năng lực các mô hình ASR yêu cầu phân tích sâu vào bản chất phân phối của dữ liệu (data distribution) thay vì chỉ dựa trên bảng xếp hạng (leaderboard).

## Hệ sinh thái Dữ liệu Benchmark Công cộng

| Tên Bộ Dữ liệu | Miền Dữ liệu (Domain) | Quy mô | Chỉ số Đánh giá | Độ Phù hợp với Lâm sàng Tự động | Hạn chế Cốt lõi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VIVOS** | Đọc văn bản (Read speech) | 15 giờ | WER / CER | **Rất thấp**. Giọng tĩnh, chuẩn mực. | Thiếu dấu câu, không viết hoa, không phản ánh ngắt lời, nhiễu môi trường, không thuật ngữ y khoa. |
| **VLSP (2020-2023)** | Đa miền (Tin tức, Phát thanh, YouTube) | Hàng trăm giờ | WER | **Thấp**. Phổ thông, có kiểm soát. | Không chứa hội thoại y khoa dài. Không có hiện tượng nói chồng lấp (overlapping speech). |
| **BUD500** | Podcast, hội thoại tự nhiên | ~500 giờ | WER | **Trung bình**. Giọng tự nhiên, đa phương ngữ. | Đa phần độc thoại podcast thay vì hội thoại tương tác (interactive). Hiếm thuật ngữ lâm sàng. |
| **PhoASR & VietSuperSpeech** | YouTube vlog, chăm sóc khách hàng | 500h & 267h | WER / Timestamp | **Trung bình cao**. Bắt tốt văn phong không trang trọng (casual), lặp từ, nói xen ngang. | Rỗng về ngữ nghĩa y khoa và thuật ngữ giải phẫu/dược lý. Thiết kế cho chatbot tổng quát. |
| **VietMed** | Y khoa (Bác sĩ - Bệnh nhân, Talkshow) | 16h gán nhãn, 1000h thô | WER / CER | **Cao**. Bao phủ ICD-10, 978 thuật ngữ độc nhất. | Thu từ YouTube/telehealth với âm thanh sạch. Không phản ánh tiếng vang và nhiễu (ambient noise) của phòng khám thực tế. |
| **ViMedCSS** | Y khoa có Chuyển mã (Code-Switching) | 34.6 giờ (16.576 câu) | WER, CS-WER | **Rất cao**. Phản ánh giao tiếp thực tế (pha trộn tiếng Anh - Việt). | Quy mô nhỏ. Chỉ tập trung vào chuyển mã, chưa mô phỏng trọn vẹn quy trình khám bệnh 15 phút. |
| **MultiMed-ST** | Dịch thuật Tiếng nói Đa ngôn ngữ | 290.000 mẫu | WER, BLEU | **Trung bình cao**. Đối chiếu thuật ngữ quốc tế. | Mục tiêu chính là Dịch thuật (Speech Translation), không thuần túy là ASR trong phòng khám. |

## Lỗ hổng Nghiên cứu và Thực tiễn Lâm sàng
Mặc dù có các tập dữ liệu lớn như **VietMed**, chúng vẫn bị phân tách khỏi thực tế của hệ thống Ghi nhận Lâm sàng Tự động (Ambient). Các mô hình đạt thành tích cao trên VIVOS hay BUD500 thường gặp **"cú sốc miền" (domain shift)** tại phòng mạch:
*   Môi trường âm thanh sạch (podcast) khác xa môi trường đa hướng, hỗn loạn lâm sàng.
*   Sự lệch pha này khiến việc đầu tư chỉ dựa vào benchmark công cộng là cực kỳ rủi ro.
*   Bắt buộc xác nhận tính hiệu quả thông qua **thước đo an toàn thực thể y tế (clinical safety metrics)** trên tập dữ liệu đặc thù tự thu thập.
