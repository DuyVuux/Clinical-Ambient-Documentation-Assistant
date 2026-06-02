# Annotation Notes — SYN_OUT_002

## Main annotation goals

- Test gastrointestinal symptom extraction.
- Test duration extraction.
- Test frequency extraction.
- Test red-flag negation.
- Test exposure/risk-context extraction.
- Test dehydration-related signs.
- Test source attribution from clinical facts to transcript segments.
- Test conservative SOAP-lite generation.

## Important safety points

1. "Không thấy máu" must be extracted as:
   - normalized_text: máu trong phân
   - assertion: negated

2. "Không thấy phân đen" must be extracted as:
   - normalized_text: phân đen
   - assertion: negated

3. "Không sốt cao" must be extracted as:
   - normalized_text: sốt cao
   - assertion: negated

4. "Không nôn ra máu" must be extracted as:
   - normalized_text: nôn ra máu
   - assertion: negated

5. "Hơi buồn nôn" must not be confused with "nôn nhiều" or "nôn ra máu".

6. "Ăn hải sản ở ngoài" is an exposure/context fact, not a confirmed diagnosis.

7. The SOAP assessment must not state a definitive diagnosis such as "ngộ độc thực phẩm" unless doctor explicitly confirms it.

## Known limitations

- Timestamp is estimated because this case is script-only.
- No real audio yet.
- No physical exam, vital signs, stool test or lab result.
- Assessment is conservative and must not be treated as final diagnosis.