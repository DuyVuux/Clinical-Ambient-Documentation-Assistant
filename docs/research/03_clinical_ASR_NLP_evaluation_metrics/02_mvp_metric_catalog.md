## Mục tiêu file
Danh mục metric chính thức cho intern MVP.

## Metric Groups

### A. ASR Metrics

#### WER - Word Error Rate
Generic word-level error rate.
Useful for baseline only.
Not sufficient for clinical safety.

#### CharER - Character Error Rate
Character-level error rate.
Useful for Vietnamese accents, spelling, and diacritics.
Do not confuse with Captured Entity Rate.

#### mWER - Medical Word Error Rate
Error rate calculated only on clinically important terms:
- symptoms;
- medications;
- dosage;
- frequency;
- allergies;
- lab names;
- lab values;
- diagnoses;
- red flags;
- negations.

MVP Target:
- Internship MVP: track and report.
- Good demo target: mWER < 20%.
- Strong target: mWER < 15%.

#### Medical Word Hit Rate
Percentage of medical terms correctly captured.

Formula:
Medical Word Hit Rate = Correct Medical Terms / Total Medical Terms

MVP Target:
- >= 80% for synthetic cases.
- >= 90% is strong.

#### Negation Error Rate
Measures incorrect handling of:
- không;
- chưa;
- không ghi nhận;
- phủ nhận;
- không dị ứng;
- không đau ngực;
- không sốt.

Critical cases:
Any negation reversal involving red flags, allergy, medication, chest pain, dyspnea, bleeding, pregnancy, or severe symptoms is a major error.

#### Critical Entity Error Rate
Tracks errors involving:
- medication name;
- dosage;
- frequency;
- allergy;
- red flag symptom;
- lab value;
- diagnosis mention;
- plan/order.

MVP Target:
- 0 unflagged critical errors in demo cases.

---

### B. Speaker Metrics

#### Speaker Attribution Accuracy
Percentage of clinical facts assigned to correct speaker role:
- Doctor
- Patient
- Caregiver
- Nurse
- Other
- Unknown

MVP Target:
- >= 90% for manually tagged transcripts.
- Unknown speaker must require review.

#### DER - Diarization Error Rate
Use only if automated diarization is implemented.
Measures speaker segmentation errors over time.

MVP Target:
- Track if available.
- If unavailable, use manually speaker-tagged transcript fallback.

#### Plan Attribution Error
Occurs when the system writes a Plan item from non-doctor speech.

Example:
[Nurse] Có cần tăng liều không bác sĩ?
Wrong output:
Plan: tăng liều.

MVP Target:
- 0 plan-from-non-doctor errors.

---

### C. Clinical Fact Extraction Metrics

#### Captured Entity Rate
Percentage of expected clinical entities that were extracted.

Formula:
Captured Entity Rate = Correctly Extracted Expected Entities / Total Expected Entities

MVP Target:
- >= 80% minimum.
- >= 85% good.
- >= 90% strong.

#### Accurate Entity Rate
Percentage of extracted entities that are correct and supported by transcript.

Formula:
Accurate Entity Rate = Correct Supported Extracted Entities / Total Extracted Entities

MVP Target:
- >= 90% minimum.
- >= 95% strong.

#### Unsupported Fact Count
Number of facts generated without source evidence.

MVP Target:
- 0 unsupported critical facts.
- Unsupported non-critical facts must be marked and fixed.

#### Source Attribution Completeness
Percentage of clinical facts with:
- source quote;
- speaker;
- timestamp if available;
- note section;
- confidence or uncertainty label.

MVP Target:
- 100% for all extracted facts.

---

### D. SOAP Note Metrics

#### SOAP Section Classification Accuracy
Measures whether facts are placed in correct section:
- Subjective
- Objective
- Assessment
- Plan

MVP Target:
- >= 90%.

#### Hallucination Rate
Percentage of SOAP note facts not supported by transcript or extracted facts.

MVP Target:
- 0 critical hallucinations.
- Track all hallucinations.

#### Omission Rate
Percentage of important expected facts missing from SOAP note.

MVP Target:
- No omitted red flags, allergy statements, medication, dosage, or major symptoms.

#### Major Defect-Free Rate
Percentage of evaluated note items without major errors.

MVP Target:
- >= 90% in synthetic demo cases.

#### Critical Defect-Free Rate
Percentage of evaluated note items without critical dangerous errors.

MVP Target:
- 100% in synthetic demo cases.

---

### E. Doctor Review Metrics

#### Edit Distance
Character or word-level difference between AI draft and doctor-edited note.

Use:
- estimate doctor correction burden;
- compare prompts or model versions;
- detect sections that need improvement.

#### Minimally-Edited Note Rate
Percentage of notes where doctor changes less than 10% of text.

MVP Target:
- >= 50% for early demo.
- >= 70% strong intern MVP.

#### Time to Review
Time from opening SOAP draft to confirm/reject.

MVP Target:
- Track only.
- Do not overclaim time saved.

#### Note Usable After Light Edits
Human reviewer marks whether note was usable after light edits.

MVP Target:
- >= 50–60% for intern demo.
- >= 70% strong.

#### Doctor Trust / Usability
For intern MVP, use simple 1–5 rating:
- accuracy;
- usefulness;
- review effort;
- trust;
- would use again.

Optional:
Use SUS if there are enough reviewers.