## Mục tiêu file
Danh sách yêu cầu an toàn bắt buộc cho MVP intern.

## Must-Have Safety Requirements

### SR-01: Draft-only state
All AI-generated notes must start with status = "draft".
The system must display "AI-generated draft. Doctor review required."

Allowed statuses:
- draft
- edited
- rejected
- confirmed

Only doctor action can change status to confirmed.

### SR-02: No autonomous diagnosis
The AI must not create a diagnosis unless it is clearly mentioned by the doctor or marked as "diagnosis mention / requires confirmation".

Bad:
"Chẩn đoán: viêm dạ dày."

Acceptable:
"Assessment: Bác sĩ có nhắc khả năng viêm dạ dày. Requires doctor confirmation."

### SR-03: No autonomous prescribing
The AI must not create medication, dosage, route, or frequency unless explicitly present in transcript and attributed to doctor.

Bad:
"Cho omeprazole 20mg ngày 1 viên."

Acceptable:
"Plan: Medication mentioned but dosage/frequency requires doctor confirmation."

### SR-04: Mandatory doctor confirmation
The UI must require explicit confirmation before finalizing the note.

At minimum, doctor must check:
- allergy;
- medication and dosage;
- diagnosis/assessment;
- plan/order;
- important negations;
- red flags.

### SR-05: Source traceability
Each clinical fact must link back to source transcript.

Minimum source fields:
- transcript_quote;
- speaker;
- timestamp;
- confidence.

### SR-06: Safety flags
The system must generate safety flags for:
- missing allergy;
- uncertain medication;
- uncertain dosage;
- negation conflict;
- unknown speaker;
- low ASR confidence around critical entity;
- plan from non-doctor;
- diagnosis not clearly confirmed by doctor;
- missing vitals;
- missing lab value;
- red flag symptom.

### SR-07: Input quality gate
If audio/transcript quality is poor, the system must warn the user.

For intern MVP:
- If no ASR confidence is available, allow manual "low_quality_input" flag.
- If transcript is too short or contains many "[unclear]" segments, warn doctor.
- If critical entities appear near unclear text, require confirmation.

### SR-08: Audit log
The system must log key lifecycle events:
- session_created;
- transcript_uploaded_or_generated;
- clinical_facts_extracted;
- safety_flags_generated;
- soap_draft_generated;
- doctor_edited_note;
- doctor_rejected_note;
- doctor_confirmed_note;
- session_deleted.

For intern MVP, append-only local JSONL log is acceptable.

### SR-09: Error feedback
Doctor reviewer must be able to flag errors:
- hallucination;
- omission;
- wrong medication;
- wrong dosage;
- wrong allergy;
- wrong negation;
- wrong speaker attribution;
- unsafe plan.

### SR-10: No direct EHR write
For intern MVP, there is no EHR/HIS write.
Export is allowed only as:
- Markdown;
- JSON;
- PDF/HTML demo;
- copied draft after doctor confirmation.

## Should-Have Safety Requirements

### SR-11: Highlight uncertain text
Uncertain facts should be visually marked.

Suggested labels:
- LOW_CONFIDENCE
- NEEDS_CONFIRMATION
- SOURCE_MISSING
- SPEAKER_UNKNOWN
- CRITICAL_ENTITY

### SR-12: Edit distance tracking
Calculate how much doctor edits the AI draft.

Track:
- original_ai_draft;
- doctor_edited_draft;
- character_edit_distance;
- sections most edited.

### SR-13: Basic red-team cases
Test the MVP with cases containing:
- negation;
- medication/dosage;
- allergy;
- caregiver speaker;
- nurse question;
- noisy transcript;
- missing vitals;
- red flag symptom.

## Not Allowed in MVP

- Autonomous diagnosis.
- Autonomous prescribing.
- Automatic ICD-10 coding as final diagnosis.
- Direct EHR write.
- One-click approve without review.
- Hidden AI-generated status.
- Removing source transcript.
- Using real patient data by default.