# 09_benchmark_and_maturity_positioning.md

## Mục tiêu file
Định vị MVP so với chuẩn quốc tế mà không overclaim.

## International Benchmark Lessons
Ambient clinical documentation tools are evaluated not only by transcript accuracy, but by:
- clinical safety;
- doctor review workflow;
- linked evidence;
- auditability;
- editing burden;
- physician trust;
- real workflow adoption.

## What Intern MVP Does Not Need
The intern MVP does not need:
- deep EHR integration;
- real-time assistant;
- billing code generation;
- ICD-10/HCC suggestion;
- patient-facing summary;
- 500–800 real visits;
- multi-site clinical trial;
- specialty fine-tuning;
- production-grade model monitoring.

## What Intern MVP Must Demonstrate
The MVP must demonstrate:
- draft SOAP generation;
- clinical fact extraction;
- source attribution;
- safety flags;
- doctor confirmation;
- audit log;
- basic evaluation metrics;
- ability to fail safely.

## Maturity Model Position
The MVP should not stop at Level 3.

### Level 3
Draft SOAP generation only.
Risk:
- hallucination;
- omission;
- black-box note;
- automation bias.

### Level 4 Target for MVP
Draft SOAP generation with:
- doctor review;
- safety flags;
- source attribution;
- linked evidence concept;
- audit log;
- evaluation of critical errors.

## Practical MVP Claim
Safe claim:
"This MVP demonstrates a local-first clinical documentation pipeline that generates draft outpatient notes from synthetic/actor data with source attribution, safety flags, and doctor confirmation."

Unsafe claim:
"This MVP automatically writes accurate medical records."
"This MVP diagnoses or recommends treatment."
"This MVP saves hours per doctor per day."
"This MVP is clinically validated."

## Time-Saving Claim Rule
Do not claim real time saved unless baseline and comparison data exist.

For intern MVP, report:
- processing time;
- review time;
- edit ratio;
- note usable after light edits.

Only after pilot, measure:
- time saved per visit;
- after-hours documentation reduction;
- continued usage rate.