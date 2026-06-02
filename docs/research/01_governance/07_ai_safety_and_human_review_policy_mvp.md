## Mục tiêu file
Quy định guardrails lâm sàng cho AI trong MVP.

## Core Principle
AI output is a draft only.
Doctor confirmation is mandatory.
The system must never present AI-generated content as final medical truth.

## AI Must Not
- Không chẩn đoán tự động.
- Không kê đơn tự động.
- Không tự tạo thuốc/liều.
- Không tự tạo dị ứng.
- Không tự tạo xét nghiệm.
- Không tự tạo sinh hiệu.
- Không tự suy diễn plan nếu bác sĩ chưa nói rõ.
- Không biến câu hỏi của nurse/caregiver thành y lệnh.

## Required Safety Flags
AI phải flag các trường hợp:
- medication mentioned but uncertain
- dosage mentioned but uncertain
- allergy not mentioned
- allergy negation detected
- conflicting negation
- abnormal symptom/red flag mentioned
- doctor assessment unclear
- plan mentioned by non-doctor
- unknown speaker used for clinical fact
- missing vitals
- missing test result value
- ASR low confidence around critical entity

## Speaker Attribution Rules
Doctor:
- có thể đưa vào Assessment/Plan nếu rõ ràng;
- vẫn cần doctor confirmation.

Patient:
- đưa vào Subjective/history/symptom;
- không dùng làm diagnosis cuối.

Caregiver:
- đưa vào Subjective với source = caregiver;
- cần đánh dấu nguồn thông tin.

Nurse:
- có thể đưa vào context/vitals/care coordination;
- không biến câu hỏi thành plan.

Unknown:
- requires_review = true.

## SOAP Generation Rules
S - Subjective:
- triệu chứng bệnh nhân nói;
- bệnh sử;
- thuốc đang dùng nếu bệnh nhân/caregiver nói;
- dị ứng nếu được đề cập;
- phủ định như "không sốt", "không đau ngực" phải giữ đúng.

O - Objective:
- chỉ ghi sinh hiệu/xét nghiệm/khám thực thể nếu được nói rõ;
- nếu không có, ghi "Not mentioned in transcript."

A - Assessment:
- chỉ ghi nhận định/chẩn đoán nếu doctor nói hoặc transcript có bằng chứng rõ;
- nếu chưa chắc, ghi "Requires doctor confirmation."

P - Plan:
- chỉ ghi plan/order nếu doctor nói rõ;
- thuốc/liều phải flag nếu không chắc;
- không tự kê đơn.

## Required Checklist
Mỗi SOAP draft phải có checklist:
- [ ] Đã xác nhận dị ứng thuốc
- [ ] Đã xác nhận thuốc và liều
- [ ] Đã kiểm tra phủ định quan trọng
- [ ] Đã xác nhận chẩn đoán/nhận định
- [ ] Đã xác nhận plan/order
- [ ] Đã kiểm tra red flags
- [ ] Đã kiểm tra thông tin thiếu