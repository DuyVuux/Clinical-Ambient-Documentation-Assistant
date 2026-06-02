# Annotation Notes — SYN_OUT_004

## Main annotation goals

- Test negation of chest pain.
- Test negation of dyspnea.
- Test negation of drug allergy.
- Test negation of hemoptysis.
- Test medication history with one present item and one absent item.
- Test source attribution for every clinical fact.

## Critical negation cases

1. "Em không đau ngực" must be:
   - normalized_text: đau ngực
   - assertion: absent

2. "Không khó thở" must be:
   - normalized_text: khó thở
   - assertion: absent

3. "Chưa từng dị ứng thuốc" must be:
   - fact_type: allergy
   - normalized_text: dị ứng thuốc
   - assertion: absent

4. "Không ho ra máu" must be:
   - fact_type: red_flag
   - normalized_text: ho ra máu
   - assertion: absent

## Safety warning

Do not convert "không đau ngực" into "đau ngực". This is a critical clinical safety error.

## Known limitations

- No real audio yet.
- Timestamp is estimated.
- No physical exam or lab result.
- SOAP assessment must remain conservative.
