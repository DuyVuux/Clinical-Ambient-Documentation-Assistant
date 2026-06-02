# 08_schema_anti_patterns_to_avoid.md

## Mục tiêu file

Những lỗi thiết kế schema cần tránh trong MVP.

## Anti-pattern 1: Free-text only note

Sai:
{
"note": "Bệnh nhân đau bụng..."
}

Đúng:
ClinicalNote.sections = [
{
"title": "Subjective",
"text": "...",
"entries": ["ClinicalFact/fact_001"]
}
]

## Anti-pattern 2: Clinical fact without Encounter

Sai:
ClinicalFact chỉ có patientId.

Đúng:
ClinicalFact phải có patient reference và encounter reference.

## Anti-pattern 3: Symptom becomes diagnosis

Sai:
Patient nói đau thượng vị → lưu Diagnosis = viêm dạ dày.

Đúng:
Patient nói đau thượng vị → ClinicalFact type symptom.
Doctor nói nghi viêm dạ dày → diagnosis_mention, requires confirmation.

## Anti-pattern 4: Medication history mixed with order

Sai:
Tất cả thuốc cho vào một list "medications".

Đúng:
Medication.assertionType:

* history nếu patient/caregiver tự khai.
* order nếu doctor chỉ định rõ.

## Anti-pattern 5: No source attribution

Sai:
SOAP note có câu nhưng không biết lấy từ đâu.

Đúng:
ClinicalFact.source phải có segmentId, timestamp, speaker, quote.

## Anti-pattern 6: Losing audit/provenance

Sai:
Không biết ai sửa note, sửa lúc nào.

Đúng:
ReviewAction + AuditEvent + AuditMetadata.

## Anti-pattern 7: Hardcoded clinical strings only

Sai:
"diagnosis": "High blood pressure"

Đúng:
{
"code": {
"text": "Tăng huyết áp",
"coding": []
}
}

## Anti-pattern 8: Overbuilding FHIR too early

Sai:
Intern MVP cố dựng FHIR server, SMART on FHIR, terminology service.

Đúng:
Build canonical schema first.
FHIR mapping later.
