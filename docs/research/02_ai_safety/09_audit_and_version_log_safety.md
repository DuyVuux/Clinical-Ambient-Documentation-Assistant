## Mục tiêu file
Audit/version log rút gọn cho intern MVP.

## Principle
The MVP must be able to reconstruct:
- what AI generated;
- what doctor changed;
- what was confirmed;
- when it happened.

## Storage
For intern MVP, use local JSONL append-only log:
data/audit/events.jsonl

## Required Event Schema

{
  "event_id": "uuid",
  "timestamp": "ISO-8601",
  "session_id": "string",
  "actor_role": "developer | doctor_reviewer | mentor | admin_demo | system",
  "action": "string",
  "object_type": "session | transcript | clinical_facts | safety_flags | soap_draft | note",
  "object_id": "string",
  "status": "success | failed",
  "details": {
    "safe_summary": "string"
  }
}

## Required Events
- session_created
- transcript_uploaded
- transcript_generated
- input_quality_checked
- clinical_facts_extracted
- safety_flags_generated
- soap_draft_generated
- doctor_viewed_draft
- doctor_edited_note
- doctor_acknowledged_flag
- doctor_resolved_flag
- doctor_rejected_note
- doctor_confirmed_note
- session_deleted

## Versioned Note Objects
Store:
- ai_draft_v1
- doctor_edited_v1
- confirmed_note

## Do Not Store in Audit Details
- full patient identifiers;
- phone numbers;
- addresses;
- national IDs;
- full raw transcript if real data;
- unnecessary PHI.

For synthetic demo data, still keep logs minimal.