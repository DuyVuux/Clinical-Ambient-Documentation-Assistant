#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant}"
VIMEDCSS_ROOT="$PROJECT_ROOT/experiments/asr/vimedcss"

mkdir -p \
  "$VIMEDCSS_ROOT/data_audit" \
  "$VIMEDCSS_ROOT/manifests/"{raw,run0,runA,runB,runC,runD_optional,forgetting_eval} \
  "$VIMEDCSS_ROOT/preprocessing/"{subset_archives,materialized_subsets,logs} \
  "$VIMEDCSS_ROOT/baseline/"{run0_original_phowhisper,run0_week5_checkpoint} \
  "$VIMEDCSS_ROOT/finetune/"{runA_smoke_200,runB_mini_1000,runC_balanced_4h,runD_medium_8h_optional} \
  "$VIMEDCSS_ROOT/final_model/selected_model" \
  "$VIMEDCSS_ROOT/reports"

for split in train validation test hard; do
  src="$VIMEDCSS_ROOT/manifests/vimedcss_${split}_raw.jsonl"
  dst="$VIMEDCSS_ROOT/manifests/raw/vimedcss_${split}_raw.jsonl"
  if [[ -f "$src" && ! -f "$dst" ]]; then
    cp "$src" "$dst"
  fi
done

cat > "$VIMEDCSS_ROOT/reports/VIMEDCSS_TASK_BRIEF.md" <<'MD'
# ViMedCSS Task Brief

## Context

The project is continuing from the Week 5 PhoWhisper VietMed checkpoint to a progressive ViMedCSS adaptation track.

## Priority

Fine-tune PhoWhisper on ViMedCSS progressively, starting from the Week 5 VietMed checkpoint.

## Dataset

`tensorxt/ViMedCSS`

## Main risk

The dataset is noisy and code-switching heavy. Therefore, the track must include audit, baseline, controlled subset selection, progressive fine-tuning, and forgetting checks.

## Run sequence

- Run 0: baseline, no training
- Run A: smoke test 100–200 samples
- Run B: mini adaptation 500–1000 samples
- Run C: balanced strategic subset 3–5 hours
- Run D: optional medium run 8–10 hours
- Full run: only with stable GPU/cloud
MD

cat > "$VIMEDCSS_ROOT/reports/COLAB_CPU_GPU_PROTOCOL.md" <<'MD'
# Colab CPU/GPU Protocol for ViMedCSS

## CPU runtime

Use CPU runtime for dataset streaming, schema inspection, metadata audit, manifest creation, subset selection, and archive creation.

Do not enable T4 just to download or prepare data.

## GPU runtime

Use GPU runtime only for baseline, fine-tuning, evaluation, and forgetting checks.

## Drive policy

Google Drive is persistent storage. Do not train directly from Drive.

Correct flow:

```text
Drive archive → copy to /content → extract → train/eval from /content → save results back to Drive
```
MD