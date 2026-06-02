# Annotation Notes — SYN_OUT_001

## Main annotation goals

- Test symptom extraction.
- Test negation extraction.
- Test medication + dose extraction.
- Test allergy negation.
- Test source attribution from fact to segment.
- Test SOAP-lite note generation.

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