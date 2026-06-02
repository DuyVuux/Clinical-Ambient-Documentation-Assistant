## Mục tiêu file
Bản Safety Case rút gọn cho intern MVP, thay cho CSCR production.

## Product
Local-first Clinical Ambient Documentation Assistant MVP for outpatient visits.

## Intended Use
The system supports doctors by creating a draft outpatient/SOAP note from synthetic or actor-generated visit audio/transcript.
The draft is used only for review and demonstration.
Doctor confirmation is mandatory.

## Contraindications
The MVP must not be used for:
- emergency care;
- autonomous diagnosis;
- autonomous prescribing;
- final medical record creation without doctor review;
- direct HIS/EHR write;
- real patient data processing without approval.

## Main Safety Claims

### Claim 1
The AI does not create final clinical records.

Evidence:
- status machine includes draft/edited/rejected/confirmed;
- only doctor can confirm;
- audit log records confirmation.

### Claim 2
The AI does not invent unsupported clinical facts.

Evidence:
- every fact requires source_quote;
- unsupported facts are rejected by validator;
- SOAP renderer uses extracted facts only.

### Claim 3
High-risk clinical entities require doctor confirmation.

Evidence:
- medication, dosage, allergy, diagnosis, plan, red flags, negation require confirmation;
- high-risk flags block final confirmation.

### Claim 4
The system reduces automation bias.

Evidence:
- AI draft label;
- mandatory checklist;
- section-by-section review;
- traceability panel;
- error flagging.

### Claim 5
The system supports error analysis.

Evidence:
- audit log;
- doctor edits;
- safety flags;
- CREOLA-lite error taxonomy;
- demo evaluation table.

## Residual Risks
Remaining risks:
- ASR may still mishear clinical terms.
- LLM may still omit details.
- Doctor may still miss errors.
- Speaker attribution may fail.
- Demo data may not represent real clinic noise.

Mitigation:
- local synthetic-only MVP;
- doctor confirmation;
- safety flags;
- low-quality warning;
- no EHR write;
- no real patient data by default.

## MVP Safety Conclusion
This MVP is acceptable for internal demo/research only if:
- synthetic/actor data is used;
- AI output remains draft-only;
- doctor confirmation is required;
- high-risk facts are flagged;
- source attribution is available;
- limitations are clearly disclosed.