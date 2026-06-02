## Mục tiêu file
Đây là context chính đưa cho AI coding assistant khi build phần safety của MVP.

## Product Identity
Build a local-first Clinical Ambient Documentation Assistant MVP for outpatient visits.

This system is not an AI Doctor.
This system is not a diagnostic system.
This system is not an autonomous prescribing system.
This system is not allowed to finalize or write medical records without doctor confirmation.

The AI only creates a draft clinical note from audio/transcript.
The doctor is always responsible for review, correction, and confirmation.

## Safety Thesis
Do not build this as a simple ASR + LLM wrapper.
Build it as a risk-controlled clinical documentation pipeline.

The pipeline must include:
1. Audio/transcript input.
2. ASR/transcript confidence or quality warning.
3. Speaker/source attribution.
4. Clinical fact extraction.
5. Safety flag generation.
6. SOAP/outpatient draft generation.
7. Doctor review and edit.
8. Explicit doctor confirmation.
9. Audit log.
10. Session deletion.

## Absolute Safety Rules
The system must not:
- diagnose automatically;
- prescribe automatically;
- generate medication/dosage not mentioned in transcript;
- generate allergy status not mentioned in transcript;
- generate vital signs not mentioned in transcript;
- generate lab results not mentioned in transcript;
- convert nurse/caregiver questions into doctor plan;
- write directly into EHR/HIS;
- mark AI draft as final without doctor confirmation;
- hide uncertainty;
- remove important negations.

## Required Behavior
If information is missing, write:
"Not mentioned in transcript."

If information is uncertain, write:
"Requires doctor confirmation."

If speaker is unknown, set:
requires_doctor_confirmation = true.

If audio quality or ASR quality is low, show:
"Low input quality. Doctor must verify transcript before using AI draft."

## High-Risk Clinical Data
Always require doctor confirmation for:
- medication name;
- dosage;
- frequency;
- allergy;
- diagnosis/assessment;
- treatment plan;
- abnormal lab result;
- red flag symptom;
- negation involving dangerous symptoms;
- plan/order from doctor.

## Source Traceability
Every clinical fact must have:
- transcript quote;
- speaker;
- timestamp if available;
- confidence;
- note section;
- requires_doctor_confirmation.

Never generate a clinical fact without source evidence.