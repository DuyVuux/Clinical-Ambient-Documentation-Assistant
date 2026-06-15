# ViMedCSS Task Brief

## Context

Week 5 produced an accepted PhoWhisper VietMed checkpoint. Week 6 continues with a controlled ViMedCSS progressive adaptation track.

## Primary objective

Fine-tune PhoWhisper progressively on `tensorxt/ViMedCSS`, starting from the Week 5 VietMed checkpoint.

## Why progressive?

ViMedCSS is expected to be noisy and code-switching heavy. Jumping directly to full training may waste GPU time and can cause catastrophic forgetting on the previous VietMed domain.

## Run sequence

| Run | Role |
|---|---|
| Run 0 | Baseline only, no training |
| Run A | Smoke test 100–200 samples |
| Run B | Mini adaptation 500–1000 samples |
| Run C | Balanced strategic subset, 3–5h audio |
| Run D | Optional 8–10h run only if Run C passes |
| Full run | Only with stable GPU/cloud resources |

## Split policy

| ViMedCSS split | Usage |
|---|---|
| train | training only |
| validation | model selection |
| test | final/reporting only |
| hard | stress/reporting only |

## Guardrails

- Do not self-split train/validation/test/hard.
- Do not train on validation/test/hard.
- Do not select checkpoint using test/hard.
- Do not store full dataset locally on laptop.
- Do not use GPU runtime just to download data.
