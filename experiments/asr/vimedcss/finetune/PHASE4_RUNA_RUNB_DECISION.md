# Phase 4 — Run A/B Decision

## Status: **PROCEED_TO_RUN_C_WITH_CAUTION**

## Metrics

| Item | WER |
|---|---:|
| Run 0 ViMedCSS validation baseline | TBD |
| Run A smoke eval | 30.14% |
| Run B mini eval | 22.85% |
| Run B VietMed forgetting eval | TBD |
| Week 5 VietMed reference | 16.57% |

## Reasons

- Run 0 baseline metrics were not provided; Run B ran technically and forgetting is acceptable.

## Decision rule

- If Run B fails technically: fix script, do not run Run C.
- If Run B loss is flat/unstable: inspect data/preprocessing.
- If Run B improves ViMedCSS validation and does not strongly degrade VietMed dev: proceed to Run C.
