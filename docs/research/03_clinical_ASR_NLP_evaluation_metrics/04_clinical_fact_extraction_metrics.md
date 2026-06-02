## Mục tiêu file
Đánh giá chất lượng trích xuất clinical facts từ transcript.

## Required Ground Truth Per Case
Each case must have expected facts manually written.

Example:

{
  "case_id": "GI_A01",
  "expected_facts": [
    {
      "fact_text": "Bệnh nhân đau thượng vị 3 ngày",
      "fact_type": "symptom",
      "speaker": "Patient",
      "note_section": "Subjective",
      "criticality": "medium"
    },
    {
      "fact_text": "Bệnh nhân không sốt",
      "fact_type": "negation",
      "speaker": "Patient",
      "note_section": "Subjective",
      "criticality": "medium"
    },
    {
      "fact_text": "Chưa ghi nhận dị ứng thuốc",
      "fact_type": "allergy",
      "speaker": "Patient",
      "note_section": "Subjective",
      "criticality": "high"
    }
  ]
}

## Metrics

### Captured Entity Rate
Measures recall.

Formula:
Captured Entity Rate = matched_expected_facts / total_expected_facts

### Accurate Entity Rate
Measures precision.

Formula:
Accurate Entity Rate = correct_extracted_facts / total_extracted_facts

### Unsupported Fact Count
Facts that appear in AI output but have no transcript evidence.

### Source Attribution Completeness
Each extracted fact must include:
- source_quote;
- speaker;
- timestamp if available;
- fact_type;
- note_section;
- confidence;
- requires_doctor_confirmation.

Formula:
Source Attribution Completeness = facts_with_complete_source / total_facts

### Critical Entity Capture Rate
Measures capture of high-risk entities:
- medication;
- dosage;
- allergy;
- red flag;
- diagnosis mention;
- plan;
- negation.

Formula:
Critical Entity Capture Rate = captured_critical_entities / total_expected_critical_entities

## Matching Rules
A fact is considered matched if:
- meaning is clinically equivalent;
- correct speaker;
- correct section;
- no reversed negation;
- no wrong value;
- has source quote.

## Major Error Examples
- wrong speaker;
- wrong medication;
- wrong dosage;
- allergy reversed;
- negation reversed;
- diagnosis created without doctor source;
- plan created from non-doctor speech.

## MVP Target
- Source Attribution Completeness: 100%
- Critical Entity Capture Rate: >= 90%
- Unsupported Critical Fact Count: 0
- Plan-from-non-doctor: 0