## Mục tiêu file
File này là context chính đưa cho AI coding assistant khi build MVP.

## Project Context
Build a local-first Clinical Ambient Documentation Assistant MVP for outpatient visits.

The system records or receives simulated outpatient visit audio, transcribes it, labels speakers, extracts clinical facts, generates a SOAP/outpatient note draft, adds safety flags, and requires doctor review before confirmation.

This is not an AI Doctor.
The system must not diagnose automatically.
The system must not prescribe automatically.
The system must not generate final medical records without doctor confirmation.
The system must not treat transcript or AI draft as final clinical truth.

## MVP Scope
In scope:
- Simulated outpatient visit audio.
- Local audio upload or recording.
- ASR transcription.
- Optional speaker labeling.
- Clinical fact extraction.
- Source attribution for every clinical fact.
- SOAP/outpatient note draft.
- Safety checklist.
- Doctor review actions: accept, edit, reject, confirm.
- Local storage for demo.
- Audit log for key events.

Out of scope:
- Real HIS/EHR integration.
- Production patient data workflow.
- Realtime assistant.
- Automatic diagnosis.
- Automatic prescribing.
- Autonomous clinical decision-making.
- Cloud processing of real patient data without approval.
- Training/fine-tuning on real patient data.

## Data Policy for MVP
Default development data must be synthetic or actor-generated.
Do not use real patient audio by default.
Do not include real names, phone numbers, addresses, patient IDs, or identifiable health records in demo data.
If a sample transcript contains personal identifiers, mark it as unsafe for development and do not use it.

## Cloud Policy
For MVP, assume local-first.
Do not send real patient audio, transcripts, SOAP drafts, or clinical facts to cloud APIs.
Cloud/API models may only be used with synthetic/de-identified demo data.

## Required Data Objects
The app may handle:
- Session metadata
- Audio file
- Transcript
- Speaker segments
- Clinical facts
- SOAP draft
- Safety flags
- Doctor edits
- Confirmed draft
- Audit log

## Clinical Fact Rule
Every clinical fact must include:
- fact_text
- fact_type
- speaker
- source_timestamp
- transcript_quote
- confidence
- note_section
- requires_doctor_confirmation

Example:
{
  "fact_text": "Bệnh nhân đau thượng vị 3 ngày",
  "fact_type": "symptom",
  "speaker": "Patient",
  "source_timestamp": "00:02:14-00:02:19",
  "transcript_quote": "Em đau vùng thượng vị khoảng 3 ngày nay",
  "note_section": "Subjective",
  "confidence": 0.86,
  "requires_doctor_confirmation": true
}

## Safety Rules
The AI must flag:
- uncertain medication
- uncertain dosage
- missing allergy information
- negation conflict
- unclear speaker
- test result mentioned without value
- diagnosis mentioned but not clearly confirmed by doctor
- plan/order mentioned by non-doctor speaker

## Generation Rules
When generating SOAP/outpatient note:
- Do not invent diagnosis.
- Do not invent medication.
- Do not invent dosage.
- Do not invent allergy.
- Do not invent test results.
- Do not invent vital signs.
- If information is missing, write "Not mentioned in transcript" or "Requires doctor confirmation".
- Keep uncertain items in safety checklist.
- Include source references internally for each fact.

## Doctor Review Rule
The AI draft is never final.
The UI must require doctor review before marking a note as confirmed.
Confirmed note status can only be created after explicit doctor action.

## Retention Rule for MVP
For simulated demo:
- Audio may be kept locally for debugging during the demo.
- Raw audio should be deletable from the UI.
- Prefer deleting raw audio after transcript generation unless needed for evaluation.
- Logs should avoid storing full PHI.

For real patient data:
- Do not process unless explicit approval exists.
- Raw audio should be short-retention only.
- No training on real patient data by default.

## Audit Log Events
Log at minimum:
- session_created
- audio_uploaded_or_recorded
- transcript_generated
- facts_extracted
- soap_draft_generated
- safety_flags_generated
- doctor_edited_note
- doctor_confirmed_note
- audio_deleted
- session_deleted

Each audit event should include:
- event_id
- timestamp
- session_id
- actor_role
- action
- object_type
- object_id
- status

Do not log unnecessary patient identifiers.