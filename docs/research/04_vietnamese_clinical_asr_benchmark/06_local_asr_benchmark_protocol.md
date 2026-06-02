# 06. Quy trình Đánh giá Benchmark Nội bộ Đề xuất (Local Benchmark Protocol)

Các kết quả đánh giá công cộng chỉ mang tính tham khảo. Đội ngũ Kỹ sư và QA bắt buộc thiết lập Quy trình Đánh giá Nội bộ (SOP) nghiêm ngặt sau:

## 1. Xây dựng Tập dữ liệu Vàng (Golden Dataset Creation)
*   **Kích thước mẫu:** Tối thiểu 50-100 giờ âm thanh (tương đương 300-500 phiên khám bệnh kéo dài 10-15 phút).
*   **Loại hình:** Ưu tiên dữ liệu thực tế (đã khử định danh/consent). Nếu vướng pháp lý, dùng phương pháp **Bệnh nhân Tiêu chuẩn (Standardized Patients)**. TUYỆT ĐỐI không dùng văn bản đọc sẵn (unscripted audio is mandatory).
*   **Phân bổ Chuyên khoa:** 
    *   *Tim mạch/Nội tiết:* Nặng về con số, liều lượng.
    *   *Truyền nhiễm/Miễn dịch:* Nặng về thông tin phủ định (negation) và dị ứng.
    *   *Nội tổng hợp:* Tên thuốc dài (polypharmacy).
*   **Phương ngữ:** Tối thiểu 40% giọng Bắc, 40% giọng Nam, 20% giọng Trung.

## 2. Cấu trúc Môi trường Thu âm (Acoustic Conditions)
Sử dụng Microphone đa hướng (Omnidirectional), đặt xa. Tổ chức thu âm theo các phân lớp:
1.  **Clean audio:** Phòng tĩnh lặng.
2.  **Mild clinic noise:** Nhiễu nền nhẹ (quạt, điều hòa, gõ bàn phím).
3.  **High clinic noise:** Nhiễu nặng (còi xe, loa gọi tên, tiếng cáng xe).
4.  **Overlapping speech:** Bệnh nhân và bác sĩ tranh nhau nói.
5.  **Masked speech:** Giao tiếp qua khẩu trang y tế (làm nghẹt tần số cao).

## 3. Tiêu chuẩn Gán nhãn và Chấm điểm (Annotation & Entity Schema)
*   **Hướng dẫn sao chép (Verbatim Transcription):** Gán nhãn y nguyên âm thanh (kể cả vấp "à, ờ", hay đọc tắt "hát a"). Tuyệt đối không tự ý dịch (Ví dụ: "hát a" không được ghi thành "huyết áp").
*   **Lược đồ Thực thể (Entity Schema):** Sử dụng thẻ XML/JSON để bọc thực thể. 
    *   *Ví dụ:* `<NEG>không</NEG> có tiền sử dị ứng <MED>Penicillin</MED>, uống <MED>Paracetamol</MED> <DOS>500mg</DOS>`.
*   **Quy trình Xét duyệt (Dual-pass):** Hai chuyên viên gán nhãn độc lập. Nếu xung đột > 5%, Bác sĩ chuyên khoa làm trọng tài (Adjudicator) để chốt bản Reference.

## 4. Phương pháp Chấm điểm và Ngưỡng Đạt (Pass/Fail Thresholds)
Thuật toán Levenshtein Distance trên cả chuỗi văn bản thô (cho WER) và văn bản trong thẻ XML (cho CEER, NCER).

*   **WER Tổng quát:** Phải **< 25%** (Mức chấp nhận được trong môi trường ồn).
*   **CEER (Lỗi Thực thể Trọng yếu):** Phải **< 5%**.
*   **NCER (Lỗi Phủ định):** Phải **< 2%** (Sai lầm phủ định là tối kỵ).
*   **Hallucination Rate (Ảo giác Y khoa):** Phải **< 1%** (Mô hình không được tự sáng tác thuốc).
