# Kết quả Kiểm tra Thủ công (Manual Inspection Results)

**Hướng dẫn điền:**
Lấy file `[tên_sample]_original.wav` làm chuẩn gốc. Nghe và so sánh file `[tên_sample]_p03_selected.wav` với file gốc, sau đó điền vào bảng dưới đây.

**Các tiêu chí đánh giá:**
*   **A:** `p03` có mất âm đầu không? *(Có / Không)*
*   **B:** `p03` có mất âm cuối không? *(Có / Không)*
*   **C:** `p03` có mất từ y khoa/negation/số/liều không? *(Có / Không)*
*   **D:** `p03` có cắt mất khoảng thở tự nhiên nhưng không ảnh hưởng speech không? *(Có / Không)*
*   **E:** `p03` nghe rõ hơn, tương đương, hay tệ hơn original? *(Rõ hơn / Tương đương / Tệ hơn)*

---

### Tập dữ liệu: Train

| Sample ID | A. Mất âm đầu? | B. Mất âm cuối? | C. Mất từ quan trọng? | D. Cắt khoảng thở (tốt)? | E. Chất lượng so với gốc? | Ghi chú thêm (nếu có) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `public_vietmed_0007` |Không |Có |Không |Có |Tương đương|Mất từ 'nhưng' ở cuối câu, nhưng tôi nghe được nội dung lại có thêm từ 'mà', nguyên mẫu như sau :"giận nó hay đau mà đau cả cả ngày đêm" |
| `public_vietmed_0152` |Không |Có | Mất 4 từ cuối |Có |Tương đương|Mất 4 từ cuối cùng 'ngày được phát vào', chữ 'ngày' bị mất chỉ nghe thấy âm của chữ 'ng'|
| `public_vietmed_0176` |Có |Không |Không |Có | Tốt hơn vì cắt khoảng thở cuối câu hiệu quả| Trong file json nguyên mẫu là 'còn phục hồi sụn khớp thoái hóa hiệu quả cứ mười người dùng thì chín người thấy hiệu quả', tuy nhiên ở đầu câu tôi còn nghe được từ 'mà', nghĩa là 'mà còn phục hồi sụn khớp thoái hóa hiệu quả cứ mười người dùng thì chín người thấy hiệu quả' |
| `public_vietmed_0547` |Không |Có |Không |Có |Tót hơn vì cắt khỏang thở ở đầu câu hiệu quả |Mất từ 'mình' ở cuối câu, tôi chỉ nghe thấy 'vâng thế và cái hiện tượng mà cái bàn tay mình' |
| `public_vietmed_0894` |Có |Không |Có |Chỉ tốt hơn original chứ không tốt |Chỉ tốt hơn original chứ không tốt | Mất từ 'hiểu' ở phần đầu của câu, nguyên mẫu là 'hiểu ở phần đầu chương trình ngay sau đây', tuy nhiên ở câu đầu tôi chỉ nghe được 'ở phần đầu chương trình ngay sau đây'. Bên cạnh đó nội dung ở phần cuối của file có 1 đoạn tiếng xoẹt qua để chuyển cảnh nhưng sau đó có khỏang lặng khá lớn, file p03 có cắt nhưng vẫn còn giữ lại khoảng lặng khá dài |
| `public_vietmed_0972` |Có |Không |Tôi nghĩ là có, từ mất là từ 'suốt' trong cụm 'suốt cuộc đời' |Không khác bản gốc mấy |Không khác bản gốc mấy |Phẩn khoảng lặng ở cuối câu vẫn bị kéo dài, tôi thấy khá dài |
---

### Tập dữ liệu: Dev

| Sample ID | A. Mất âm đầu? | B. Mất âm cuối? | C. Mất từ quan trọng? | D. Cắt khoảng thở (tốt)? | E. Chất lượng so với gốc? | Ghi chú thêm (nếu có) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `public_vietmed_0483` |Không |Không |Không |Có |Tốt hơn nhiều, quá tốt | |

---

### Kết luận chung
*(Sau khi nghe xong tất cả, bạn có thể ghi tóm tắt đánh giá về pipeline `p03_selected` tại đây)*

*   **Nhận xét:**
