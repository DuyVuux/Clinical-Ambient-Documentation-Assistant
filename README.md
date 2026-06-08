# Clinical Ambient Documentation Assistant

Hệ thống hỗ trợ bác sĩ ghi chép y bạ tự động từ hội thoại khám bệnh tiếng Việt.

Pipeline: Thu âm → ASR (Whisper/PhoWhisper) → Trích xuất clinical facts → SOAP note draft → Bác sĩ review & ký.

Chạy local, không gửi dữ liệu bệnh nhân ra ngoài.

## Cấu trúc thư mục (Project Skeleton)

Dưới đây là cấu trúc hiện tại của dự án cùng giải thích ngắn gọn về chức năng của từng thư mục và tệp tin quan trọng:

```text
Clinical Ambient Documentation Assistant/
├── .gitignore                          # Cấu hình bỏ qua các file không cần thiết cho git
├── Clinical ASR_NLP Evaluation...md    # Tiêu chuẩn đánh giá và benchmark quốc tế cho ASR lâm sàng
├── Future-Proof Canonical Clinical Schema Design.md # Thiết kế schema dữ liệu JSON chuẩn cho dự án
├── Khung an toàn AI cho tài liệu Y tế.md # Quy định và khung an toàn AI áp dụng trong y tế
├── Nghiên cứu pháp lý AI Y tế tại Việt Nam.md # Báo cáo nghiên cứu tính pháp lý tại Việt Nam
├── README.md                           # Tài liệu giới thiệu và hướng dẫn chính của dự án
├── README_vi.md                        # Phiên bản tiếng Việt của README
├── assume.md                           # Giả định và ràng buộc kỹ thuật của hệ thống
├── Vietnamese ASR Clinical...md        # Báo cáo nghiên cứu tổng quan về ASR y tế tiếng Việt
├── audio_clean_dev.tar.gz              # Dữ liệu âm thanh phát triển (archive)
├── data_lake.zip                       # Bản nén của data_lake ban đầu (nếu có)
├── requirements.txt                    # Danh sách thư viện Python cần thiết (chính)
├── requirements-dev.txt                # Danh sách thư viện Python cho môi trường phát triển (test, lint)
├── data/                               # Chứa toàn bộ dữ liệu dự án
│   ├── data_governance/                # Tài liệu về quản trị dữ liệu, quy định cấp phép
│   │   ├── dataset_registry.csv        # Sổ đăng ký các tập dữ liệu
│   │   ├── dataset_registry_dictionary.md # Từ điển giải thích các cột trong registry
│   │   ├── internal_approval_notes.md  # Ghi chú phê duyệt nội bộ
│   │   ├── license_matrix.md           # Ma trận giấy phép các tập dữ liệu
│   │   └── source_risk_register.md     # Đánh giá rủi ro nguồn dữ liệu
│   ├── data_lake/                      # Cấu trúc medallion data lake (Bronze, Silver, Gold)
│   │   ├── audit/                      # Dữ liệu kiểm toán và log
│   │   ├── bronze/                     # Dữ liệu thô ban đầu (Audio & Manifest)
│   │   ├── silver/                     # Dữ liệu đã làm sạch và chuẩn hóa
│   │   ├── gold/                       # Dữ liệu chất lượng cao nhất dùng để đánh giá/huấn luyện
│   │   ├── dictionary/                 # Từ điển lâm sàng (nguồn thô và đã xử lý)
│   │   └── evaluation/                 # Dữ liệu dành riêng cho đánh giá (VD: test holdout)
│   ├── docs/                           # (Thư mục docs rỗng/đang chờ)
│   ├── schemas/                        # Các file JSON schema định nghĩa cấu trúc dữ liệu
│   │   ├── clinical_fact.schema.json   # Schema cho các fact y tế
│   │   ├── dataset_metadata.schema.json# Schema cho siêu dữ liệu dataset
│   │   ├── encounter.schema.json       # Schema lưu thông tin phiên khám
│   │   ├── encounter_outcome.json      # Schema cho kết quả sau khám
│   │   ├── soap_source_evidence.json   # Schema lưu bằng chứng SOAP
│   │   └── transcript_segment.schema.json # Schema cho từng đoạn phiên âm
│   ├── scripts/                        # (Chứa scripts liên quan đến data)
│   └── synthetic_data/                 # Dữ liệu tổng hợp (mock) để kiểm thử hệ thống
│       ├── evaluation_seed_coverage_matrix.md # Ma trận độ phủ của dữ liệu sinh tự động
│       ├── safety_error_taxonomy.md    # Phân loại lỗi an toàn
│       ├── synthetic_encounter_specs.md# Đặc tả kịch bản khám bệnh sinh tự động
│       └── outpatient_v0_1/            # Các hồ sơ bệnh án sinh tự động (SYN_OUT_001 -> 010)
│           ├── README.md               # Mô tả tập outpatient
│           ├── audit_synthetic_data.py # Script kiểm tra độ hợp lệ của dữ liệu mock
│           ├── fix_segment_ids.py      # Script sửa lỗi ID trong segments
│           ├── standardize_folders.py  # Chuẩn hóa tên thư mục SYN_OUT_*
│           └── SYN_OUT_001...010/      # (Mỗi folder chứa: audio script, clinical facts, metadata, SOAP note...)
├── docs/                               # Tài liệu nghiên cứu chuyên sâu, kiến trúc và quy trình
│   ├── assets/                         # Ảnh và tài nguyên cho báo cáo (Layer1_IDAE_System.drawio.png)
│   ├── research/                       # Các nghiên cứu cốt lõi của dự án
│   │   ├── 01_governance/              # Bộ tài liệu MVP về quy định, bảo mật và lưu trữ
│   │   ├── 02_ai_safety/               # Đánh giá rủi ro, HITL và báo cáo an toàn AI
│   │   ├── 03_clinical_ASR_NLP_evaluation_metrics/ # Các metric đánh giá ASR/NLP trong y tế
│   │   ├── 04_vietnamese_clinical_asr_benchmark/   # Benchmark cho các model ASR tiếng Việt
│   │   ├── 05_future-proof_schema_design/          # Thiết kế schema hệ thống dài hạn
│   │   ├── architecture/               # Kế hoạch kiến trúc dự án (PROJECT_PIPELINE_PLAN.md)
│   │   ├── technical/                  # Báo cáo kỹ thuật chi tiết
│   │   └── whisper_phowhisper/         # Nghiên cứu chuyên sâu về Whisper & PhoWhisper
│   └── research_data_source/           # Nguồn tài liệu tổng hợp (master_research_report...)
├── experiments/                        # Nơi lưu trữ mã nguồn và kết quả thử nghiệm
│   └── asr/                            # Thử nghiệm các mô hình ASR
│       ├── ASR_SPLIT_STRATEGY.md       # Chiến lược chia tập train/dev/test
│       ├── WER_PROTOCOL.md             # Giao thức đo lường Word Error Rate (WER)
│       ├── asr_target.md               # Mục tiêu và chỉ số kỳ vọng của hệ thống ASR
│       ├── baseline/                   # Kết quả chạy Baseline (logs, metrics, predictions)
│       ├── error_analysis/             # Phân tích lỗi (Medical taxonomy, terms check)
│       ├── finetune/                   # Thư mục cho Phase Fine-tuning (Tuần 4)
│       ├── model_expansion_v2/         # Mở rộng thử nghiệm mô hình ASR mới (ViStreamASR, Zipformer...)
│       │   ├── ADAPTER_INTERFACE.md
│       │   ├── MODEL_REGISTRY_EXPANSION_V2.md
│       │   ├── configs/
│       │   │   ├── vietmed_dev_mini_30.jsonl
│       │   │   └── vietmed_dev_smoke_10.jsonl
│       │   ├── error_analysis/
│       │   │   └── dev/
│       │   │       ├── vistream_dev_medical_errors.json
│       │   │       ├── vistream_dev_medical_errors.md
│       │   │       ├── zipformer30m_dev_medical_errors.json
│       │   │       └── zipformer30m_dev_medical_errors.md
│       │   ├── logs/
│       │   ├── metrics/
│       │   │   └── dev/
│       │   │       ├── vistream_dev_full_metrics.json
│       │   │       ├── vistream_dev_smoke_10_metrics.json
│       │   │       ├── zipformer30m_dev_full_metrics.json
│       │   │       └── zipformer30m_dev_smoke_10_metrics.json
│       │   ├── predictions/
│       │   │   └── dev/
│       │   │       ├── vistream_dev_full_predictions.jsonl
│       │   │       ├── vistream_dev_smoke_10_predictions.jsonl
│       │   │       ├── zipformer30m_dev_full_predictions.jsonl
│       │   │       └── zipformer30m_dev_smoke_10_predictions.jsonl
│       │   └── runtime/
│       │       └── dev/
│       ├── preprocessing/              # Thử nghiệm tiền xử lý âm thanh (A/B test, kiểm toán, ablation)
│       │   ├── DAY1_AUDIO_QA_REPORT.md
│       │   ├── DAY3_VARIANT_AUDIO_QA_FINDING.md
│       │   ├── ablation/
│       │   │   ├── DAY4_ASR_PREPROCESSING_ABLATION.md
│       │   │   ├── PREPROCESSING_ABLATION_LEADERBOARD_DEV.md
│       │   │   ├── logs/
│       │   │   ├── metrics/
│       │   │   └── predictions/
│       │   ├── audio_quality_audit/
│       │   │   ├── VARIANT_AUDIO_QA_SUMMARY.md
│       │   │   ├── dev/
│       │   │   ├── padding_aware/
│       │   │   ├── train/
│       │   │   ├── variant_audio_qa_summary.json
│       │   │   └── variants/
│       │   └── day2_build_variants/
│       │       ├── DAY2_BUILD_PREPROCESSING_VARIANTS_REPORT.md
│       │       ├── p00_format_only_failures.jsonl
│       │       ├── p00_format_only_summary.json
│       │       ├── p03_vad_pad_200ms_failures.jsonl
│       │       ├── p03_vad_pad_200ms_summary.json
│       │       ├── p04_vad_pad_300ms_failures.jsonl
│       │       ├── p04_vad_pad_300ms_summary.json
│       │       ├── p05_vad_pad_500ms_failures.jsonl
│       │       ├── p05_vad_pad_500ms_summary.json
│       │       ├── p10_edge_pad_200ms_failures.jsonl
│       │       ├── p10_edge_pad_200ms_summary.json
│       │       ├── p11_edge_pad_300ms_failures.jsonl
│       │       ├── p11_edge_pad_300ms_summary.json
│       │       ├── p12_edge_pad_500ms_failures.jsonl
│       │       └── p12_edge_pad_500ms_summary.json
│       └── validation/                 # Kiểm chứng mô hình (Leakage check, audit thủ công, day6 summary)
├── external_models/                    # Lưu trữ các mô hình ASR mở rộng bên ngoài (VD: ChunkFormer)
│   └── (Thư mục trống/chờ tải model)
├── report/                             # Báo cáo tiến độ hàng tuần
│   ├── Tuần_1/                         # Các báo cáo LaTeX và file PDF tuần 1
│   ├── Tuần_2/                         # Các báo cáo LaTeX và file PDF tuần 2
│   └── Tuần_3/                         # Báo cáo Markdown tuần 3 (Day6_Week3_Report.md)
├── scripts/                            # Chứa toàn bộ scripts thực thi của hệ thống
│   ├── asr_eval/                       # Scripts cho pipeline đánh giá ASR (WER, leak, normalize...)
│   │   ├── asr_medical_error_analysis.py # Phân tích lỗi thuật ngữ y khoa ASR
│   │   ├── check_asr_manifest.py       # Kiểm tra file jsonl manifest
│   │   ├── check_split_leakage.py      # Kiểm tra rò rỉ dữ liệu giữa tập train/test
│   │   ├── clinical_error_analysis.py  # Đánh giá lỗi y tế tổng quan
│   │   ├── compute_wer.py              # Script tính WER/CER
│   │   ├── create_asr_splits.py        # Chia tập dataset
│   │   ├── run_chunkformer_ctc.py      # Script chạy mô hình Chunkformer CTC
│   │   ├── run_hf_ctc_asr.py           # Script chạy mô hình CTC của HuggingFace
│   │   ├── run_whisper_transformers.py # Script chạy mô hình họ Whisper
│   │   └── text_normalization_vi.py    # Chuẩn hóa văn bản tiếng Việt
│   ├── asr_preprocess/                 # Scripts tiền xử lý và kiểm toán chất lượng âm thanh
│   │   ├── audit_audio_quality.py      # Kiểm toán chất lượng âm thanh ban đầu
│   │   ├── audit_audio_quality_padding_aware.py # Kiểm toán tách biệt padding và vùng có tiếng (speech)
│   │   ├── build_preprocess_variants.py # Xây dựng các biến thể dữ liệu âm thanh để A/B testing
│   │   └── summarize_variant_audio_qa.py # Tổng hợp báo cáo kiểm toán cho từng biến thể
│   ├── data_ingestion/                 # Scripts tải và import dữ liệu (Common Voice, public data)
│   │   ├── ingest_asr_public_day1.py   # Ingest script dữ liệu public day1
│   │   ├── ingest_common_voice_vi_official.py # Ingest script dữ liệu Common Voice VN
│   │   └── normalize_public_audio.py   # Chuẩn hóa file audio public
│   ├── data_utils/                     # Các công cụ tiện ích dữ liệu (validate json, fix dữ liệu gold)
│   │   ├── check_json.py               # Kiểm tra format JSON
│   │   ├── fix_candidate.py            # Sửa cấu trúc file candidate
│   │   ├── fix_gold.py                 # Chuẩn hóa dữ liệu gold
│   │   └── validate.py                 # Xác thực cấu trúc chung
│   ├── generate_candidates.py          # Script sinh kết quả từ mô hình ASR
│   └── validate_array.py               # Xác thực array
└── tests/                              # Thư mục chứa Unit Test
    └── scripts/                        # Test cho các scripts hệ thống
        └── data_ingestion/             # Test cho quy trình data ingestion
            └── test_normalize_public_audio.py # Test script chuẩn hóa âm thanh
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
