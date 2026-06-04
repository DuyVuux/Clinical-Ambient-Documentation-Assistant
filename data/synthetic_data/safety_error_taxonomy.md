# Safety Error Taxonomy v0.1

## Required safety groups

### 1. Negation Error
Model làm mất hoặc đảo nghĩa phủ định.

Example:
Gold: "không đau ngực"
Wrong: "đau ngực"

### 2. Allergy Error
Model bỏ sót, thêm sai hoặc đảo nghĩa dị ứng.

Example:
Gold: "dị ứng penicillin"
Wrong: "không dị ứng thuốc"

### 3. Medication Dose Error
Model sai thuốc, sai liều, sai tần suất.

Example:
Gold: "amlodipine 5mg mỗi sáng"
Wrong: "amlodipine 50mg mỗi sáng"

### 4. Source Attribution Error
Claim trong SOAP không link đúng segment.

Example:
Claim: "Bệnh nhân khó thở"
Source segment lại là câu bác sĩ hỏi.

### 5. Temporal Error
Model sai thời gian, onset, duration hoặc frequency.

Example:
Gold: "đau đầu 3 ngày"
Wrong: "đau đầu 3 tháng"

### 6. Speaker Attribution Error
Model nhầm người nói hoặc nhầm vai trò.

Example:
Doctor: "Anh có dị ứng penicillin không?"
Wrong summary: "Bệnh nhân dị ứng penicillin"

### 7. Missing Critical Finding
Transcript có finding quan trọng nhưng summary bỏ mất.

Example:
Gold: "không khó thở"
Wrong summary: bỏ hoàn toàn câu này.

### 8. Unit / Numeric Error
Model sai số, đơn vị hoặc liều lượng.

Example:
Gold: "5 mg"
Wrong: "50 mg"
Gold: "1 viên"
Wrong: "10 viên"