## Mục tiêu file
Context chính đưa cho AI coding assistant khi build evaluation module cho MVP.

## Project Context
Build evaluation logic for a local-first Clinical Ambient Documentation Assistant MVP.

The system processes outpatient audio/transcript, extracts clinical facts, generates SOAP/outpatient note draft, shows safety flags, and requires doctor confirmation.

Evaluation must not focus only on generic WER or text similarity.
Evaluation must measure clinical safety, source attribution, doctor review burden, and note usability.

## Evaluation Philosophy
A transcript with low WER can still be unsafe if it gets medication, dosage, allergy, negation, or speaker attribution wrong.

A SOAP note that sounds fluent can still be unsafe if it contains unsupported clinical facts, omitted red flags, or invented assessment/plan.

Therefore, every evaluation case must compare:
1. audio/transcript against ground truth transcript;
2. transcript against expected clinical entities;
3. extracted facts against expected facts;
4. SOAP draft against source facts;
5. doctor-edited note against AI draft;
6. safety flags against expected risks.

## Required MVP Evaluation Levels

### Level 1: ASR Evaluation
Measure:
- WER
- CharER
- mWER
- Medical Word Hit Rate
- Negation Error
- Critical Entity Error

### Level 2: Speaker Evaluation
Measure:
- speaker attribution accuracy
- DER if timestamped diarization exists
- plan-from-non-doctor errors
- unknown speaker facts

### Level 3: Clinical Fact Extraction Evaluation
Measure:
- Captured Entity Rate
- Accurate Entity Rate
- Unsupported Fact Count
- Omission Count
- Source Attribution Completeness

### Level 4: SOAP Note Evaluation
Measure:
- SOAP Section Classification Accuracy
- Hallucination Rate
- Omission Rate
- Major Defect Count
- Critical Defect Count

### Level 5: Doctor Review Evaluation
Measure:
- edit distance
- time to review
- number of doctor edits
- safety flags resolved
- note usable after light edits

## MVP Data Assumption
Use synthetic or actor-generated demo cases by default.
Do not require real patient data.
Do not require EHR/HIS logs.
Do not require production-scale pilot dataset.

## Minimum Dataset
Minimum acceptable:
- 3 synthetic cases.

Recommended:
- 10 synthetic outpatient cases.

Strong intern MVP:
- 20 synthetic cases with ground truth.

## Required Case Types
Include at least:
1. normal outpatient case;
2. missing information case;
3. medication/dosage case;
4. allergy/negation case;
5. speaker confusion case;
6. noisy or unclear transcript case;
7. red flag symptom case;
8. temporal history vs current symptom case.

## Rule
The MVP evaluation passes only if dangerous errors are visible, counted, and blocked by doctor review.
Do not hide errors behind a single average score.