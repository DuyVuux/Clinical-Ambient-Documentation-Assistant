# Week 6 Plan — Clinical ASR Safety Guardrails

## Condition

Week 5 accepted fine-tuned PhoWhisper-medium as backup model v0.1.

## Objective

Improve clinical safety around ASR outputs rather than further lowering generic WER.

## Tasks

1. Build negation checker.
2. Build medical term checker.
3. Build medication/dose/unit checker.
4. Compare ChunkFormer primary vs PhoWhisper backup on clinical errors.
5. Prepare final test_holdout evaluation protocol.

## Guardrails

- test_holdout still not used until final evaluation protocol is frozen.