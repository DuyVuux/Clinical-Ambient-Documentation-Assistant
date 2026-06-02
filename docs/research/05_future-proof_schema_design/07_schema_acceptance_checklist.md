# 07_schema_acceptance_checklist.md

## Mục tiêu file

Checklist kiểm tra schema MVP đã đủ chưa.

## Must Have

* [ ] Có PatientProfile.
* [ ] Có ClinicianProfile.
* [ ] Có Encounter.
* [ ] Có TranscriptSegment.
* [ ] Có ClinicalFact.
* [ ] Có ClinicalNote dạng sections, không phải 1 free-text blob.
* [ ] Có Medication với assertionType = history/order.
* [ ] Có Allergy hoặc missing allergy flag.
* [ ] Có SafetyFlag.
* [ ] Có ReviewAction.
* [ ] Có AuditEvent.
* [ ] Mỗi major entity có AuditMetadata.
* [ ] Mỗi ClinicalFact có source attribution.
* [ ] Mỗi ClinicalFact link tới Patient + Encounter.
* [ ] ClinicalNote link tới Patient + Encounter.
* [ ] SOAP sections reference ClinicalFact IDs nếu có.
* [ ] Note không thể confirmed nếu chưa có doctor review.

## Should Have

* [ ] CodeableConcept.text được dùng cho mọi concept lâm sàng.
* [ ] coding array có thể để trống.
* [ ] Identifier array được giữ để future HIS mapping.
* [ ] Quantity dùng cho lab/vital numeric values.
* [ ] Unknown speaker tạo safety flag.
* [ ] Missing allergy tạo safety flag.
* [ ] Uncertain medication/dosage tạo safety flag.
* [ ] Plan từ non-doctor không tự đưa vào Plan.

## Defer

* [ ] FHIR server.
* [ ] FHIR Bundle export.
* [ ] SMART on FHIR.
* [ ] Terminology server.
* [ ] SNOMED/LOINC/ICD/RxNorm full mapping.
* [ ] Native FHIR Provenance.
* [ ] Native FHIR AuditEvent.
* [ ] Strict FHIR profile validation.
* [ ] HIS/EHR integration.
* [ ] Multi-tenant production RBAC.
