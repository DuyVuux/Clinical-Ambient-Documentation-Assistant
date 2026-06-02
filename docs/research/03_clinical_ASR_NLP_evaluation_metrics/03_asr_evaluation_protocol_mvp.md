## Mục tiêu file
Quy trình đánh giá ASR cho MVP.

## Input Data
Each ASR test case should include:
- audio_file_path
- ground_truth_transcript
- asr_transcript
- speaker labels if available
- list of expected medical terms
- list of expected critical entities
- list of expected negations

## Required Audio Case Types
Create at least:

### A01 - Simple outpatient
Basic symptom discussion.

### A02 - Multiple speakers
Doctor, patient, optional caregiver.

### A03 - Medication and dosage
Includes medication name, dose, frequency, duration.

### A04 - Lab tests
Includes tests such as HbA1c, CRP, creatinine, blood pressure, SpO2.

### A05 - Negation
Includes "không sốt", "không đau ngực", "không dị ứng thuốc".

### A06 - Noisy audio
Light clinic background noise.

### A07 - Regional accent
Northern/Central/Southern accent variation if available.

## Metrics to Calculate

### 1. WER
Use generic transcript comparison.
Report only as baseline.

### 2. CharER
Useful for Vietnamese spelling and diacritics.

### 3. mWER
Calculate on medical dictionary terms only.

Medical dictionary categories:
- symptoms;
- medications;
- dosage;
- labs;
- diagnoses;
- allergies;
- red flags;
- negations.

### 4. Medical Word Hit Rate
Correctly recognized medical terms divided by total expected medical terms.

### 5. Negation Error Count
Count each negation reversal or deletion.

Examples:
Expected: không đau ngực
ASR: đau ngực
Error type: critical negation error

### 6. Critical Entity Error Count
Track:
- wrong medication;
- wrong dose;
- wrong route;
- wrong frequency;
- wrong allergy;
- wrong lab value;
- wrong diagnosis mention.

## MVP ASR Report Format

For each case:

| Case ID | WER | CharER | mWER | Medical Word Hit Rate | Negation Errors | Critical Entity Errors | Notes |
|---|---:|---:|---:|---:|---:|---:|---|

## Interpretation Rule
Do not say ASR is safe because WER is low.
ASR is only clinically acceptable if critical terms, negations, medication, dosage, and allergy are captured correctly or flagged for doctor confirmation.

## Fallback Rule
If ASR setup is unstable, allow pasted transcript fallback.
But evaluation report must clearly mark:
- ASR not evaluated;
- transcript quality assumed;
- safety evaluation continues from transcript stage.