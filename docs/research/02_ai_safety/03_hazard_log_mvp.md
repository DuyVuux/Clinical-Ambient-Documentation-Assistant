## Mục tiêu file
Hazard log rút gọn cho intern MVP.

## Risk Scoring
Severity:
1 = negligible
2 = minor
3 = moderate
4 = serious
5 = catastrophic

Likelihood:
1 = rare
2 = unlikely
3 = possible
4 = likely
5 = frequent

Risk Score = Severity x Likelihood

For intern MVP:
- Risk score > 10 requires mitigation.
- Residual risk should be <= 5 where possible.

| Risk ID | Hazard | Cause | Potential Harm | Initial S | Initial L | Mitigation | Residual Risk | Owner | Monitoring |
|---|---|---|---:|---:|---:|---|---:|---|---|
| CR-01 | Omitted red flag symptom | LLM summarizes too aggressively | Delay in urgent diagnosis | 5 | 3 | Red flag checklist, no aggressive summarization, doctor confirmation | 5 | Clinical reviewer | Red flag omission count |
| CR-02 | Wrong medication name | ASR error or LLM normalization error | Wrong medication in note | 4 | 3 | Medication flag, source quote, doctor confirmation | 4 | ML/dev + doctor reviewer | Medication error rate |
| CR-03 | Wrong dosage/frequency | ASR hears number incorrectly | Overdose/underdose risk | 5 | 3 | Dosage always requires confirmation, highlight numeric entities | 5 | Doctor reviewer | Dosage error count |
| CR-04 | Allergy omitted | Allergy not mentioned or missed | Unsafe medication plan | 5 | 3 | Missing allergy flag required | 5 | Doctor reviewer | Missing allergy cases |
| CR-05 | Negation reversed | "Không đau ngực" becomes "đau ngực" | Wrong clinical meaning | 5 | 2 | Negation detector/checklist, source quote | 5 | ML/dev | Negation error rate |
| CR-06 | AI invents diagnosis | LLM fills missing assessment | Misleading medical record | 4 | 3 | Strict prompt grounding, assessment requires doctor source | 4 | ML/dev | Hallucinated diagnosis count |
| CR-07 | Plan from non-doctor | Caregiver/nurse question treated as plan | Incorrect treatment plan | 4 | 3 | Speaker role policy, plan only from doctor | 4 | ML/dev | Plan attribution errors |
| CR-08 | Unknown speaker used as fact | Diarization fails | Wrong source attribution | 3 | 3 | Unknown speaker requires review | 3 | ML/dev | Unknown speaker facts |
| CR-09 | Low audio quality causes unsafe transcript | Noise/overlap/soft speech | Chain of downstream errors | 4 | 3 | Input quality warning, no auto-draft if too unclear | 4 | ML/dev | Low-quality sessions |
| CR-10 | Doctor rubber-stamps AI draft | Automation bias | Errors enter final note | 5 | 3 | Mandatory checklist, explicit confirmation, error highlighting | 5 | Product/clinical | Review time, unchecked items |
| CR-11 | Audit gap | No event trail | Cannot investigate incident | 3 | 3 | Append-only audit log | 3 | Dev | Missing log events |
| CR-12 | Unsupported fact appears in SOAP note | Renderer/LLM adds fact without source | False documentation | 4 | 3 | No fact without source; validation before render | 4 | ML/dev | Unsupported facts count |

## MVP Rule
Any risk involving medication, dosage, allergy, diagnosis, plan, red flags, or negation must require doctor confirmation.