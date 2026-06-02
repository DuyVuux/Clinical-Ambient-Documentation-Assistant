## Mục tiêu file
Mô tả consent/session policy ở mức đủ cho MVP.

## MVP Default
Với synthetic/actor data:
- consent_status = simulated_consent
- không cần lưu chữ ký thật;
- cần hiển thị rõ trong UI: "Demo uses synthetic/actor data only."

## Nếu demo với người thật nhưng không phải bệnh nhân
Ví dụ actor hoặc thành viên team:
- cần verbal consent hoặc written demo consent đơn giản;
- người tham gia biết audio được dùng để test MVP;
- người tham gia có thể yêu cầu xóa audio/session.

## Nếu dùng bệnh nhân thật
Không dùng trong intern MVP nếu chưa được duyệt.
Chỉ được dùng khi có approval đầy đủ.

## Session Metadata Required
Mỗi session cần có:
- session_id
- created_at
- data_type: synthetic | actor | real_patient_approved
- consent_status: simulated_consent | actor_consent | approved_patient_consent | not_allowed
- visit_type: outpatient
- specialty
- created_by
- storage_location
- retention_due_at

## Consent UI Text for MVP
"Đây là bản demo sử dụng dữ liệu giả lập/actor data. Hệ thống không thay thế bác sĩ, không chẩn đoán, không kê đơn. Bản ghi và bản nháp chỉ dùng để kiểm thử quy trình tạo ghi chú khám ngoại trú."

## Patient Data Warning
If data_type = real_patient_approved is not explicitly selected and approved, the system must not label the session as patient data.
