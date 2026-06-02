# 06_minimal_json_schema_for_mvp.md

## Mục tiêu file

Một schema JSON tối giản để dùng ngay trong MVP.

```json
{
  "session": {
    "sessionId": "session_001",
    "dataType": "synthetic",
    "patient": {
      "id": "patient_001",
      "identifiers": [
        {
          "use": "temp",
          "system": "urn:demo:patient",
          "value": "DEMO-PATIENT-001"
        }
      ],
      "name": {
        "text": "Bệnh nhân demo"
      },
      "gender": "unknown",
      "birthDate": null,
      "isSynthetic": true
    },
    "clinician": {
      "id": "doctor_001",
      "name": {
        "text": "Bác sĩ demo"
      },
      "role": {
        "text": "Doctor Reviewer"
      }
    },
    "encounter": {
      "id": "encounter_001",
      "status": "in-progress",
      "class": {
        "text": "outpatient"
      },
      "specialty": {
        "text": "Tiêu hóa"
      },
      "period": {
        "start": "2026-05-29T09:00:00+07:00",
        "end": null
      }
    },
    "transcriptSegments": [],
    "clinicalFacts": [],
    "medications": [],
    "allergies": [],
    "safetyFlags": [],
    "clinicalNote": null,
    "reviewActions": [],
    "auditLog": []
  }
}
```
