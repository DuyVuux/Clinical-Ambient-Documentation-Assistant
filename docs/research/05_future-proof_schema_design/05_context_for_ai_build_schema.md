# 05_context_for_ai_build_schema.md

## Mục tiêu file

Paste file này vào ChatGPT/Cursor/Claude để yêu cầu AI build schema layer cho MVP.

## Build Instruction

You are building the schema layer for an intern MVP: a local-first Clinical Ambient Documentation Assistant for Vietnamese outpatient visits.

This is not an AI Doctor.
The system must not diagnose, prescribe, or finalize a medical record automatically.
The output is a draft SOAP/outpatient note that requires doctor review and confirmation.

## Architecture

Use a FHIR-informed internal canonical model.
Do not implement a native FHIR server.
Do not store raw FHIR resources as the primary database model.
Do not implement HIS/EHR integration.
Do not implement SMART on FHIR.
Do not require terminology server lookup.
Do not require strict FHIR profile validation.

Use simple internal models that preserve future FHIR compatibility:

* Identifier
* Reference
* CodeableConcept
* Quantity
* Period
* AuditMetadata
* SourceAttribution

## Required Entities

Implement:

* PatientProfile
* ClinicianProfile
* Encounter
* TranscriptSegment
* ClinicalFact
* ClinicalNote
* Medication
* Allergy
* SafetyFlag
* ReviewAction
* AuditEvent

Optional later:

* DiagnosticReport
* Attachment
* FHIR Export Bundle
* FHIR Import Mapping

## Data Storage

For MVP, use local-first storage:

* SQLite with JSON fields, or
* PostgreSQL with JSONB, or
* local JSON files per session.

Every record must include:

* id
* createdAt
* updatedAt
* createdBy
* updatedBy
* versionId where practical.

## Key Constraints

1. Every clinical object must reference Patient and Encounter.
2. Every clinical fact must have source attribution.
3. ClinicalNote must be sectioned into SOAP.
4. Medication history and medication order must be separated by assertionType.
5. Symptoms must not be stored as diagnoses.
6. Missing information must not be invented.
7. Unknown speaker requires review.
8. Doctor confirmation is mandatory before note status becomes confirmed.
9. Audit log must not contain full PHI.
10. All demo data must be synthetic/actor data.

## ClinicalNote Status State Machine

Allowed transitions:

* draft → edited
* draft → rejected
* draft → confirmed
* edited → confirmed
* edited → rejected
* confirmed → amended
* confirmed → entered-in-error

The system must not allow:

* AI-generated draft → confirmed without explicit doctor action.

## Minimal API / Function Requirements

Build functions:

* create_patient_profile()
* create_clinician_profile()
* create_encounter()
* create_transcript_segment()
* extract_clinical_fact()
* create_medication_from_fact()
* create_allergy_status()
* create_safety_flag()
* render_soap_note()
* record_review_action()
* confirm_note()
* write_audit_event()
* delete_session()

## Validation Rules

ClinicalFact validation:

* must have factType
* must have patient reference
* must have encounter reference
* must have source quote unless manually entered by doctor
* must have requiresDoctorConfirmation = true by default

Medication validation:

* assertionType must be history or order
* if assertionType = order, source speaker must be Doctor
* dosageText missing or unclear creates UNCERTAIN_DOSAGE flag

ClinicalNote validation:

* must have Subjective, Objective, Assessment, Plan sections
* must include safety checklist
* status cannot be confirmed unless reviewedBy exists

SafetyFlag validation:

* high severity flags must block confirmation until doctor marks reviewed

## Output Expected

Generate:

* schema definitions
* validation functions
* example JSON
* simple persistence layer
* test cases for 3 demo encounters
