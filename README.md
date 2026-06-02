# Clinical Ambient Documentation Assistant

Hệ thống hỗ trợ bác sĩ ghi chép y bạ tự động từ hội thoại khám bệnh tiếng Việt.

Pipeline: Thu âm → ASR (Whisper/PhoWhisper) → Trích xuất clinical facts → SOAP note draft → Bác sĩ review & ký.

Chạy local, không gửi dữ liệu bệnh nhân ra ngoài.

## Cấu trúc thư mục

```
.
├── data/
│   ├── data_governance/         # Registry dataset, license, risk
│   ├── data_lake/
│   │   ├── bronze/public/       # Raw audio (Common Voice, FOSD, VietMed)
│   │   ├── silver/              # Audio chuẩn hóa + manifest
│   │   ├── gold/                # Dữ liệu sẵn dùng
│   │   ├── evaluation/          # Benchmark set
│   │   ├── dictionary/          # Từ điển y khoa (raw + processed)
│   │   └── audit/               # Log kiểm toán
│   ├── schemas/                 # JSON Schema (encounter, transcript, fact, metadata)
│   ├── synthetic_data/          # 6 ca khám giả lập (outpatient_v0_1)
│   ├── docs/                    # Tài liệu cho data layer
│   └── scripts/                 # ETL, validation scripts
│
├── docs/
│   ├── research/
│   │   ├── 01_governance/       # Quản trị dữ liệu y tế
│   │   ├── 02_ai_safety/        # An toàn AI
│   │   ├── 03_clinical_ASR_NLP_evaluation_metrics/
│   │   ├── 04_vietnamese_clinical_asr_benchmark/
│   │   ├── 05_future-proof_schema_design/
│   │   ├── architecture/        # Pipeline plan
│   │   ├── technical/           # Technical spec
│   │   └── whisper_phowhisper/  # Deep research Whisper/PhoWhisper
│   ├── reports/latex/           # Báo cáo LaTeX
│   └── research_data_source/    # Master research report gốc
│
├── scripts/
│   └── data_ingestion/          # Script nạp dữ liệu vào bronze
│
└── report/                      # Build output (git-ignored)
```

## Synthetic data (v0.1)

Mỗi case gồm: `script.md` → `transcript_segments_gold.json` → `clinical_facts_gold.json` → `soap_note_gold.md` + `annotation_notes.md` + `encounter_metadata.json`

| Case | Mô tả |
|---|---|
| SYN_OUT_001 | Ho 3 ngày, sốt nhẹ, phủ nhận đau ngực/khó thở |
| SYN_OUT_002 | Đau bụng + tiêu chảy 2 ngày, phủ nhận máu trong phân |
| SYN_OUT_003 | Đau đầu 1 tuần, ngủ kém, phủ nhận nôn/nhìn mờ |
| SYN_OUT_004 | Đau ngực — negation test tim mạch |
| SYN_OUT_005 | Đau thượng vị — negation test tiêu hóa |
| SYN_OUT_006 | Ho kéo dài — negation test hô hấp |
