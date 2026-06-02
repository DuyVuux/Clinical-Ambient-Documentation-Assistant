# 01_mvp_schema_scope.md

## Mục tiêu file
Chốt phạm vi schema cần build cho intern MVP.

## MVP Schema Goal
Build a lightweight but future-proof canonical schema for a local-first outpatient clinical documentation assistant.

The schema must support:
- simulated/actor outpatient session;
- transcript with speaker and timestamp;
- clinical facts with source attribution;
- SOAP/outpatient note draft;
- safety flags;
- doctor review and confirmation;
- audit logging;
- future mapping to FHIR without implementing FHIR now.

## In Scope
Implement these entities:

1. PatientProfile
2. ClinicianProfile
3. Encounter
4. TranscriptSegment
5. ClinicalFact
6. ClinicalNote
7. Medication
8. Allergy
9. SafetyFlag
10. ReviewAction
11. AuditEvent

## Out of Scope for Intern MVP
Do not implement:
- native FHIR server;
- SMART on FHIR;
- HIS/EHR API integration;
- FHIR Bundle export;
- strict FHIR profile validation;
- terminology server lookup;
- full DiagnosticReport workflow;
- full DocumentReference workflow;
- multi-tenant production isolation;
- billing/coding workflow;
- auto ICD-10 coding;
- auto prescription order submission.

## Architecture Rule
Use a FHIR-informed internal model.

This means:
- Internal schema is simple.
- FHIR-like primitives are used where useful.
- Every major object has audit metadata.
- Clinical notes are structured into sections.
- Every clinical fact can be traced back to transcript evidence.

## Recommended Storage for Intern MVP
Use one of:
- SQLite + JSON columns;
- PostgreSQL + JSONB;
- local JSON files for very early prototype.

Recommended simple folder:
data/
  sessions/
    {session_id}/
      metadata.json
      audio.wav
      transcript.json
      clinical_facts.json
      soap_note.json
      safety_flags.json
      audit_log.jsonl
