## Mục tiêu file
Đo gánh nặng review của bác sĩ và mức độ sử dụng được của note.

## Required Data to Store
For each session:
- ai_draft_text
- doctor_edited_text
- confirmed_text
- safety_flags_before_review
- safety_flags_after_review
- review_started_at
- review_confirmed_at
- doctor_action_log

## Metrics

### Edit Distance
Calculate character-level or word-level edit distance between:
- AI draft and doctor-edited note.

Use this to estimate how much doctor had to fix.

### Edit Ratio
Formula:
Edit Ratio = edit_distance / length_of_ai_draft

Interpretation:
- < 10%: minimally edited
- 10–30%: moderate edits
- > 30%: heavy edits

### Minimally-Edited Note Rate
Formula:
MNR = notes_with_edit_ratio_below_10_percent / total_notes

Intern MVP target:
- >= 50% acceptable
- >= 70% strong

### Review Time
Formula:
review_confirmed_at - review_started_at

Use cautiously.
Do not claim time saved unless baseline exists.

### Safety Flag Resolution Rate
Formula:
resolved_or_acknowledged_flags / total_flags

High severity flags must be acknowledged or resolved before confirmation.

### Note Usable After Light Edits
Reviewer marks:
- yes
- no
- borderline

Definition:
A note is usable after light edits if the doctor does not need to rewrite entire SOAP sections and no critical clinical facts are wrong.

### Doctor Trust Rating
Simple 1–5 scores:
- factual accuracy;
- clinical usefulness;
- review burden;
- safety confidence;
- would use again.

## UI Requirement
Doctor reviewer should be able to:
- edit note;
- flag AI error;
- resolve safety flag;
- confirm note;
- reject note.

## MVP Report Table

| Case ID | Edit Ratio | Review Time | High Flags | Resolved Flags | Usable After Light Edits | Doctor Trust | Notes |
|---|---:|---:|---:|---:|---|---:|---|