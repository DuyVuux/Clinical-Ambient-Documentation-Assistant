# 03_canonical_entities_mvp.md

## Mục tiêu file

Định nghĩa entity chính cần build trong intern MVP.

## 1. PatientProfile

Represents the demo patient.
Do not use real patient data by default.

```json
{
  "id": "patient_001",
  "resourceType": "Patient",
  "identifiers": [
    {
      "use": "temp",
      "system": "urn:demo:patient",
      "value": "DEMO-PATIENT-001"
    }
  ],
  "name": {
    "text": "Bệnh nhân demo 001"
  },
  "gender": "female",
  "birthDate": "1988-01-01",
  "isSynthetic": true,
  "audit": {}
}
```

MVP notes:

* name can be fake.
* birthDate can be fake or omitted.
* identifiers must not contain real MRN unless approved.
* Keep identifiers array for future HIS mapping.

## 2. ClinicianProfile

Represents doctor/reviewer/user.

```json
{
  "id": "doctor_001",
  "resourceType": "Practitioner",
  "identifiers": [
    {
      "use": "temp",
      "system": "urn:demo:clinician",
      "value": "DEMO-DOCTOR-001"
    }
  ],
  "name": {
    "text": "Bác sĩ demo"
  },
  "role": {
    "text": "Doctor Reviewer",
    "coding": []
  },
  "audit": {}
}
```

MVP notes:

* Use role to distinguish doctor_reviewer, developer, admin_demo.
* Do not overbuild PractitionerRole yet.

## 3. Encounter

Represents one outpatient visit/session.

```json
{
  "id": "encounter_001",
  "resourceType": "Encounter",
  "status": "in-progress",
  "class": {
    "text": "outpatient",
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "AMB",
        "display": "ambulatory"
      }
    ]
  },
  "subject": {
    "reference": "Patient/patient_001",
    "type": "Patient",
    "display": "Bệnh nhân demo 001"
  },
  "participant": [
    {
      "reference": "Practitioner/doctor_001",
      "type": "Practitioner",
      "display": "Bác sĩ demo"
    }
  ],
  "period": {
    "start": "2026-05-29T09:00:00+07:00",
    "end": null
  },
  "specialty": {
    "text": "Tiêu hóa",
    "coding": []
  },
  "audit": {}
}
```

MVP notes:

* Encounter is mandatory.
* Every clinical fact and note must reference encounterId.
* This prevents losing visit context.

## 4. TranscriptSegment

Represents speaker-tagged transcript with timestamp.

```json
{
  "id": "seg_001",
  "sessionId": "session_001",
  "encounter": {
    "reference": "Encounter/encounter_001",
    "type": "Encounter"
  },
  "speaker": "Patient",
  "timestampStart": "00:01:12",
  "timestampEnd": "00:01:18",
  "text": "Em đau vùng thượng vị khoảng 3 ngày nay",
  "asrConfidence": 0.86,
  "isEdited": false,
  "audit": {}
}
```

Allowed speaker values:

* Doctor
* Patient
* Caregiver
* Nurse
* Other
* Unknown

MVP notes:

* Manual speaker tags are acceptable.
* Diarization can be added later.
* Unknown speaker must trigger review if used for clinical facts.

## 5. ClinicalFact

Represents extracted clinical fact with source attribution.

```json
{
  "id": "fact_001",
  "sessionId": "session_001",
  "subject": {
    "reference": "Patient/patient_001",
    "type": "Patient"
  },
  "encounter": {
    "reference": "Encounter/encounter_001",
    "type": "Encounter"
  },
  "factType": "symptom",
  "code": {
    "text": "Đau thượng vị",
    "coding": []
  },
  "valueText": "Bệnh nhân đau thượng vị 3 ngày",
  "valueQuantity": null,
  "clinicalStatus": "active",
  "noteSection": "Subjective",
  "source": {
    "sourceType": "transcript",
    "segmentId": "seg_001",
    "timestampStart": "00:01:12",
    "timestampEnd": "00:01:18",
    "speaker": "Patient",
    "quote": "Em đau vùng thượng vị khoảng 3 ngày nay",
    "asrConfidence": 0.86
  },
  "confidence": 0.86,
  "requiresDoctorConfirmation": true,
  "safetyFlagIds": [],
  "audit": {}
}
```

Allowed factType:

* symptom
* duration
* medication
* dosage
* allergy
* vital
* lab_test
* diagnosis_mention
* plan
* instruction
* red_flag
* negation
* other

MVP mapping logic:

* symptom/duration/negation from Patient → Subjective.
* vital/lab_test → Objective.
* diagnosis_mention from Doctor → Assessment.
* plan/instruction from Doctor → Plan.
* plan from non-Doctor → do not auto-add to Plan; create safety flag.

## 6. ClinicalNote

Represents structured SOAP/outpatient note draft.

```json
{
  "id": "note_001",
  "resourceType": "ClinicalNote",
  "status": "draft",
  "type": {
    "text": "Outpatient SOAP note",
    "coding": []
  },
  "title": "SOAP note draft - outpatient visit",
  "subject": {
    "reference": "Patient/patient_001",
    "type": "Patient"
  },
  "encounter": {
    "reference": "Encounter/encounter_001",
    "type": "Encounter"
  },
  "author": {
    "reference": "Practitioner/ai_assistant",
    "type": "Practitioner",
    "display": "AI Assistant"
  },
  "sections": [
    {
      "title": "Subjective",
      "code": {
        "text": "Subjective",
        "coding": []
      },
      "text": "Bệnh nhân đau thượng vị 3 ngày. Không ghi nhận sốt.",
      "entries": [
        {
          "reference": "ClinicalFact/fact_001",
          "type": "ClinicalFact"
        }
      ]
    },
    {
      "title": "Objective",
      "code": {
        "text": "Objective",
        "coding": []
      },
      "text": "Not mentioned in transcript.",
      "entries": []
    },
    {
      "title": "Assessment",
      "code": {
        "text": "Assessment",
        "coding": []
      },
      "text": "Requires doctor confirmation.",
      "entries": []
    },
    {
      "title": "Plan",
      "code": {
        "text": "Plan",
        "coding": []
      },
      "text": "Requires doctor confirmation.",
      "entries": []
    }
  ],
  "safetyChecklistIds": [
    "flag_001"
  ],
  "doctorReview": {
    "reviewStatus": "not_reviewed",
    "reviewedBy": null,
    "reviewedAt": null,
    "doctorEdits": []
  },
  "audit": {}
}
```

Allowed note status:

* draft
* edited
* rejected
* confirmed
* entered-in-error

MVP notes:

* ClinicalNote must be sectioned.
* Do not store only one free-text blob.
* Sections should reference ClinicalFact IDs where possible.
* Confirmed note requires explicit doctor action.

## 7. Medication

Represents medication history or medication order mention.

```json
{
  "id": "med_001",
  "subject": {
    "reference": "Patient/patient_001",
    "type": "Patient"
  },
  "encounter": {
    "reference": "Encounter/encounter_001",
    "type": "Encounter"
  },
  "assertionType": "history",
  "status": "active",
  "medication": {
    "text": "Paracetamol",
    "coding": []
  },
  "dosageText": "Không rõ liều",
  "source": {
    "sourceType": "transcript",
    "segmentId": "seg_010",
    "timestampStart": "00:04:10",
    "timestampEnd": "00:04:16",
    "speaker": "Patient",
    "quote": "Tôi có uống para nhưng không nhớ liều",
    "asrConfidence": 0.74
  },
  "requiresDoctorConfirmation": true,
  "audit": {}
}
```

Allowed assertionType:

* history: patient/caregiver reports current or past medication.
* order: doctor clearly gives medication order/instruction.

Safety rule:

* If assertionType = order, speaker must be Doctor.
* If dosage unclear, create UNCERTAIN_DOSAGE flag.
* If medication unclear, create UNCERTAIN_MEDICATION flag.

## 8. Allergy

Represents allergy or allergy negation.

```json
{
  "id": "allergy_001",
  "subject": {
    "reference": "Patient/patient_001",
    "type": "Patient"
  },
  "encounter": {
    "reference": "Encounter/encounter_001",
    "type": "Encounter"
  },
  "clinicalStatus": "unknown",
  "type": "allergy",
  "criticality": "unknown",
  "substance": {
    "text": "Not mentioned",
    "coding": []
  },
  "reaction": [],
  "source": null,
  "requiresDoctorConfirmation": true,
  "audit": {}
}
```

Allowed clinicalStatus:

* active
* inactive
* resolved
* unknown
* not-mentioned

MVP notes:

* Missing allergy must generate safety flag.
* "Không dị ứng thuốc" should be captured as allergy negation.
* Do not invent allergy status.

## 9. SafetyFlag

Represents safety issue requiring review.

```json
{
  "id": "flag_001",
  "sessionId": "session_001",
  "subject": {
    "reference": "Patient/patient_001",
    "type": "Patient"
  },
  "encounter": {
    "reference": "Encounter/encounter_001",
    "type": "Encounter"
  },
  "flagType": "MISSING_ALLERGY",
  "severity": "high",
  "message": "Allergy information was not mentioned in the transcript. Doctor must confirm before finalizing note.",
  "relatedFactIds": [],
  "relatedSegmentIds": [],
  "requiresDoctorConfirmation": true,
  "status": "open",
  "audit": {}
}
```

Allowed flagType:

* MISSING_ALLERGY
* UNCERTAIN_MEDICATION
* UNCERTAIN_DOSAGE
* NEGATION_CONFLICT
* UNKNOWN_SPEAKER
* PLAN_FROM_NON_DOCTOR
* LOW_ASR_CONFIDENCE_CRITICAL_ENTITY
* UNCLEAR_DIAGNOSIS
* MISSING_VITALS
* MISSING_TEST_VALUE
* RED_FLAG_REQUIRES_REVIEW
* OTHER

## 10. ReviewAction

Represents doctor review action.

```json
{
  "id": "review_001",
  "note": {
    "reference": "ClinicalNote/note_001",
    "type": "ClinicalNote"
  },
  "reviewedBy": {
    "reference": "Practitioner/doctor_001",
    "type": "Practitioner"
  },
  "action": "edit",
  "timestamp": "2026-05-29T09:30:00+07:00",
  "beforeText": "Requires doctor confirmation.",
  "afterText": "Bác sĩ nghi viêm dạ dày, hẹn tái khám nếu đau tăng.",
  "comment": "Assessment clarified by doctor.",
  "audit": {}
}
```

Allowed action:

* open_review
* accept_section
* edit
* reject
* confirm
* mark_entered_in_error

## 11. AuditEvent

Simplified audit event for MVP.

```json
{
  "id": "audit_001",
  "timestamp": "2026-05-29T09:30:00+07:00",
  "actor": {
    "reference": "Practitioner/doctor_001",
    "type": "Practitioner"
  },
  "action": "doctor_confirmed_note",
  "object": {
    "reference": "ClinicalNote/note_001",
    "type": "ClinicalNote"
  },
  "sessionId": "session_001",
  "status": "success",
  "details": {
    "noteStatus": "confirmed"
  }
}
```

Do not store full PHI in audit details.
