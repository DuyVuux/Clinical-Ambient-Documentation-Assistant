# ASR Medical Error Analysis — hynt/Zipformer-30M-RNNT-6000h

## Summary

- Samples: 200
- Samples with critical/high missing error: 7

## Group summary

| Group | Severity | Ref samples | Missing samples | Missing total | Inserted samples | Inserted total |
|---|---|---:|---:|---:|---:|---:|
| negation | critical | 52 | 6 | 7 | 0 | 0 |
| symptom | moderate | 61 | 7 | 7 | 8 | 8 |
| medication | high | 0 | 0 | 0 | 0 | 0 |
| allergy | critical | 0 | 0 | 0 | 0 | 0 |
| dose_unit | high | 6 | 1 | 1 | 3 | 3 |
| number | moderate | 0 | 0 | 0 | 0 | 0 |
| red_flag | high | 0 | 0 | 0 | 0 | 0 |

## Top missing terms

### negation
- `không`: 5
- `không có`: 2

### symptom
- `ho`: 7

### medication
- None

### allergy
- None

### dose_unit
- `ngày`: 1

### number
- None

### red_flag
- None

## Critical/high examples

### public_vietmed_0495

**Reference:** xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không

**Prediction:** NGÀY XƯA CÁI ĐÔI TAY CỦA MÌNH VÀ CÁI VAI CỦA MÌNH NÓ ĐAU ĐỚN THẾ NÀO THÌ BÂY GIỜ NÓ

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0062

**Reference:** thông dụng thôi nhưng mà mọi người nên để ý để tránh cái tình trạng là các cái tác động nó cứ tích lũy ngày một ngày

**Prediction:** NÓ RẤT LÀ THÔNG DỤNG THÔI NHƯNG MÀ MỌI NGƯỜI NÊN ĐỂ Ý ĐỂ TRÁNH CÁI TÌNH TRẠNG LÀ CÁC CÁI TÁC ĐỘNG NÓ CỨ TÍCH

**Flags:**
- dose_unit (high): missing ['ngày']

### public_vietmed_0273

**Reference:** trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bệnh cao tuổi đúng không ạ

**Prediction:** HỎI ĐẾN CHƯƠNG TRÌNH VÀ CHÚC BÁC THẬT LÀ NHIỀU SỨC KHỎE VÂNG VỪA RỒI THÌ CHÚNG TA THẤY LÀ RẤT LÀ NHIỀU NGƯỜI BỆNH

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0424

**Reference:** hiệu quả nhưng lại tác dụng phụ không có nhiều như vậy không ảnh hưởng đến nội tạng nhiều như vậy và bản thân

**Prediction:** CÓ HIỆU QUẢ NHƯNG LẠI TÁC DỤNG PHỤ KHÔNG NÓ NHIỀU NHƯ VẬY KHÔNG ẢNH HƯỞNG ĐẾN NỘI TẠNG NHIỀU NHƯ VẬY VÀ BẢN THÂN

**Flags:**
- negation (critical): missing ['không có']

### public_vietmed_0431

**Reference:** này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình không hai

**Prediction:** CÁI MÃ NÀY CHÚNG TA SẼ CÓ THỂ CÓ THÔNG TIN VỀ SẢN PHẨM VÂNG VÀ TÔI CŨNG XIN ĐƯỢC NHẮC LẠI TỔNG ĐÀI CỦA CHƯƠNG TRÌNH

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0919

**Reference:** giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó không có

**Prediction:** GIAI ĐOẠN SAU MƯỜI NĂM CÁI VIỆC MÀ PHẪU THUẬT KÍCH THÍCH NÃO SAU NÓ TRỞ NÊN KÉM HIỆU QUẢ HƠN TUY NHIÊN ĐIỀU

**Flags:**
- negation (critical): missing ['không', 'không có']

### public_vietmed_0325

**Reference:** của chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh của chúng ta chứ không

**Prediction:** CỦA CHÚNG TA THÌ KHI ĐÓ RÕ RÀNG CHÚNG TA BIẾT RẰNG LÀ CHÚNG TA CẦN PHẢI ĐIỀU CHỈNH CÁI BỆNH CỦA CHÚNG TA

**Flags:**
- negation (critical): missing ['không']
