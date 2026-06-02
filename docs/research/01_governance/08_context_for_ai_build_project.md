## Mục tiêu file
Đây là file có thể paste trực tiếp vào ChatGPT/Cursor/Claude khi yêu cầu AI build project.

## Build Instruction
You are building an intern MVP for a Local-first Clinical Ambient Documentation Assistant for outpatient visits in Vietnamese.

This system is not an AI Doctor.
It must not diagnose, prescribe, or finalize a medical record automatically.
It creates a draft SOAP/outpatient note from audio/transcript and requires doctor review.

## Functional Requirements
Build a local demo app that supports:
1. Create outpatient demo session.
2. Upload or record synthetic/actor audio.
3. Run ASR or accept pasted transcript for fallback.
4. Segment transcript by speaker if available.
5. Extract clinical facts into JSON.
6. Attach source attribution to every fact.
7. Generate SOAP/outpatient note draft.
8. Generate safety checklist.
9. Allow doctor reviewer to edit, reject, or confirm.
10. Log key audit events.
11. Delete audio or full session.

## Data Requirements
Use local storage only for MVP.
Use synthetic/actor data only by default.
Do not require HIS/EHR integration.
Do not send real patient data to cloud APIs.
Do not store unnecessary PII.

## Required JSON Schema: Clinical Fact
{
  "fact_id": "uuid",
  "session_id": "string",
  "fact_text": "string",
  "fact_type": "symptom | duration | medication | dosage | allergy | vital | lab_test | diagnosis_mention | plan | instruction | red_flag | other",
  "speaker": "Doctor | Patient | Caregiver | Nurse | Other | Unknown",
  "source_timestamp": "start-end or null",
  "transcript_quote": "string",
  "note_section": "Subjective | Objective | Assessment | Plan | Checklist",
  "confidence": 0.0,
  "requires_doctor_confirmation": true,
  "safety_flags": []
}

## Required JSON Schema: Safety Flag
{
  "flag_id": "uuid",
  "session_id": "string",
  "flag_type": "UNCERTAIN_MEDICATION | UNCERTAIN_DOSAGE | MISSING_ALLERGY | NEGATION_CONFLICT | UNKNOWN_SPEAKER | MISSING_VITALS | UNCLEAR_DIAGNOSIS | PLAN_FROM_NON_DOCTOR | LOW_ASR_CONFIDENCE_CRITICAL_ENTITY | OTHER",
  "severity": "low | medium | high",
  "message": "string",
  "related_fact_id": "string or null",
  "requires_doctor_confirmation": true
}

## Required JSON Schema: SOAP Draft
{
  "session_id": "string",
  "subjective": "string",
  "objective": "string",
  "assessment": "string",
  "plan": "string",
  "safety_checklist": [
    {
      "item": "string",
      "status": "unchecked | checked | not_applicable",
      "requires_doctor_confirmation": true
    }
  ],
  "status": "draft | edited | rejected | confirmed",
  "doctor_edits": [],
  "confirmed_at": null
}

## Generation Constraints
When generating notes:
- Do not invent clinical facts.
- Do not invent diagnosis.
- Do not invent medication.
- Do not invent dosage.
- Do not invent allergy.
- Do not invent test result.
- Do not invent vital signs.
- If missing, write "Not mentioned in transcript."
- If uncertain, write "Requires doctor confirmation."
- Keep all critical medication/allergy/dosage/negation issues in safety checklist.

## Recommended MVP Stack
Frontend:
- Streamlit or Gradio for fastest demo.

Backend:
- Python functions or FastAPI if needed.

Storage:
- Local folder + SQLite.
- Store each session under data/sessions/{session_id}/.

ASR:
- Start with faster-whisper or allow transcript paste fallback.
- For demo, transcript paste fallback is acceptable if ASR setup is not stable.

Speaker:
- Support speaker-tagged transcript manually first.
- Example format:
  [Doctor 00:00:01] Hôm nay anh/chị thấy thế nào?
  [Patient 00:00:05] Tôi đau thượng vị 3 ngày nay.

Clinical NLP:
- Use rule-based extraction + dictionary + LLM structured JSON extraction.
- Validate output against schema.

SOAP:
- Render from clinical facts.
- Do not generate unsupported facts.

Evaluation:
- Track WER/CER if ASR is used.
- Track Medical Term Error Rate manually for demo cases.
- Track critical errors:
  - wrong medication
  - wrong dosage
  - wrong allergy
  - wrong negation
  - wrong speaker attribution

## Demo Acceptance Criteria
The MVP is acceptable if:
- It can process at least 3 synthetic outpatient cases.
- It creates transcript or accepts transcript fallback.
- It extracts clinical facts with source attribution.
- It generates SOAP draft.
- It shows safety checklist.
- It requires doctor confirmation.
- It can delete a session.
- It has a simple audit log.
- It clearly says AI output is draft only.