# 09_future_phase_mapping_notes.md

## Mục tiêu file

Ghi chú định hướng tương lai, không build trong intern MVP.

## Future Mapping

PatientProfile → FHIR Patient
ClinicianProfile → FHIR Practitioner / PractitionerRole
Encounter → FHIR Encounter
ClinicalFact symptom/vital/lab → FHIR Observation
ClinicalFact diagnosis_mention → FHIR Condition
Medication assertionType = order → FHIR MedicationRequest
Medication assertionType = history → FHIR MedicationStatement / FHIR R5 MedicationUsage
Allergy → FHIR AllergyIntolerance
ClinicalNote → FHIR Composition
Attachment/audio/pdf → FHIR DocumentReference
AuditEvent/AuditMetadata → FHIR AuditEvent / Provenance later

## Future Stages

Stage 1 - Intern MVP:
Canonical schema without HIS integration.

Stage 2 - Terminology:
Add coding enrichment for SNOMED CT, LOINC, ICD-10, RxNorm/ATC.

Stage 3 - FHIR export:
Export canonical objects as FHIR Bundle.

Stage 4 - HIS/EHR integration:
Add FHIR API, SMART on FHIR, anti-corruption/facade layer.

## Important

Do not let future mapping requirements block intern MVP.
The goal now is semantic discipline, not enterprise integration.
