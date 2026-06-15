#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant}"
DRIVE_ROOT="${DRIVE_ROOT:-/content/drive/MyDrive/clinical_asr_vimedcss}"
WEEK5_CKPT="${WEEK5_CKPT:-$PROJECT_ROOT/experiments/asr/finetune/week5/run_01_phowhisper_medium_conservative/best_model}"

cd "$PROJECT_ROOT"

bash scripts/vimedcss/00_prepare_vimedcss_day1.sh \
  "$PROJECT_ROOT" \
  "$DRIVE_ROOT" \
  "$WEEK5_CKPT"

python scripts/vimedcss/00_validate_vimedcss_day1_readiness.py \
  --project_root "$PROJECT_ROOT" \
  --drive_root "$DRIVE_ROOT" \
  --week5_checkpoint "$WEEK5_CKPT"
