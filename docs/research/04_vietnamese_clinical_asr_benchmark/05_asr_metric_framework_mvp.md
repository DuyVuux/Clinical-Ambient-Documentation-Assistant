# 05. Khung Đo lường Tiêu chuẩn ASR MVP (ASR Metric Framework MVP)

Sự phụ thuộc quá lớn vào Tỷ lệ Lỗi Từ (WER) là một cái bẫy nguy hiểm trong việc đánh giá ASR y tế. Việc ASR nhận diện đúng 100 từ nhưng sai duy nhất 1 từ "không" (ví dụ: không dị ứng) có thể gây hậu quả chết người. Do đó, hệ thống tài liệu lâm sàng tự động phải được đánh giá thông qua một khung đo lường đa chiều, tập trung vào thực thể (Entity-level).

## 1. Các Thước đo Tổng quát (Dùng để Đối sánh Kỹ thuật)

*   **WER (Word Error Rate - Tỷ lệ Lỗi Từ):**
    *   Công thức: $WER = \frac{S + D + I}{N_{ref}}$ ($S$: Thay thế, $D$: Xóa bỏ, $I$: Chèn thêm, $N$: Tổng số từ gốc).
    *   *Tính hữu dụng:* Chỉ dùng để đánh giá năng lực bắt tiếng Việt tổng quát, **không mang ý nghĩa an toàn lâm sàng**.
*   **CER (Character Error Rate - Tỷ lệ Lỗi Ký tự):**
    *   *Tính hữu dụng:* Quan trọng với ngôn ngữ đơn lập, thanh điệu như tiếng Việt (sai một dấu ngã thành dấu hỏi có thể thay đổi toàn bộ từ vựng).

## 2. Các Thước đo An toàn Lâm sàng (Dùng để Quyết định Triển khai)

Hệ thống đánh giá phải chạy qua một mô hình Trích xuất Thực thể Y tế (Medical NER) để xác định ranh giới các từ khóa y khoa trước khi so khớp chuỗi.

*   **MTER (Medical Term Error Rate - Tỷ lệ Lỗi Thuật ngữ Y khoa):**
    *   Tỷ lệ lỗi chỉ tính trên các từ thuộc bộ từ vựng y khoa danh định ($V_{med}$).
    *   *Tính hữu dụng:* Đánh giá khả năng hiểu thuật ngữ chuyên ngành (thường cao hơn WER từ 1.5 đến 2 lần do phân phối đuôi dài).
*   **CEER (Critical Entity Error Rate - Tỷ lệ Lỗi Thực thể Trọng yếu):**
    *   Một "Thực thể Trọng yếu" ($E_{crit}$) bao gồm: **Tên thuốc, Liều lượng, Tần suất, Đường dùng, và Thông tin dị ứng**.
    *   Công thức: $CEER = \frac{\text{Số thực thể } E_{crit} \text{ bị lỗi}}{\text{Tổng số thực thể } E_{crit} \text{ trong bản Reference}}$.
    *   *Các Metric Phân tách:*
        *   **DNER (Drug Name Error Rate):** Chỉ tính trên Tên thuốc.
        *   **DER (Dosage Error Rate):** Chỉ tính trên Liều lượng (con số và đơn vị).
        *   **LTER (Lab Test Error Rate):** Chỉ tính trên Xét nghiệm/Chỉ số sinh hóa.
*   **NCER (Negation Critical Error Rate - Tỷ lệ Lỗi Phủ định):**
    *   Đánh giá số lỗi Xóa bỏ (bỏ sót từ phủ định "không", "chưa") hoặc Chèn ảo (tự thêm từ phủ định) đứng trước một thực thể bệnh lý.
    *   Đây là một trong những lỗi chí mạng nhất.
*   **Tỷ lệ Bỏ sót (Omission) và Thay thế (Substitution):**
    *   **Omission Rate:** Đánh giá việc ASR "nuốt" mất lời dặn dò quan trọng.
    *   **Substitution Rate:** Đánh giá sự nguy hiểm khi ASR thay thế thuốc này bằng thuốc khác.
*   **Tỷ lệ Ảo giác Y khoa (Medical Hallucination Rate):**
    *   Ảo giác xảy ra khi mô hình ASR tự động bịa ra một thuật ngữ y tế hoặc chẩn đoán không hề tồn tại trong luồng âm thanh gốc.
    *   *Tính hữu dụng:* Nếu tỷ lệ này > 1%, hệ thống phải bị chặn không được đưa vào sản xuất.
*   **SCER (Safety-Critical Error Rate - Tỷ lệ Lỗi Gây nguy hiểm An toàn):**
    *   Thước đo toàn cục: Một hồ sơ bị dán nhãn "Nguy hiểm" nếu chuyên gia y tế xác định rằng sai sót trong bản ASR sẽ dẫn đến hành động y khoa sai lầm gây hại cho bệnh nhân.
