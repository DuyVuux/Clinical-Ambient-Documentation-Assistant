# Phân loại Lỗi ASR Lâm sàng (Medical ASR Error Taxonomy v0.1)

## 1. Mục đích (Context & Purpose)
Trong môi trường y tế, một lỗi nhận dạng giọng nói (ASR) nhỏ có thể dẫn đến sai lệch lớn trong phác đồ điều trị và gây nguy hiểm cho bệnh nhân. 
Tài liệu này định nghĩa hệ thống phân loại lỗi ASR dựa trên rủi ro lâm sàng, ưu tiên đánh giá độ an toàn (Clinical Safety) thay vì chỉ nhìn vào chỉ số WER (Word Error Rate) truyền thống. 

**Nguyên tắc cốt lõi:** Các lỗi mức độ `Critical` và `High` có trọng số rủi ro cao hơn nhiều so với Average WER. Việc một mô hình có WER 15% nhưng hay bỏ sót từ "không" nguy hiểm hơn một mô hình WER 25% nhưng bảo toàn được các thực thể y tế.

## 2. Các nhóm lỗi cốt lõi (Core Error Groups)

| Nhóm lỗi (Error Group) | Ý nghĩa (Meaning) | Ví dụ (Reference → Prediction) | Mức độ (Severity) |
|---|---|---|---|
| **negation_deletion** | Bỏ sót từ phủ định (rất nguy hiểm) | "bệnh nhân **không** đau ngực" → "bệnh nhân đau ngực" | **Critical** |
| **negation_hallucination**| Tự tạo ra từ phủ định | "tôi bị dị ứng tôm" → "tôi **không** bị dị ứng tôm" | **Critical** |
| **allergy_error** | Bỏ sót/sai thông tin dị ứng | "tiền sử dị ứng **penicillin**" → "tiền sử dị ứng" | **Critical** |
| **medication_substitution**| Sai tên thuốc (dễ nhầm âm) | "uống **amlodipine**" → "uống **ampicillin**" | **High** |
| **dose_unit_error** | Sai liều lượng hoặc đơn vị đo | "uống **500 mg**" → "uống **50 mg**" | **High** |
| **symptom_deletion** | Bỏ sót triệu chứng quan trọng | "sáng nay **khó thở** nhiều" → "sáng nay nhiều" | **High** |
| **condition_substitution**| Nhận diện sai tên bệnh lý | "bị **đái tháo đường**" → "bị **đau thái dương**" | **High** |
| **insertion_hallucination**| Ảo giác: Tự thêm bệnh/thuốc không có trong audio | "chào bác sĩ" → "chào bác sĩ tôi bị **ung thư**" | **High** |
| **numeric_error** | Sai lệch chỉ số sinh tồn/xét nghiệm | "nhiệt độ **37.8** độ" → "nhiệt độ **38.7** độ" | **Moderate/High** |
| **temporal_error** | Sai mốc thời gian/thời lượng bệnh | "đau bụng **3 ngày** nay" → "đau bụng **vài ngày** nay" | **Moderate** |
| **dialect_term_error** | Sai do phương ngữ/tiếng lóng y khoa | "đau nhức **mình mẩy**" → "đau nhức **mây mẩy**" | **Moderate** |

## 3. Định nghĩa Mức độ Nghiêm trọng (Severity Levels)

- **CRITICAL (Nghiêm trọng):** Lỗi thay đổi hoàn toàn chẩn đoán, chống chỉ định, hoặc phác đồ cấp cứu. Có nguy cơ trực tiếp gây tử vong hoặc tổn hại nặng nề cho bệnh nhân nếu bác sĩ không kiểm tra lại. *(Yêu cầu: Zero Tolerance đối với hệ thống tự động, phải có chốt chặn kiểm tra kép).*
- **HIGH (Cao):** Lỗi dẫn đến kê sai thuốc, sai liều lượng, hoặc bỏ sót triệu chứng chính. Có thể gây ảnh hưởng xấu đến quá trình điều trị. *(Yêu cầu: Bắt buộc Highlight cảnh báo cho Bác sĩ trong vòng lặp Human-in-the-loop).*
- **MODERATE (Trung bình):** Lỗi làm sai lệch thông tin thứ yếu (mốc thời gian tương đối, chỉ số sai lệch nhẹ không vượt ngưỡng nguy hiểm). *(Yêu cầu: Chấp nhận được trong bản nháp, bác sĩ sẽ tự chỉnh sửa).*
- **LOW (Thấp):** Lỗi chính tả, lỗi từ nối không làm thay đổi ý nghĩa y khoa (VD: "bác sĩ" → "bác sỹ", "bệnh nhân" → "người bệnh"). *(Yêu cầu: Được phép bỏ qua trong quá trình phân tích lâm sàng).*

## 4. Khuyến nghị Kỹ thuật (Engineering Recommendations)
Để giảm thiểu các lỗi Critical và High, kiến trúc của Clinical Ambient Documentation cần tích hợp các chốt chặn sau:
1. **Context-Aware Post-Processing (LLM):** Sử dụng một LLM (ví dụ: mô hình ngôn ngữ lớn chuyên ngành y) để dò lỗi ngữ cảnh, so khớp lại với bản nháp SOAP Note để phát hiện ảo giác (hallucination) hoặc mâu thuẫn (contradiction) trong phủ định.
2. **Dictionary Enforcing (Tries/Regex):** Xây dựng bộ từ điển tĩnh (Static Lexicon) cho tên các loại thuốc (Medications) và danh mục bệnh ICD-10 nhằm bảo vệ tính nguyên vẹn của từ khóa trong quá trình text normalization.
3. **Audio-Text Anchoring:** Giao diện người dùng (UI) cần cho phép bác sĩ nhấn vào các danh từ y khoa được in đậm để nghe lại đúng đoạn audio gốc (Timestamp alignment) nhằm tự xác minh liều lượng thuốc.