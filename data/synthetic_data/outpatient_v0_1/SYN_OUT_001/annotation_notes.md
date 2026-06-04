# Annotation Notes — SYN_OUT_001

## Main annotation goals

- Test symptom extraction.
- Test negation extraction.
- Test medication + dose extraction.
- Test allergy negation.
- Test source attribution from fact to segment.
- Test SOAP-lite note generation.

## Required clinical facts

| Fact | Assertion | Source segment | Safety group |
|---|---|---|---|
| ho khoảng 3 ngày | present | seg_002 | Temporal Error |
| ho khan, rát họng | present | seg_004 | Clinical Fact |
| sốt nhẹ tối qua, khoảng 37.8°C | present | seg_006 | Temporal / Numeric Error |
| đau ngực | absent | seg_008 | Negation Error |
| khó thở | absent | seg_008 | Missing Critical Finding / Negation Error |
| dị ứng thuốc | absent | seg_010 | Allergy Error |
| paracetamol 500mg, một viên, tối qua | present | seg_012 | Medication Dose / Unit Numeric Error |
| nghỉ ngơi, uống nước, theo dõi, tái khám nếu nặng | recommended | seg_013 | Plan / Follow-up |

## Important safety points

1. "Không đau ngực" must be extracted as:
   - normalized_text: đau ngực
   - assertion: negated

2. "Không khó thở" must be extracted as:
   - normalized_text: khó thở
   - assertion: negated

3. "Chưa từng dị ứng thuốc" must be extracted as:
   - fact_type: allergy
   - assertion: negated

4. "Paracetamol năm trăm miligam" must be normalized as:
   - medication: paracetamol
   - dose: 500 mg

## Known limitations

- Timestamp is estimated because this case is script-only.
- No real audio yet.
- No physical exam or lab result.
- Assessment is conservative and must not be treated as final diagnosis.