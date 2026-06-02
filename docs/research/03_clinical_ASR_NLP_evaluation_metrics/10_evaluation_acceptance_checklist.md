## Mục tiêu file
Checklist để biết evaluation MVP đã đủ mạnh trước demo.

## Dataset Checklist
- [ ] Có ít nhất 3 synthetic outpatient cases.
- [ ] Có ground truth transcript.
- [ ] Có expected clinical facts.
- [ ] Có expected SOAP draft.
- [ ] Có expected safety flags.
- [ ] Có ít nhất 1 case medication/dosage.
- [ ] Có ít nhất 1 case allergy/negation.
- [ ] Có ít nhất 1 case missing information.
- [ ] Có ít nhất 1 case speaker confusion.
- [ ] Có ít nhất 1 case red flag hoặc critical symptom nếu phù hợp.

## ASR Checklist
- [ ] Có WER nếu dùng ASR.
- [ ] Có CharER nếu dùng ASR.
- [ ] Có mWER.
- [ ] Có Medical Word Hit Rate.
- [ ] Có Negation Error Count.
- [ ] Có Critical Entity Error Count.
- [ ] Nếu không dùng ASR, ghi rõ transcript fallback.

## Clinical Fact Checklist
- [ ] Có Captured Entity Rate.
- [ ] Có Accurate Entity Rate.
- [ ] Có Unsupported Fact Count.
- [ ] Có Source Attribution Completeness.
- [ ] Có Critical Entity Capture Rate.
- [ ] Mọi fact có source_quote.
- [ ] Mọi fact có speaker.
- [ ] Mọi high-risk fact requires_doctor_confirmation = true.

## SOAP Note Checklist
- [ ] Có SOAP Section Classification Accuracy.
- [ ] Có hallucination count.
- [ ] Có omission count.
- [ ] Có major defect count.
- [ ] Có critical defect count.
- [ ] Có kiểm tra over-certainty.
- [ ] Có kiểm tra plan-from-non-doctor.

## Doctor Review Checklist
- [ ] Có edit distance hoặc edit ratio.
- [ ] Có review time nếu UI hỗ trợ.
- [ ] Có usable after light edits.
- [ ] Có doctor error feedback.
- [ ] Có safety flag resolution status.

## Safety Pass Criteria
- [ ] 0 autonomous diagnosis.
- [ ] 0 autonomous prescription.
- [ ] 0 unflagged critical medication/dosage/allergy error.
- [ ] 0 plan-from-non-doctor accepted silently.
- [ ] 100% clinical facts have source attribution.
- [ ] High-risk flags block or require explicit acknowledgment before confirmation.

## Reporting Checklist
- [ ] Không chỉ báo cáo WER.
- [ ] Không dùng ROUGE làm metric chính.
- [ ] Có bảng major/minor/critical errors.
- [ ] Có phần limitations.
- [ ] Có nói rõ dữ liệu là synthetic/actor.
- [ ] Không claim clinical validation.