## Mục tiêu file
CREOLA-lite taxonomy để đánh giá lỗi lâm sàng trong MVP intern.

## Severity Levels

### Major Error
An error that could plausibly affect patient safety, clinical decision-making, medication, follow-up, or legal medical record quality.

Examples:
- wrong medication;
- wrong dosage;
- wrong allergy;
- reversed negation;
- omitted red flag;
- invented diagnosis;
- invented test result;
- plan/order not spoken by doctor;
- wrong patient/source attribution.

### Minor Error
An error that affects style, wording, formatting, or non-critical completeness but is unlikely to cause harm.

Examples:
- awkward wording;
- repeated phrase;
- minor grammar issue;
- non-critical detail phrased poorly.

## Error Types

### E01: Fabrication
AI creates information not present in transcript.

Example:
Transcript: no blood pressure mentioned.
AI note: "BP 120/80 mmHg."

### E02: Negation Error
AI reverses or weakens a negation.

Example:
Transcript: "Không đau ngực."
AI note: "Có đau ngực."

### E03: Assumed Causality
AI invents causal relationship.

Example:
Transcript: patient has headache and changed diet.
AI note: "Headache due to diet change."

### E04: Context Conflation
AI mixes information between people or sections.

Example:
Caregiver's medication becomes patient's medication.

### E05: Omission
AI omits clinically important information.

Examples:
- omitted allergy;
- omitted medication;
- omitted red flag symptom;
- omitted follow-up instruction.

### E06: Medication Error
Wrong medication name, wrong route, wrong frequency, or wrong dose.

### E07: Allergy Error
Missing, wrong, or reversed allergy information.

### E08: Speaker Attribution Error
Fact is assigned to wrong speaker.

Example:
Nurse asks "Có tăng liều không?"
AI writes "Plan: tăng liều."

### E09: Unsupported Assessment
Assessment appears without doctor source or clear evidence.

### E10: Unsafe Plan
Plan contains treatment instruction not confirmed by doctor.

## Evaluation Fields
Each error record should include:
- case_id
- note_section
- generated_text
- source_quote
- error_type
- severity
- reviewer_comment
- requires_fix