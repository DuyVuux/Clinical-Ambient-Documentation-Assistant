# Medical ASR Error Taxonomy v0.1

## Error groups

| Error group | Meaning | Example | Severity |
|---|---|---|---|
| negation_deletion | Model misses negation cue | không đau ngực → đau ngực | critical |
| symptom_deletion | Model misses clinical symptom | khó thở missing | high |
| medication_error | Model changes medication name | paracetamol → ... | high |
| dose_unit_error | Model changes dose/unit | 500 mg → 50 mg | high |
| allergy_error | Model misses allergy phrase | chưa từng dị ứng thuốc missing | critical |
| numeric_error | Model changes number | 37.8 → 38.7 | moderate/high |
| temporal_error | Model misses time/duration | 3 ngày missing | moderate |
| insertion_hallucination | Model adds words not in audio | thêm bệnh/thuốc | high |
| dialect_term_error | Model mishears accent/dialect | local phrase wrong | moderate |

## Clinical priority

Critical errors matter more than average WER.