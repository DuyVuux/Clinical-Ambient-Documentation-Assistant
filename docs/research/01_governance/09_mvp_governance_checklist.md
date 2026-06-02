## Mục tiêu file
Checklist trước khi demo MVP.

## Scope Checklist
- [ ] MVP chỉ làm outpatient.
- [ ] Không gọi sản phẩm là AI Doctor.
- [ ] Không có auto diagnosis.
- [ ] Không có auto prescription.
- [ ] Không có final note nếu chưa doctor confirm.
- [ ] Không yêu cầu HIS/EHR integration.
- [ ] Không yêu cầu realtime.

## Data Checklist
- [ ] Demo dùng synthetic/actor data.
- [ ] Không có tên bệnh nhân thật.
- [ ] Không có số điện thoại thật.
- [ ] Không có địa chỉ thật.
- [ ] Không có mã bệnh nhân thật.
- [ ] Không có đơn thuốc/hồ sơ thật.
- [ ] Có nút xóa session.
- [ ] Có chính sách không đưa real patient data lên cloud.

## Pipeline Checklist
- [ ] Có audio hoặc transcript input.
- [ ] Có transcript output.
- [ ] Có speaker role hoặc fallback manual speaker tag.
- [ ] Có clinical facts JSON.
- [ ] Mỗi fact có source attribution.
- [ ] Có SOAP draft.
- [ ] Có safety checklist.
- [ ] Có doctor review action.

## Safety Checklist
- [ ] Missing allergy được flag.
- [ ] Medication/dosage uncertain được flag.
- [ ] Negation quan trọng được giữ đúng.
- [ ] Unknown speaker requires review.
- [ ] Plan từ non-doctor không tự đưa vào Plan.
- [ ] Missing vitals/test results không bị bịa.
- [ ] Assessment/diagnosis chưa chắc được đánh dấu requires confirmation.

## Audit Checklist
- [ ] Log session_created.
- [ ] Log transcript_generated.
- [ ] Log facts_extracted.
- [ ] Log soap_draft_generated.
- [ ] Log doctor_edited_note.
- [ ] Log doctor_confirmed_note.
- [ ] Log audio_deleted/session_deleted.
- [ ] Audit log không chứa full PHI.

## Final Demo Checklist
- [ ] Có 3 case demo.
- [ ] Case 1: note bình thường, dùng được sau chỉnh nhẹ.
- [ ] Case 2: thiếu thông tin, AI biết báo thiếu.
- [ ] Case 3: có thuốc/liều/dị ứng/phủ định, AI flag đúng.
- [ ] Có báo cáo limitation.
- [ ] Có thông báo rõ: AI draft only, doctor confirmation required.