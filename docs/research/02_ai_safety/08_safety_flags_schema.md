## Mục tiêu file
Schema safety flags cho MVP.

## Safety Flag JSON Schema

{
  "flag_id": "uuid",
  "session_id": "string",
  "flag_type": "string",
  "severity": "low | medium | high",
  "message": "string",
  "related_fact_id": "string | null",
  "source_quote": "string | null",
  "speaker": "Doctor | Patient | Caregiver | Nurse | Other | Unknown | null",
  "timestamp": "string | null",
  "requires_doctor_confirmation": true,
  "status": "open | acknowledged | resolved | dismissed",
  "doctor_comment": "string | null"
}

## Required Flag Types

### HIGH severity
- UNCERTAIN_MEDICATION
- UNCERTAIN_DOSAGE
- ALLERGY_CONFLICT
- NEGATION_CONFLICT
- RED_FLAG_SYMPTOM
- PLAN_FROM_NON_DOCTOR
- UNSUPPORTED_DIAGNOSIS
- UNSUPPORTED_PRESCRIPTION
- CRITICAL_ENTITY_LOW_CONFIDENCE

### MEDIUM severity
- MISSING_ALLERGY
- MISSING_MEDICATION_REVIEW
- UNKNOWN_SPEAKER
- LOW_AUDIO_QUALITY
- LOW_ASR_CONFIDENCE
- MISSING_VITALS
- MISSING_LAB_VALUE
- UNCLEAR_FOLLOW_UP

### LOW severity
- STYLE_UNCLEAR
- SECTION_MAPPING_UNCERTAIN
- NEEDS_FORMAT_REVIEW

## Safety Flag Rules
- High severity flags must block confirmation until acknowledged or resolved.
- Medication/dosage/allergy flags must always require doctor confirmation.
- Unknown speaker facts must be reviewed.
- Missing data should not be silently filled.