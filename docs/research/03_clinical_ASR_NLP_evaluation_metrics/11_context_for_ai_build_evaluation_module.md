## Mục tiêu file
Paste trực tiếp cho AI khi yêu cầu build evaluation module.

## Build Instruction
You are building the evaluation module for a Vietnamese outpatient Clinical Ambient Documentation Assistant MVP.

The MVP is local-first and uses synthetic/actor data by default.
It generates AI draft notes only.
Doctor confirmation is required.
The system must not diagnose or prescribe autonomously.

## What to Build
Build evaluation utilities that can compare:
1. ground truth transcript vs ASR transcript;
2. expected clinical facts vs extracted facts;
3. expected SOAP draft vs generated SOAP draft;
4. AI draft vs doctor-edited draft;
5. expected safety flags vs generated safety flags.

## Required Inputs Per Case
Each case folder should contain:
- metadata.json
- ground_truth_transcript.txt
- asr_transcript.txt or transcript.txt
- expected_facts.json
- actual_facts.json
- expected_safety_flags.json
- actual_safety_flags.json
- expected_soap.md
- actual_soap.md
- doctor_edited_soap.md optional
- evaluation_result.json

## Required Metrics
Implement or support manual entry for:
- WER
- CharER
- mWER
- Medical Word Hit Rate
- Negation Error Count
- Critical Entity Error Count
- Captured Entity Rate
- Accurate Entity Rate
- Unsupported Fact Count
- Source Attribution Completeness
- SOAP Section Classification Accuracy
- Hallucination Count
- Omission Count
- Major Defect Count
- Critical Defect Count
- Edit Ratio
- Minimally-Edited Note status
- Usable After Light Edits status

## Important Metric Naming
Do not use "CER" ambiguously.

Use:
- CharER for Character Error Rate.
- CapturedEntityRate for Captured Entity Rate.

## Clinical Matching Rule
A fact is correct only if:
- clinically equivalent;
- correct speaker;
- correct SOAP section;
- supported by source quote;
- no wrong numeric value;
- no reversed negation;
- no unsupported diagnosis or plan.

## Critical Entities
Treat these as high-risk:
- medication;
- dosage;
- frequency;
- allergy;
- diagnosis;
- plan/order;
- red flag symptom;
- lab value;
- important negation.

## Evaluation Result Schema
{
  "case_id": "string",
  "asr_metrics": {
    "wer": 0.0,
    "char_er": 0.0,
    "mwer": 0.0,
    "medical_word_hit_rate": 0.0,
    "negation_error_count": 0,
    "critical_entity_error_count": 0
  },
  "fact_metrics": {
    "captured_entity_rate": 0.0,
    "accurate_entity_rate": 0.0,
    "unsupported_fact_count": 0,
    "source_attribution_completeness": 0.0,
    "critical_entity_capture_rate": 0.0
  },
  "soap_metrics": {
    "soap_section_accuracy": 0.0,
    "hallucination_count": 0,
    "omission_count": 0,
    "major_defect_count": 0,
    "critical_defect_count": 0
  },
  "doctor_review_metrics": {
    "edit_ratio": 0.0,
    "minimally_edited": true,
    "usable_after_light_edits": "yes | no | borderline",
    "review_time_seconds": null
  },
  "pass_fail": {
    "passed": true,
    "reasons": []
  }
}

## Pass/Fail Logic
Fail the case if:
- any unflagged critical error exists;
- medication/dosage/allergy is unsupported;
- diagnosis is invented;
- plan is created from non-doctor speaker;
- clinical fact lacks source attribution;
- AI note status becomes confirmed without doctor action.

## Output
Generate:
- per-case evaluation_result.json;
- summary table;
- error taxonomy report;
- markdown evaluation report.

## Do Not
- Do not rely only on WER.
- Do not rely on ROUGE as primary metric.
- Do not hide critical errors inside average scores.
- Do not claim clinical validation.
- Do not use real patient data by default.