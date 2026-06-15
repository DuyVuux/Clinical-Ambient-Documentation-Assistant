#!/usr/bin/env bash
set -euo pipefail

# Week 6 Day 1 — ViMedCSS execution skeleton and readiness setup.
#
# Usage:
#   bash scripts/vimedcss/00_prepare_vimedcss_day1.sh \
#     "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant" \
#     "/content/drive/MyDrive/clinical_asr_vimedcss" \
#     "/path/to/week5/best_model"
#
# This script:
# - Creates the professional ViMedCSS skeleton.
# - Avoids day-based folders.
# - Preserves existing inventory/raw manifests.
# - Writes protocol/report templates.
# - Records Drive policy so heavy data stays off local disk.
# - Does not download full ViMedCSS.
# - Does not train.

PROJECT_ROOT="${1:-/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant}"
DRIVE_ROOT="${2:-/content/drive/MyDrive/clinical_asr_vimedcss}"
WEEK5_CKPT="${3:-$PROJECT_ROOT/experiments/asr/finetune/week5/run_01_phowhisper_medium_conservative/best_model}"

VIMEDCSS_ROOT="$PROJECT_ROOT/experiments/asr/vimedcss"
SCRIPT_ROOT="$PROJECT_ROOT/scripts/vimedcss"

mkdir -p "$SCRIPT_ROOT"
mkdir -p "$VIMEDCSS_ROOT"

# Core module folders.
mkdir -p "$VIMEDCSS_ROOT/data_audit"
mkdir -p "$VIMEDCSS_ROOT/manifests"
mkdir -p "$VIMEDCSS_ROOT/preprocessing"
mkdir -p "$VIMEDCSS_ROOT/baseline"
mkdir -p "$VIMEDCSS_ROOT/finetune"
mkdir -p "$VIMEDCSS_ROOT/final_model"
mkdir -p "$VIMEDCSS_ROOT/reports"

# Manifest folders.
mkdir -p "$VIMEDCSS_ROOT/manifests/raw"
mkdir -p "$VIMEDCSS_ROOT/manifests/run0"
mkdir -p "$VIMEDCSS_ROOT/manifests/runA"
mkdir -p "$VIMEDCSS_ROOT/manifests/runB"
mkdir -p "$VIMEDCSS_ROOT/manifests/runC"
mkdir -p "$VIMEDCSS_ROOT/manifests/runD_optional"
mkdir -p "$VIMEDCSS_ROOT/manifests/forgetting_eval"

# Preprocessing and archive folders.
mkdir -p "$VIMEDCSS_ROOT/preprocessing/subset_archives"
mkdir -p "$VIMEDCSS_ROOT/preprocessing/materialized_subsets"
mkdir -p "$VIMEDCSS_ROOT/preprocessing/logs"

# Baseline folders.
mkdir -p "$VIMEDCSS_ROOT/baseline/run0_original_phowhisper"
mkdir -p "$VIMEDCSS_ROOT/baseline/run0_week5_checkpoint"

# Fine-tune run folders.
mkdir -p "$VIMEDCSS_ROOT/finetune/runA_smoke_200"
mkdir -p "$VIMEDCSS_ROOT/finetune/runB_mini_1000"
mkdir -p "$VIMEDCSS_ROOT/finetune/runC_balanced_4h"
mkdir -p "$VIMEDCSS_ROOT/finetune/runD_medium_8h_optional"

# Final model folder.
mkdir -p "$VIMEDCSS_ROOT/final_model/selected_model"

# Create .gitkeep for empty dirs.
find "$VIMEDCSS_ROOT" -type d -empty -exec touch "{}/.gitkeep" \;

# Preserve existing raw manifests if they currently live directly under manifests/.
for split in train validation test hard; do
  src="$VIMEDCSS_ROOT/manifests/vimedcss_${split}_raw.jsonl"
  dst="$VIMEDCSS_ROOT/manifests/raw/vimedcss_${split}_raw.jsonl"

  if [[ -f "$src" && ! -f "$dst" ]]; then
    cp "$src" "$dst"
    echo "[INFO] copied raw manifest: $src -> $dst"
  fi
done

# Also preserve existing inventory artifacts by leaving them in place.
# We only generate missing protocol/task files.

cat > "$VIMEDCSS_ROOT/reports/VIMEDCSS_TASK_BRIEF.md" <<'MD'
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
MD

cat > "$VIMEDCSS_ROOT/reports/COLAB_CPU_GPU_PROTOCOL.md" <<'MD'
# Colab CPU/GPU Protocol for ViMedCSS

## Principle

Local laptop coordinates the experiment. Google Drive stores heavy artifacts. Colab CPU prepares data. Colab GPU trains/evaluates.

## Local laptop

Allowed:

- write code
- manage repo
- keep small manifests/reports
- inspect JSONL/CSV metadata

Not allowed:

- download full ViMedCSS
- train PhoWhisper-medium
- store multiple large checkpoints
- let Hugging Face cache fill `/home`

## Google Drive

Use Drive as persistent storage for:

- subset archives
- predictions
- metrics
- reports
- best checkpoints
- final models

## Colab CPU

Use CPU runtime for:

- dataset streaming
- schema verification
- manifest creation
- sample-based audit
- subset materialization
- `.tar.gz` archive creation

Do not enable T4 just to download data.

## Colab GPU/T4

Use GPU runtime only for:

- baseline ASR
- fine-tuning
- evaluation
- forgetting check

## Correct archive flow

```text
Drive archive
→ copy to /content
→ extract in /content
→ train/eval from /content
→ copy predictions/metrics/checkpoints back to Drive
```

## Cache policy

Recommended Colab cache:

```text
/content/vimedcss_work/hf_cache
/content/vimedcss_work/datasets_cache
/content/vimedcss_work/runs
```
MD

cat > "$VIMEDCSS_ROOT/reports/DRIVE_STORAGE_POLICY.md" <<MD
# Google Drive Storage Policy — ViMedCSS

## Drive root

\`$DRIVE_ROOT\`

## Purpose

Keep local laptop lightweight by storing heavy artifacts on Google Drive.

## Recommended Drive structure

\`\`\`text
$DRIVE_ROOT/
├── subset_archives/
├── baseline/
│   ├── run0_original_phowhisper/
│   └── run0_week5_checkpoint/
├── finetune/
│   ├── runA_smoke_200/
│   ├── runB_mini_1000/
│   ├── runC_balanced_4h/
│   └── runD_medium_8h_optional/
├── final_model/
├── reports/
└── logs/
\`\`\`

## Local-to-Drive rule

Local should keep:

- code
- small JSONL manifests
- CSV summaries
- Markdown reports

Drive should keep:

- audio archives
- model checkpoints
- prediction files
- metric outputs
- exported final model

## Training rule

Do not train by streaming audio directly from Drive. Copy archive to \`/content\`, extract there, train/evaluate from local Colab disk, then copy outputs back to Drive.
MD

cat > "$VIMEDCSS_ROOT/reports/TTS_DATA_REQUEST_MESSAGE.md" <<'MD'
Em chào mọi người, hiện tại em đang chuyển sang fine-tune PhoWhisper trên bộ `tensorxt/ViMedCSS` theo hướng ASR y khoa tiếng Việt có code-switching.

Anh/chị cho em hỏi nhóm mình có bộ dữ liệu audio + transcript đã label thêm cho ViMedCSS hoặc các tập y khoa/code-switching tương tự không ạ?

Nếu có, anh/chị có thể cho em xin:
1. danh sách split hoặc manifest,
2. format audio/transcript,
3. thông tin license/allowed use,
4. có dùng được cho training/evaluation nội bộ không,
5. các ghi chú về noise, speaker, accent, hoặc code-switching term.

Em sẽ dùng trước cho baseline, audit chất lượng audio, rồi mới đưa vào fine-tune có kiểm soát, không trộn trực tiếp vào test set.
MD

cat > "$VIMEDCSS_ROOT/preprocessing/PREPROCESSING_POLICY_VIMEDCSS.md" <<'MD'
# ViMedCSS Preprocessing Policy

## Goal

Prepare ViMedCSS subsets for PhoWhisper progressive fine-tuning without corrupting medical/code-switching content.

## Allowed

- Decode audio to 16kHz mono when materializing subsets.
- Validate duration.
- Exclude broken/empty samples.
- Keep official splits.
- Preserve English medical terms and code-switching terms.
- Write stable JSONL manifests.
- Keep original `segment_text` as reference transcript.

## Not allowed

- Do not train on validation/test/hard.
- Do not normalize away English medical terms.
- Do not use aggressive text normalization before evaluation.
- Do not apply VAD/cropping blindly if audio is already segmented.
- Do not choose checkpoint from test/hard.
- Do not self-split ViMedCSS 60/40.

## Initial suspect filters

```text
duration_seconds < 1.0
duration_seconds > 25.0
num_words <= 1
text_len <= 3
audio missing/unreadable
segment_text missing/empty
```

## Code-switching preservation

Fields such as `cs_terms_list` and `cs_terms_count` must be preserved in run manifests when available.

## Official split usage

| Split | Usage |
|---|---|
| train | training only |
| validation | model selection |
| test | final/reporting only |
| hard | stress/reporting only |
MD

cat > "$VIMEDCSS_ROOT/reports/WEEK6_ENVIRONMENT_CONFIG.json" <<JSON
{
  "project_root": "$PROJECT_ROOT",
  "vimedcss_root": "$VIMEDCSS_ROOT",
  "drive_root": "$DRIVE_ROOT",
  "week5_checkpoint": "$WEEK5_CKPT",
  "dataset_id": "tensorxt/ViMedCSS",
  "track": "ViMedCSS Progressive Fine-tuning",
  "skeleton_version": "week6_day1_v1.0",
  "folder_policy": "module_based_not_day_based",
  "local_policy": "code_reports_manifests_only",
  "drive_policy": "heavy_artifacts_and_archives",
  "created_by": "Duy"
}
JSON

cat > "$VIMEDCSS_ROOT/reports/WEEK6_EXECUTION_READINESS_CHECK.md" <<MD
# Week 6 Execution Readiness Check

This file is initialized by \`00_prepare_vimedcss_day1.sh\`.

Run the validator to fill status:

\`\`\`bash
python scripts/vimedcss/00_validate_vimedcss_day1_readiness.py \\
  --project_root "$PROJECT_ROOT" \\
  --drive_root "$DRIVE_ROOT" \\
  --week5_checkpoint "$WEEK5_CKPT"
\`\`\`

## Initial setup

- Project root: \`$PROJECT_ROOT\`
- ViMedCSS root: \`$VIMEDCSS_ROOT\`
- Drive root: \`$DRIVE_ROOT\`
- Week 5 checkpoint: \`$WEEK5_CKPT\`

## Decision

PENDING_VALIDATION
MD

echo "[DONE] Week 6 Day 1 ViMedCSS skeleton prepared."
echo "[INFO] Project root:    $PROJECT_ROOT"
echo "[INFO] ViMedCSS root:   $VIMEDCSS_ROOT"
echo "[INFO] Drive root:      $DRIVE_ROOT"
echo "[INFO] Week5 ckpt:      $WEEK5_CKPT"
echo "[NEXT] Run: python scripts/vimedcss/00_validate_vimedcss_day1_readiness.py --project_root \"$PROJECT_ROOT\" --drive_root \"$DRIVE_ROOT\" --week5_checkpoint \"$WEEK5_CKPT\""
