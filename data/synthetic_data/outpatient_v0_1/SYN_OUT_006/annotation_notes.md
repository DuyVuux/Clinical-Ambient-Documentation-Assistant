# Annotation Notes — SYN_OUT_006

## Main annotation goals

- Test distinction between "khó chịu vùng ngực" (present symptom) and "đau ngực" (absent).
- Test negation of dyspnea.
- Test negation of jaw radiation, left arm radiation, cold sweating (cardiac red flags).
- Test negation of syncope and limb weakness (neurological red flags).
- Test social history extraction (caffeine intake, sleep deprivation, work stress).
- Test source attribution for every clinical fact.

## Critical negation cases

1. "Không phải đau ngực" must be:
   - normalized_text: đau ngực
   - assertion: absent
   - Must NOT be confused with "khó chịu vùng ngực" which is a separate present symptom.

2. "Không khó thở" must be:
   - normalized_text: khó thở
   - assertion: absent

3. "Không lan lên hàm" must be:
   - fact_type: red_flag
   - normalized_text: đau lan lên hàm
   - assertion: absent

4. "Không lan ra tay trái" must be:
   - fact_type: red_flag
   - normalized_text: đau lan ra tay trái
   - assertion: absent

5. "Không vã mồ hôi lạnh" must be:
   - fact_type: red_flag
   - assertion: absent

6. "Không ngất" must be:
   - fact_type: red_flag
   - normalized_text: ngất
   - assertion: absent

7. "Không yếu liệt tay chân" must be:
   - fact_type: red_flag
   - assertion: absent

## Safety warning

Do not convert "khó chịu vùng ngực" into "đau ngực present". This is semantically different and clinically critical.

## Known limitations

- No real audio yet.
- Timestamp is estimated.
- No physical exam, ECG, or lab result.
- SOAP assessment must remain conservative.
