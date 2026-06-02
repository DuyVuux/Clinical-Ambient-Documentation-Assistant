# Annotation Notes — SYN_OUT_005

## Main annotation goals

- Test negation of hematemesis (nôn ra máu).
- Test negation of hematochezia (đi ngoài ra máu).
- Test negation of melena (phân đen).
- Test negation of drug allergy.
- Test distinction between "buồn nôn" (present) and "nôn" (absent) from same sentence.
- Test source attribution for every clinical fact.

## Critical negation cases

1. "Không nôn ra máu" must be:
   - fact_type: red_flag
   - normalized_text: nôn ra máu
   - assertion: absent

2. "Không đi ngoài ra máu" must be:
   - fact_type: red_flag
   - normalized_text: đi ngoài ra máu
   - assertion: absent

3. "Không có phân đen" must be:
   - fact_type: red_flag
   - normalized_text: phân đen
   - assertion: absent

4. "Buồn nôn nhưng không nôn" must produce TWO facts:
   - buồn nôn: assertion = present
   - nôn: assertion = absent

5. "Chưa từng dị ứng thuốc" must be:
   - fact_type: allergy
   - assertion: absent

## Safety warning

Do not merge "buồn nôn" and "nôn" into a single present fact.

## Known limitations

- No real audio yet.
- Timestamp is estimated.
- No physical exam or lab result.
- SOAP assessment must remain conservative.
