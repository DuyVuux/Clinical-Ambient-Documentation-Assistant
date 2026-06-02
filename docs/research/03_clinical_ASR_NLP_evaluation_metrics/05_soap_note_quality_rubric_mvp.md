## Mục tiêu file
Rubric chấm SOAP/outpatient note draft cho intern MVP.

## Scoring Method
For each SOAP draft, reviewer gives section-level scores from 1 to 5.

1 = unsafe/unusable
2 = major corrections required
3 = usable with moderate corrections
4 = usable with light edits
5 = clinically clear and well structured

## Sections

### S - Subjective
Check:
- symptoms captured;
- duration captured;
- relevant history captured;
- patient/caregiver source preserved;
- negations preserved;
- allergy/medication history handled safely.

Major errors:
- missing main symptom;
- reversed negation;
- caregiver statement treated as confirmed diagnosis;
- allergy omitted or reversed.

### O - Objective
Check:
- vitals only included if mentioned;
- labs only included if mentioned;
- exam findings only included if doctor mentioned;
- missing objective data marked as "Not mentioned in transcript."

Major errors:
- invented vitals;
- invented physical exam;
- invented lab results.

### A - Assessment
Check:
- assessment/diagnosis only included if doctor mentioned or clearly marked as uncertain;
- diagnostic certainty is not exaggerated;
- "nghi ngờ", "theo dõi", "cân nhắc" are preserved.

Major errors:
- invented diagnosis;
- uncertain diagnosis written as confirmed;
- AI-created ICD-10-style diagnosis without source.

### P - Plan
Check:
- plan/order comes from doctor;
- medications/dosages are accurate or flagged;
- follow-up instructions captured;
- red flags captured if mentioned;
- non-doctor questions are not turned into orders.

Major errors:
- invented prescription;
- wrong dose/frequency;
- nurse/caregiver question turned into plan;
- follow-up warning omitted.

## Overall Note Quality
Use:
- Accuracy
- Completeness
- Organization
- Conciseness
- Internal consistency
- Safety flag adequacy
- Source traceability

## MVP Note Quality Target
A demo case passes if:
- no critical errors;
- all high-risk entities flagged;
- every clinical fact has source evidence;
- note is usable after light or moderate edits;
- doctor confirmation is required.