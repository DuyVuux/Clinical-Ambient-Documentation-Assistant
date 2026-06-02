# 04. Phân loại Mẫu Lỗi cho ASR Lâm sàng Tiếng Việt (Error Pattern Taxonomy)

Sự kết hợp giữa đặc tính đơn lập, thanh điệu của tiếng Việt và sự phức tạp của danh pháp y khoa quốc tế tạo ra một phổ lỗi (error taxonomy) độc đáo. Hệ thống Ghi nhận Tài liệu Lâm sàng Tự động phải đối mặt với các dạng lỗi phổ biến và cực kỳ nguy hiểm sau:

### 1. Nhầm lẫn Tên thuốc (Medication Name Confusion / LASA Errors)
*   **Cơ chế:** Tên biệt dược/hoạt chất đa âm tiết đi ngược lại quy tắc âm tiết học tiếng Việt. Bác sĩ thường phát âm trại đi. Rủi ro đặc biệt cao ở các cặp thuốc Look-Alike, Sound-Alike (LASA).
*   **Ví dụ:** Bác sĩ nói "Kê cho bệnh nhân Amlodipin" -> ASR: "Kê cho bệnh nhân ăn lo đi pin". Hoặc nhầm lẫn chí mạng: "Cefotaxim" và "Cefuroxim".

### 2. Nhầm lẫn Liều lượng (Dosage Confusion)
*   **Cơ chế:** Các số đếm kết thúc bằng âm khép (như "lăm", "mười") thường bị nuốt âm cuối trong luồng nói nhanh, làm mất gốc tín hiệu.
*   **Ví dụ:** "Bệnh nhân uống mười lăm (15) miligam" -> ASR: "Bệnh nhân uống năm mươi (50) miligam" (Nguy cơ quá liều độc tính).

### 3. Lỗi Đơn vị và Số đo (Number/Unit Errors)
*   **Cơ chế:** Đơn vị đo lường y khoa phát âm ngắn và dính liền với con số.
*   **Ví dụ:** "mi-li-gam" (mg) nhầm với "mi-crô-gam" (mcg) tạo sai lệch 1000 lần. "Huyết áp một trăm hai" -> ASR: "Huyết áp 102" thay vì 120.

### 4. Lược bỏ hoặc Xuyên tạc Từ Phủ định (Negation Loss/Inversion)
*   **Cơ chế:** Các từ phủ định "không", "chưa", "hết" mang âm tiết nhẹ, không trọng âm, dễ chìm vào tiếng ồn. Mô hình xác suất ASR có xu hướng lược bỏ để làm câu mượt hơn.
*   **Ví dụ:** "Bệnh nhân này không có tiền sử dị ứng thuốc" -> ASR: "Bệnh nhân này có tiền sử dị ứng thuốc" (Thay đổi hoàn toàn phác đồ).

### 5. Thiếu sót Thông tin Dị ứng (Allergy Omission)
*   **Cơ chế:** Thông tin này thường được bệnh nhân nói ngắt quãng, giọng nhỏ.
*   **Ví dụ:** "Dạ tôi hay mẩn ngứa khi ăn tôm cua" -> ASR bỏ qua hoàn toàn do tạp âm phòng khám.

### 6. Nhầm lẫn Tên Xét nghiệm (Lab Test Confusion)
*   **Cơ chế:** Đọc bằng chữ cái tiếng Anh đánh vần kiểu tiếng Việt/Pháp.
*   **Ví dụ:** "HbA1c" ("Hát bê a một xê") -> ASR: "Hát bài a một xe". Tương tự với AST, ALT, GGT.

### 7. Lỗi Viết tắt (Abbreviation Errors)
*   **Cơ chế:** Đọc tắt hội chứng/thủ thuật, gây mâu thuẫn âm thanh và văn bản chuẩn.
*   **Ví dụ:** Đái tháo đường ("Đê Tê Đê") -> ASR: "Để tại đó". Huyết áp ("HA") -> ASR: "Hát a".

### 8. Hiện tượng Từ Đồng âm / Gần âm (Homophones)
*   **Cơ chế:** Tiếng Việt có 6 thanh điệu, cao độ biến thiên do micro gây sai lệch nghĩa toàn diện.
*   **Ví dụ:** "Viêm gan" và "Viêm nang"; "Máu" (Blood) và "Cáu" (Angry).

### 9. Chuyển mã Tiếng Anh - Tiếng Việt (Code-switching)
*   **Cơ chế:** Từ vựng tiếng Anh chèn vào cú pháp tiếng Việt gây đứt gãy mô hình phân phối ngôn ngữ.
*   **Ví dụ:** "đi chụp CT scan abdomen" -> ASR (thuần Việt): "đi chụp xi ti xì can áp đô men".

### 10. Phương ngữ Vùng miền (Regional Accents)
*   **Cơ chế:** Biến âm hệ thống ở các phương ngữ (v/d/gi, s/x, tr/ch, l/n, c/t, n/ng).
*   **Ví dụ:** Nam bộ: "Dạ dày" -> "Yạ yày". Bắc bộ: "Viêm loét" -> "Viêm noét".

### 11. Nhiễu nền và Nói chồng lấp (Background noise & Overlapping speech)
*   **Cơ chế:** Gây nhiễu loạn cơ chế Attention của Transformer, chèn thêm ký tự vô nghĩa hoặc lặp từ liên tục (hallucination loops).

### 12. Sự cố Phân tách Người nói (Speaker Diarization Issues)
*   **Cơ chế:** ASR gộp chung câu nói của bác sĩ và bệnh nhân.
*   **Ví dụ:** Bác sĩ: "Mẹ anh bị ung thư không?" - Bệnh nhân: "Có" -> ASR gộp: "Bệnh nhân có ung thư" (Nhầm Tiền sử gia đình thành Tiền sử bản thân).
