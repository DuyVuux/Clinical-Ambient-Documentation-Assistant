# ASR Primary/Backup Protocol v0.1

## Roles

| Role | Model | Purpose |
|---|---|---|
| Primary | `khanhld/chunkformer-ctc-large-vie` | Main ASR inference |
| Backup | `phowhisper_backup_v0_1` | Fallback ASR model |

## Default inference

Use ChunkFormer as primary.

## Backup activation

Use PhoWhisper backup if:

1. Primary model fails to load.
2. Primary inference crashes.
3. Primary output is empty or too short.
4. Primary output triggers high clinical risk.
5. Manual evaluation requires comparison.

## Double-run mode

Run both models for:

1. Clinical safety stress testing.
2. High-risk samples.
3. Evaluation only.
4. Model disagreement analysis.

## Guardrails

- ASR output is not clinical truth.
- Downstream clinical facts require source attribution.
- Doctor review remains required before final clinical note.
- test_holdout is not used until final evaluation protocol is frozen.