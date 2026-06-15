# Google Drive Storage Policy — ViMedCSS

## Drive root

`/content/drive/MyDrive/clinical_asr_vimedcss`

## Purpose

Keep local laptop lightweight by storing heavy artifacts on Google Drive.

## Recommended Drive structure

```text
/content/drive/MyDrive/clinical_asr_vimedcss/
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
```

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

Do not train by streaming audio directly from Drive. Copy archive to `/content`, extract there, train/evaluate from local Colab disk, then copy outputs back to Drive.
