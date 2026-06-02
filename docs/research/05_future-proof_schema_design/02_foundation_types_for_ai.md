# 02_foundation_types_for_ai.md

## Mục tiêu file
Các type nền tảng để AI/coder dùng khi build schema.

## Coding
Use Coding only when a known standard/local code exists.
For MVP, coding may be empty.

```json
{
  "system": "http://snomed.info/sct",
  "code": "string",
  "display": "string"
}
```

## CodeableConcept

Use this for symptoms, diagnoses, labs, medications, allergies, note type, encounter class.

MVP rule:

* Always preserve raw Vietnamese clinical text in text.
* coding can be empty.

```json
{
  "text": "Đau thượng vị",
  "coding": []
}
```

## Identifier

Use for external identifiers.
For demo, use fake identifiers only.

```json
{
  "use": "temp",
  "system": "urn:demo:patient",
  "value": "DEMO-PATIENT-001"
}
```

## Reference

Use references instead of copying entire objects.

```json
{
  "reference": "Patient/patient_001",
  "type": "Patient",
  "display": "Demo patient"
}
```

## Period

Use for encounter time or medication usage period.

```json
{
  "start": "2026-05-29T09:00:00+07:00",
  "end": "2026-05-29T09:20:00+07:00"
}
```

## Quantity

Use for vitals/labs when numeric values exist.

```json
{
  "value": 37.8,
  "unit": "°C",
  "system": "http://unitsofmeasure.org",
  "code": "Cel"
}
```

## AuditMetadata

Every major entity must include audit metadata.

```json
{
  "createdAt": "2026-05-29T09:00:00+07:00",
  "updatedAt": "2026-05-29T09:10:00+07:00",
  "createdBy": {
    "reference": "Practitioner/dev_001",
    "type": "Practitioner",
    "display": "Intern Developer"
  },
  "updatedBy": {
    "reference": "Practitioner/doctor_001",
    "type": "Practitioner",
    "display": "Doctor Reviewer"
  },
  "versionId": 1
}
```

## SourceAttribution

This is required for clinical documentation AI.

```json
{
  "sourceType": "transcript",
  "segmentId": "seg_001",
  "timestampStart": "00:01:12",
  "timestampEnd": "00:01:18",
  "speaker": "Patient",
  "quote": "Em đau vùng thượng vị khoảng 3 ngày nay",
  "asrConfidence": 0.86
}
```
