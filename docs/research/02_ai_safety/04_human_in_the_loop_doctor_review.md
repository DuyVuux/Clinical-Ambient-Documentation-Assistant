## Mục tiêu file
Thiết kế doctor review loop để giảm automation bias.

## Core Principle
AI draft is never final.
Doctor must actively review and confirm.

## Review UI Requirements

### 1. Always show draft label
Display:
"AI-GENERATED DRAFT — DOCTOR REVIEW REQUIRED"

### 2. Section-by-section review
SOAP sections:
- Subjective
- Objective
- Assessment
- Plan
- Safety checklist

Each section should have:
- content;
- source facts;
- uncertainty markers;
- edit button;
- confirm checkbox.

### 3. Mandatory high-risk confirmation
Before confirming note, doctor must check:

- [ ] Allergy reviewed
- [ ] Medication reviewed
- [ ] Dosage/frequency reviewed
- [ ] Diagnosis/assessment reviewed
- [ ] Plan/order reviewed
- [ ] Negation-sensitive statements reviewed
- [ ] Red flags reviewed
- [ ] Missing information reviewed

### 4. Traceability interaction
When doctor clicks a note sentence, UI should show:
- source transcript quote;
- speaker;
- timestamp;
- confidence;
- safety flags.

For intern MVP, a side panel is enough.

### 5. Prevent one-click rubber stamping
The Confirm button should remain disabled until:
- all high-risk checklist items are checked;
- all high-severity safety flags are resolved or acknowledged;
- doctor has viewed the SOAP draft.

### 6. Doctor actions
Allowed actions:
- accept fact;
- edit fact;
- reject fact;
- mark uncertain;
- flag AI error;
- confirm final draft.

### 7. Confirmation event
When doctor confirms:
- set note.status = "confirmed";
- save confirmed_at timestamp;
- save reviewer role;
- write audit event "doctor_confirmed_note".

For intern MVP, no real digital signature is required.
Use explicit button click and audit log.