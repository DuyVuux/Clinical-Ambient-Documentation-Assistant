# 07_failure_modes_and_error_taxonomy_mvp.md

## Mục tiêu file
Taxonomy lỗi dùng để chấm MVP.

## Error Severity

### Critical Error
Could plausibly cause direct patient harm if accepted into final note.

Examples:
- wrong medication;
- wrong dosage;
- wrong allergy;
- reversed dangerous negation;
- invented treatment plan;
- omitted red flag;
- invented lab value;
- wrong patient/speaker source for plan.

### Major Error
Clinically important and must be fixed, but less directly dangerous.

Examples:
- omitted important symptom;
- diagnosis certainty exaggerated;
- relevant history placed in wrong timeline;
- assessment unsupported but flagged;
- SOAP section misclassification affecting interpretation.

### Minor Error
Formatting, wording, grammar, or non-critical style issues.

Examples:
- awkward phrase;
- repeated text;
- minor section formatting;
- non-clinical spelling issue.

## Error Types

### E01 - Hallucination
AI creates information not found in transcript.

### E02 - Omission
AI misses clinically relevant information.

### E03 - Medication Error
Wrong medication, route, dose, frequency, or duration.

### E04 - Allergy Error
Allergy missing, wrong, or reversed.

### E05 - Negation Error
"Không" / "chưa" / "phủ nhận" is removed, reversed, or weakened.

### E06 - Speaker Attribution Error
Fact assigned to wrong speaker role.

### E07 - Plan Attribution Error
Plan/order created from non-doctor speech.

### E08 - Over-Certainty
AI changes uncertain clinical language into confirmed diagnosis.

Example:
Doctor: "nghi ngờ viêm dạ dày"
AI: "chẩn đoán viêm dạ dày"

### E09 - Temporal Confusion
Past history is written as current symptom, or current symptom becomes past history.

### E10 - SOAP Section Misclassification
Fact is placed in wrong SOAP section.

### E11 - Over-Summarization
AI compresses important clinical timeline or details too aggressively.

### E12 - Code-Switching / Language Error
ASR/NLP fails when transcript contains mixed language or medical English terms.

## Required Error Record
{
  "case_id": "string",
  "error_id": "string",
  "error_type": "E01-Hallucination | E02-Omission | ...",
  "severity": "minor | major | critical",
  "note_section": "Subjective | Objective | Assessment | Plan | Checklist",
  "generated_text": "string",
  "source_quote": "string or null",
  "expected_text": "string or null",
  "reviewer_comment": "string",
  "requires_fix": true
}