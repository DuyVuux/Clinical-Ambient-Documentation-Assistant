# Week 6 Day 1 — ViMedCSS Execution Readiness Scripts

Bộ script này phục vụ **ngày 1 tuần 6** cho track:

```text
ViMedCSS Progressive Fine-tuning
```

Mục tiêu ngày 1:

```text
1. Chuẩn hóa skeleton experiments/asr/asr_vimedcss/
2. Không tạo folder theo ngày
3. Giữ inventory report cũ
4. Tạo task brief, Colab CPU/GPU protocol, Drive policy
5. Kiểm tra raw manifests, Week 5 checkpoint, Drive path
6. Xuất WEEK6_EXECUTION_READINESS_CHECK.md
```

## Cách dùng trên máy local

Copy thư mục `scripts/asr_vimedcss/` trong gói này vào project của bạn, rồi chạy:

```bash
PROJECT_ROOT="/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
DRIVE_ROOT="/content/drive/MyDrive/clinical_asr_vimedcss"
WEEK5_CKPT="$PROJECT_ROOT/experiments/asr/finetune/week5/run_01_phowhisper_medium_conservative/best_model"

bash scripts/asr_vimedcss/00_prepare_vimedcss_day1.sh \
  "$PROJECT_ROOT" \
  "$DRIVE_ROOT" \
  "$WEEK5_CKPT"
```

Sau đó chạy validate:

```bash
python scripts/asr_vimedcss/00_validate_vimedcss_day1_readiness.py \
  --project_root "$PROJECT_ROOT" \
  --drive_root "$DRIVE_ROOT" \
  --week5_checkpoint "$WEEK5_CKPT"
```

## Cách dùng trên Colab CPU

Trên Colab CPU, mount Drive trước:

```python
from google.colab import drive
drive.mount("/content/drive")
```

Sau đó clone/copy project skeleton nhẹ hoặc upload scripts vào `/content`, rồi chạy:

```bash
PROJECT_ROOT="/content/Clinical-Ambient-Documentation-Assistant"
DRIVE_ROOT="/content/drive/MyDrive/clinical_asr_vimedcss"
WEEK5_CKPT="/content/drive/MyDrive/clinical_asr_models/phowhisper_vietmed_week5_checkpoint"

bash scripts/asr_vimedcss/00_prepare_vimedcss_day1.sh \
  "$PROJECT_ROOT" \
  "$DRIVE_ROOT" \
  "$WEEK5_CKPT"

python scripts/asr_vimedcss/00_validate_vimedcss_day1_readiness.py \
  --project_root "$PROJECT_ROOT" \
  --drive_root "$DRIVE_ROOT" \
  --week5_checkpoint "$WEEK5_CKPT"
```

## Artifact sinh ra

```text
experiments/asr/vimedcss/
├── baseline/
├── data_audit/
├── final_model/
├── finetune/
├── manifests/
│   ├── raw/
│   ├── run0/
│   ├── runA/
│   ├── runB/
│   ├── runC/
│   ├── runD_optional/
│   └── forgetting_eval/
├── preprocessing/
│   ├── subset_archives/
│   ├── materialized_subsets/
│   ├── logs/
│   └── PREPROCESSING_POLICY_VIMEDCSS.md
└── reports/
    ├── VIMEDCSS_TASK_BRIEF.md
    ├── COLAB_CPU_GPU_PROTOCOL.md
    ├── DRIVE_STORAGE_POLICY.md
    ├── TTS_DATA_REQUEST_MESSAGE.md
    ├── WEEK6_ENVIRONMENT_CONFIG.json
    └── WEEK6_EXECUTION_READINESS_CHECK.md
```

## Ghi chú quan trọng

- Ngày 1 **không tải full ViMedCSS về local**.
- Ngày 1 **không train**.
- Ngày 1 **không bật GPU chỉ để tải data**.
- Local chỉ quản lý code/report/manifest nhẹ.
- Archive/audio/checkpoint lớn nên nằm ở Google Drive.
