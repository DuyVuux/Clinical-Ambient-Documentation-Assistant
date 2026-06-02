# 04_schema_mapping_rules_for_ai.md

## Mục tiêu file

Quy tắc để AI/coder map transcript/facts sang canonical schema.

## Rule 1: Everything belongs to an Encounter

Every ClinicalFact, ClinicalNote, Medication, Allergy, SafetyFlag must reference:

* Patient
* Encounter

Do not attach clinical facts directly to Patient only.

## Rule 2: Symptom is not Diagnosis

Patient says:
"Em đau thượng vị 3 ngày."

Store as:

* ClinicalFact.factType = symptom
* noteSection = Subjective
* possible future FHIR = Observation

Do not store as:

* Diagnosis/Condition = "viêm dạ dày"

## Rule 3: Doctor diagnosis mention is not automatically final

Doctor says:
"Có thể là viêm dạ dày."

Store as:

* ClinicalFact.factType = diagnosis_mention
* noteSection = Assessment
* requiresDoctorConfirmation = true

## Rule 4: Medication history and medication order must be separated

Patient says:
"Tôi đang uống paracetamol."

Store as:

* Medication.assertionType = history

Doctor says:
"Anh uống paracetamol 500mg khi sốt."

Store as:

* Medication.assertionType = order
* requiresDoctorConfirmation = true

If non-doctor speaker mentions a plan/order:

* create SafetyFlag PLAN_FROM_NON_DOCTOR
* do not automatically put into Plan

## Rule 5: ClinicalNote must be structured

Do not store SOAP note as a single string only.

Correct:
ClinicalNote.sections = [
Subjective,
Objective,
Assessment,
Plan
]

Each section should include:

* title
* text
* entries referencing ClinicalFact IDs

## Rule 6: Missing information must remain missing

If vitals are not mentioned:
"Not mentioned in transcript."

If allergy is not mentioned:

* create Allergy with clinicalStatus = "not-mentioned" or omit Allergy object
* create SafetyFlag MISSING_ALLERGY

Never invent:

* diagnosis
* medication
* dosage
* allergy
* test result
* vital sign
* physical exam finding

## Rule 7: CodeableConcept.text is mandatory for MVP

Even if coding is empty, text must preserve the original clinical meaning.

Example:
{
"text": "HbA1c",
"coding": []
}

Later, coding can be enriched with LOINC/SNOMED/ICD/RxNorm/ATC.

## Rule 8: Preserve source attribution

Every ClinicalFact must include:

* transcript segment ID
* timestamp range
* speaker
* quote
* confidence

If source is missing:

* requiresDoctorConfirmation = true
* create safety flag if critical
