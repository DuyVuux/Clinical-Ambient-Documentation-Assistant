# Day 1 Week 4 — Audio QA Report

## Objective
Audit VietMed audio before preprocessing.

## Dataset
- Train: 600
- Dev: 200

## Key findings
| Check | Train count | Dev count |
|---|---:|---:|
| too_short | 0 | 0 |
| too_quiet | 0 | 0 |
| clipping_risk | 0 | 0 |
| long_leading_silence | 2 | 1 |
| long_trailing_silence | 3 | 1 |
| edge_loss_risk | 110 | 29 |

## Decision
Preprocessing is **necessary**. 
Due to a high rate of `edge_loss_risk` (18.3% in train, 14.5% in dev), the audio boundaries are significantly weaker, leading to a risk of the ASR model losing the first and last words.
Global loudness issues (`too_quiet`, `clipping_risk`) are non-existent.

**Priority:** We will focus entirely on VAD padding techniques (e.g., 200ms, 300ms, 500ms padding combined with Voice Activity Detection) to provide adequate context at the boundaries.

## Next step
Create preprocessing variants.