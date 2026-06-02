## Mục tiêu file
Checklist cuối trước khi demo MVP.

## Product Positioning
- [ ] UI không gọi hệ thống là AI Doctor.
- [ ] UI ghi rõ AI-generated draft.
- [ ] UI ghi rõ doctor review required.
- [ ] Không có claim tự động chẩn đoán.
- [ ] Không có claim tự động kê đơn.

## Pipeline Safety
- [ ] Clinical facts có source quote.
- [ ] Clinical facts có speaker.
- [ ] Clinical facts có timestamp nếu có.
- [ ] Clinical facts có confidence hoặc uncertainty label.
- [ ] SOAP draft được render từ facts, không tự bịa.
- [ ] Missing info được ghi là "Not mentioned in transcript."
- [ ] Uncertain info được ghi là "Requires doctor confirmation."

## Doctor Review
- [ ] Có màn hình doctor review.
- [ ] Doctor có thể edit note.
- [ ] Doctor có thể reject note.
- [ ] Doctor có thể confirm note.
- [ ] Confirm button bị chặn nếu còn high-risk flags chưa xử lý.
- [ ] Có checklist thuốc/dị ứng/chẩn đoán/plan/negation/red flags.

## Safety Flags
- [ ] Missing allergy được flag.
- [ ] Uncertain medication được flag.
- [ ] Uncertain dosage được flag.
- [ ] Negation conflict được flag.
- [ ] Unknown speaker được flag.
- [ ] Plan from non-doctor được flag.
- [ ] Low quality input được flag.
- [ ] Unsupported diagnosis được flag.

## Evaluation
- [ ] Có ít nhất 3 demo cases.
- [ ] Có case bình thường.
- [ ] Có case thiếu thông tin.
- [ ] Có case medication/dosage/allergy/negation.
- [ ] Có case nhiều speaker hoặc speaker ambiguity.
- [ ] Có bảng lỗi major/minor.
- [ ] Có ghi nhận hallucination/omission/negation/medication/dosage errors.

## Audit
- [ ] Log session_created.
- [ ] Log facts_extracted.
- [ ] Log safety_flags_generated.
- [ ] Log soap_draft_generated.
- [ ] Log doctor_edited_note.
- [ ] Log doctor_confirmed_note.
- [ ] Log session_deleted.
- [ ] Log không chứa dữ liệu định danh không cần thiết.

## Not Allowed
- [ ] Không direct EHR write.
- [ ] Không autonomous prescribing.
- [ ] Không autonomous diagnosis.
- [ ] Không approve all một chạm mà không review.
- [ ] Không dùng real patient data mặc định.