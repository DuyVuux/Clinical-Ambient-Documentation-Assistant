# Annotation Notes — SYN_OUT_003

## Main annotation goals

- Test headache symptom extraction.
- Test duration extraction.
- Test neurological red-flag negation.
- Test sleep-related symptom extraction.
- Test lifestyle factor extraction.
- Test source attribution from clinical facts to transcript segments.
- Test conservative SOAP-lite generation.

## Important safety points

1. "Không đau dữ dội" must be extracted as:
   - normalized_text: đau đầu dữ dội
   - assertion: negated

2. "Không đột ngột" must be extracted as:
   - normalized_text: đau đầu khởi phát đột ngột
   - assertion: negated

3. "Không nhìn mờ" must be extracted as:
   - normalized_text: nhìn mờ
   - assertion: negated

4. "Không nói khó" must be extracted as:
   - normalized_text: nói khó
   - assertion: negated

5. "Không yếu liệt tay chân" must be extracted as:
   - normalized_text: yếu liệt tay chân
   - assertion: negated

6. "Không có co giật, không ngất" must be extracted as two separate negated red-flag facts.

7. "Đau dữ dội nhất từ trước đến nay" is a red flag and must remain negated.

8. "Uống cà phê buổi tối" and "làm việc máy tính khuya" are lifestyle/context factors, not diagnoses.

9. The SOAP assessment must not state a definitive neurological diagnosis.

## Known limitations

- Timestamp is estimated because this case is script-only.
- No real audio yet.
- No neurological exam.
- No vital signs or imaging.
- Assessment is conservative and must not be treated as final diagnosis.