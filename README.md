# Clinical Ambient Documentation Assistant

> **Local-first, Privacy-first** — Hệ thống hỗ trợ bác sĩ tự động ghi chép y bạ từ hội thoại lâm sàng tiếng Việt.

Dự án xây dựng pipeline hoàn chỉnh: Thu âm hội thoại khám bệnh → Nhận diện giọng nói (ASR) → Trích xuất thực thể y khoa (NLP) → Tạo bản tóm tắt SOAP Note — toàn bộ chạy on-premise, không gửi dữ liệu bệnh nhân ra bên ngoài.

---

## Project Skeleton

```text
Clinical Ambient Documentation Assistant/
│
├── .gitignore                                              # Cấu hình Git: loại trừ audio thô, report build, .agent
│
├── README.md                                               # Tài liệu tổng quan dự án & Skeleton hiện tại
│
├── Clinical ASR_NLP Evaluation Metrics and International   # Báo cáo nghiên cứu: Chỉ số đánh giá ASR/NLP quốc tế
│   Benchmarks for Ambient Clinical Documentation ...md     #   cho hệ thống ghi chép y bạ tự động
│
├── Future-Proof Canonical Clinical Schema Design.md        # Báo cáo nghiên cứu: Thiết kế lược đồ dữ liệu y khoa
│                                                           #   kinh điển, bền vững theo thời gian
│
├── Khung an toàn AI cho tài liệu Y tế.md                  # Báo cáo nghiên cứu: Khung an toàn AI (AI Safety Framework)
│                                                           #   áp dụng cho tài liệu y tế tại Việt Nam
│
├── Nghiên cứu pháp lý AI Y tế tại Việt Nam.md             # Báo cáo nghiên cứu: Phân tích khung pháp lý hiện hành
│                                                           #   liên quan đến AI trong y tế Việt Nam
│
├── Vietnamese ASR Clinical Documentation Research.md       # Báo cáo nghiên cứu: Tổng hợp nghiên cứu ASR tiếng Việt
│                                                           #   trong bối cảnh ghi chép lâm sàng
│
│
│   ══════════════════════════════════════════════════════
│   DATA LAYER — Dữ liệu, Lược đồ & Quản trị
│   ══════════════════════════════════════════════════════
│
├── data/                                                   # [DIR] Tầng dữ liệu cốt lõi của toàn bộ hệ thống
│   │
│   ├── data_governance/                                    # [DIR] Quản trị dữ liệu — Tuân thủ pháp lý & Bảo mật
│   │   ├── dataset_registry.csv                            # Sổ đăng ký tất cả dataset: nguồn, giấy phép, phiên bản
│   │   ├── dataset_registry_dictionary.md                  # Từ điển giải thích các trường trong dataset_registry.csv
│   │   ├── license_matrix.md                               # Ma trận giấy phép & bản quyền của từng nguồn dữ liệu
│   │   └── source_risk_register.md                         # Đánh giá rủi ro pháp lý/bảo mật cho từng nguồn dữ liệu
│   │
│   ├── data_lake/                                          # [DIR] Hồ dữ liệu — Kiến trúc Medallion (Bronze→Silver→Gold)
│   │   │
│   │   ├── audit/                                          # [DIR] Nhật ký kiểm toán xử lý dữ liệu (Data Audit Trail)
│   │   │
│   │   ├── bronze/                                         # [DIR] BRONZE LAYER — Dữ liệu thô chưa xử lý (Raw Ingestion)
│   │   │   └── public/                                     # [DIR] Các bộ dữ liệu công khai (Public Datasets)
│   │   │       ├── common_voice_vi/                        # [DIR] Mozilla Common Voice tiếng Việt
│   │   │       │   ├── checksums/                          #   Hash SHA256 đảm bảo toàn vẹn dữ liệu tải về
│   │   │       │   ├── license_snapshot/                   #   Bản sao giấy phép tại thời điểm tải
│   │   │       │   ├── metadata/                           #   Siêu dữ liệu gốc từ Mozilla (TSV, validated.tsv)
│   │   │       │   └── raw/                                #   File audio thô (.mp3) — Git-ignored
│   │   │       ├── fosd/                                   # [DIR] FOSD — Free Online Speech Dataset tiếng Việt
│   │   │       │   ├── checksums/                          #   Hash toàn vẹn dữ liệu FOSD
│   │   │       │   ├── license_snapshot/                   #   Bản sao giấy phép FOSD
│   │   │       │   ├── metadata/                           #   Siêu dữ liệu gốc
│   │   │       │   └── raw/                                #   File audio thô — Git-ignored
│   │   │       └── vietmed/                                # [DIR] VietMed — Bộ dữ liệu y khoa tiếng Việt
│   │   │           ├── checksums/                          #   Hash toàn vẹn dữ liệu VietMed
│   │   │           ├── license_snapshot/                   #   Bản sao giấy phép VietMed
│   │   │           ├── metadata/                           #   Siêu dữ liệu gốc
│   │   │           └── raw/                                #   File audio thô — Git-ignored
│   │   │
│   │   ├── silver/                                         # [DIR] SILVER LAYER — Dữ liệu đã làm sạch & chuẩn hóa
│   │   │   ├── audio_clean/                                #   Audio đã chuẩn hóa (16kHz, mono, noise-reduced)
│   │   │   └── public_manifest/                            #   Manifest liên kết audio ↔ transcript cho training
│   │   │
│   │   ├── gold/                                           # [DIR] GOLD LAYER — Dữ liệu sẵn sàng sử dụng (Production-ready)
│   │   │
│   │   ├── evaluation/                                     # [DIR] Tập dữ liệu benchmark đánh giá mô hình
│   │   │
│   │   └── dictionary/                                     # [DIR] Từ điển chuyên ngành y khoa
│   │       ├── raw_sources/                                #   Nguồn từ điển gốc (ICD-10, SNOMED-CT snapshot)
│   │       └── processed/                                  #   Từ điển đã xử lý, sẵn sàng cho NLP lookup
│   │
│   ├── schemas/                                            # [DIR] JSON Schema — Quy chuẩn cấu trúc dữ liệu nội bộ
│   │   ├── clinical_fact.schema.json                       # Schema: Sự kiện/Thực thể y khoa trích xuất từ hội thoại
│   │   ├── dataset_metadata.schema.json                    # Schema: Siêu dữ liệu mô tả các bộ dữ liệu
│   │   ├── encounter.schema.json                           # Schema: Thông tin một phiên khám bệnh (Encounter)
│   │   └── transcript_segment.schema.json                  # Schema: Phân đoạn bóc băng giọng nói (ASR Segment)
│   │
│   ├── synthetic_data/                                     # [DIR] Dữ liệu tổng hợp giả lập phục vụ phát triển & test
│   │   ├── synthetic_encounter_specs.md                    # Đặc tả kỹ thuật cho các ca khám giả lập
│   │   └── outpatient_v0_1/                                # [DIR] Batch v0.1 — 6 ca khám ngoại trú giả lập
│   │       ├── README.md                                   # Mô tả tổng quan batch dữ liệu v0.1
│   │       ├── SYN_OUT_001/                                # [DIR] Ca khám #001 — Tăng huyết áp (Hypertension)
│   │       │   ├── encounter_metadata.json                 #   Thông tin phiên khám (thời gian, chuyên khoa, bác sĩ)
│   │       │   ├── script.md                               #   Kịch bản hội thoại bác sĩ — bệnh nhân
│   │       │   ├── transcript_segments_gold.json           #   Gold-standard: Bóc băng chuẩn từng câu nói
│   │       │   ├── clinical_facts_gold.json                #   Gold-standard: Thực thể y khoa trích xuất
│   │       │   ├── soap_note_gold.md                       #   Gold-standard: Bản tóm tắt SOAP hoàn chỉnh
│   │       │   └── annotation_notes.md                     #   Ghi chú của người đánh giá (Annotator Notes)
│   │       ├── SYN_OUT_002/                                # [DIR] Ca khám #002
│   │       ├── SYN_OUT_003/                                # [DIR] Ca khám #003
│   │       ├── SYN_OUT_004/                                # [DIR] Ca khám #004
│   │       ├── SYN_OUT_005/                                # [DIR] Ca khám #005
│   │       └── SYN_OUT_006/                                # [DIR] Ca khám #006
│   │
│   ├── docs/                                               # [DIR] Tài liệu đặc thù cho tầng dữ liệu (Data Layer Docs)
│   │
│   └── scripts/                                            # [DIR] Script ETL, Validation, Data Processing
│
│
│   ══════════════════════════════════════════════════════
│   DOCS LAYER — Nghiên cứu, Báo cáo & Kiến trúc
│   ══════════════════════════════════════════════════════
│
├── docs/                                                   # [DIR] Trung tâm tài liệu: Nghiên cứu + Báo cáo + Kỹ thuật
│   │
│   ├── research/                                           # [DIR] Nghiên cứu chuyên sâu — 5 Module + Kiến trúc + Kỹ thuật
│   │   │
│   │   ├── 01_governance/                                  # [MODULE 1] Quản trị Dữ liệu Y tế & Tuân thủ Pháp lý
│   │   │   ├── 00_mvp_governance_reading_guide.md          #   Hướng dẫn đọc hiểu toàn bộ module Governance
│   │   │   ├── 01_mvp_data_governance_context_for_ai.md    #   Bối cảnh: Vì sao AI y tế cần quản trị dữ liệu đặc biệt
│   │   │   ├── 02_data_inventory_mvp.md                    #   Kiểm kê & Phân loại tài sản dữ liệu (Data Inventory)
│   │   │   ├── 03_dev_data_policy.md                       #   Chính sách sử dụng dữ liệu trên môi trường Dev
│   │   │   ├── 04_consent_and_session_policy_mvp.md        #   Chính sách đồng ý (Consent) & Quản lý phiên thu âm
│   │   │   ├── 05_retention_and_deletion_policy_mvp.md     #   Chính sách lưu giữ & Hủy dữ liệu (Retention/Deletion)
│   │   │   ├── 06_access_control_and_audit_log_mvp.md      #   Kiểm soát truy cập RBAC & Nhật ký kiểm toán
│   │   │   ├── 07_ai_safety_and_human_review_policy_mvp.md #   An toàn AI & Quy trình xét duyệt HITL
│   │   │   ├── 08_context_for_ai_build_project.md          #   Bối cảnh & Mục tiêu tổng thể dự án AI
│   │   │   └── 09_mvp_governance_checklist.md              #   Checklist nghiệm thu module Governance
│   │   │
│   │   ├── 02_ai_safety/                                   # [MODULE 2] An toàn Trí tuệ Nhân tạo (AI Safety & Risk)
│   │   │   ├── 00_ai_safety_reading_guide.md               #   Hướng dẫn tiếp cận framework An toàn AI
│   │   │   ├── 01_ai_safety_context_for_ai_build.md        #   Bối cảnh rủi ro an toàn AI trong y tế
│   │   │   ├── 02_mvp_ai_safety_requirements.md            #   Yêu cầu An toàn AI cho phiên bản MVP
│   │   │   ├── 03_hazard_log_mvp.md                        #   Sổ ghi chép mối nguy hiểm tiềm tàng (Hazard Log)
│   │   │   ├── 04_human_in_the_loop_doctor_review.md       #   Giao thức xác nhận bác sĩ (Human-in-the-Loop)
│   │   │   ├── 05_clinical_error_taxonomy_creola_lite.md   #   Phân loại lỗi y khoa (CREOLA-Lite Taxonomy)
│   │   │   ├── 06_evaluation_protocol_mvp_safety.md        #   Giao thức đánh giá rủi ro an toàn cho MVP
│   │   │   ├── 07_prompt_grounding_and_generation_guardrails.md # Guardrails cho Prompt: Grounding & Generation
│   │   │   ├── 08_safety_flags_schema.md                   #   Schema cắm cờ cảnh báo an toàn (Safety Flags)
│   │   │   ├── 09_audit_and_version_log_safety.md          #   Kiểm toán & Quản lý phiên bản hệ thống an toàn
│   │   │   ├── 10_safety_acceptance_checklist.md           #   Checklist kiểm định an toàn trước release
│   │   │   └── 11_safety_case_lite_for_intern_mvp.md       #   Hồ sơ an toàn thu gọn (Safety Case Lite)
│   │   │
│   │   ├── 03_clinical_ASR_NLP_evaluation_metrics/         # [MODULE 3] Chỉ số Đo lường Hiệu suất ASR & NLP
│   │   │   ├── 00_clinical_evaluation_reading_guide.md     #   Hướng dẫn sử dụng hệ thống Evaluation Metrics
│   │   │   ├── 01_evaluation_context_for_ai_build.md       #   Bối cảnh: Vì sao cần hệ thống đo lường riêng
│   │   │   ├── 02_mvp_metric_catalog.md                    #   Danh mục chỉ số đánh giá cốt lõi (WER, CER, F1...)
│   │   │   ├── 03_asr_evaluation_protocol_mvp.md           #   Giao thức đo lường ASR (Word/Character Error Rate)
│   │   │   ├── 04_clinical_fact_extraction_metrics.md      #   Chỉ số trích xuất thực thể y khoa (Precision/Recall)
│   │   │   ├── 05_soap_note_quality_rubric_mvp.md          #   Tiêu chí chất lượng SOAP Note (Rubric)
│   │   │   ├── 06_doctor_review_and_edit_metrics.md        #   Đo nỗ lực chỉnh sửa của bác sĩ (Edit Distance)
│   │   │   ├── 07_failure_modes_and_error_taxonomy_mvp.md  #   Phân loại Failure Modes của pipeline
│   │   │   ├── 08_demo_case_evaluation_template.md         #   Biểu mẫu đánh giá các Demo Cases
│   │   │   ├── 09_benchmark_and_maturity_positioning.md    #   Định vị trưởng thành & So sánh Benchmark
│   │   │   ├── 10_evaluation_acceptance_checklist.md       #   Checklist nghiệm thu module Evaluation
│   │   │   └── 11_context_for_ai_build_evaluation_module.md#   Ngữ cảnh xây dựng module Evaluation cho AI
│   │   │
│   │   ├── 04_vietnamese_clinical_asr_benchmark/           # [MODULE 4] Benchmark ASR tiếng Việt trong Y khoa
│   │   │   ├── 00_asr_research_reading_guide.md            #   Hướng dẫn tiếp cận nghiên cứu Benchmark ASR
│   │   │   ├── 01_asr_context_for_ai_build.md              #   Tổng quan ASR trong bối cảnh lâm sàng Việt Nam
│   │   │   ├── 02_candidate_asr_model_matrix.md            #   Ma trận chấm điểm các mô hình ASR ứng viên
│   │   │   ├── 03_vietnamese_asr_benchmark_summary.md      #   Kết quả Benchmark ASR tiếng Việt (WER, latency)
│   │   │   ├── 04_clinical_asr_error_taxonomy.md           #   Phân loại lỗi đặc thù khi bóc băng y khoa
│   │   │   ├── 05_asr_metric_framework_mvp.md              #   Framework đo lường chất lượng ASR
│   │   │   ├── 06_local_asr_benchmark_protocol.md          #   Giao thức Benchmark chạy Local (On-premise)
│   │   │   ├── 07_model_decision_matrix.md                 #   Ma trận quyết định lựa chọn mô hình cuối cùng
│   │   │   ├── 08_asr_pipeline_recommendation_mvp.md       #   Khuyến nghị thiết kế ASR Pipeline cho MVP
│   │   │   ├── 09_asr_safety_acceptance_checklist.md       #   Checklist an toàn đặc thù cho ASR
│   │   │   └── 10_context_for_ai_build_asr_module.md       #   Ngữ cảnh xây dựng module ASR
│   │   │
│   │   ├── 05_future-proof_schema_design/                  # [MODULE 5] Thiết kế Lược đồ Dữ liệu Bền vững
│   │   │   ├── 00_schema_reading_guide_for_intern_mvp.md   #   Hướng dẫn thiết kế Schema cho intern/MVP
│   │   │   ├── 01_mvp_schema_scope.md                      #   Phạm vi & Giới hạn Schema cho MVP
│   │   │   ├── 02_foundation_types_for_ai.md               #   Kiểu dữ liệu nền tảng (Foundation Types)
│   │   │   ├── 03_canonical_entities_mvp.md                 #   Thực thể dữ liệu kinh điển (Canonical Entities)
│   │   │   ├── 04_schema_mapping_rules_for_ai.md           #   Quy tắc ánh xạ giữa các Schema (Mapping Rules)
│   │   │   ├── 05_context_for_ai_build_schema.md           #   Bối cảnh: Vì sao AI cần Schema khắt khe
│   │   │   ├── 06_minimal_json_schema_for_mvp.md           #   Thiết kế JSON Schema tinh gọn cho MVP
│   │   │   ├── 07_schema_acceptance_checklist.md           #   Checklist rà soát chất lượng Schema
│   │   │   ├── 08_schema_anti_patterns_to_avoid.md         #   Anti-patterns cần tránh khi thiết kế Schema
│   │   │   └── 09_future_phase_mapping_notes.md            #   Ghi chú mở rộng Schema cho các phase tương lai
│   │   │
│   │   ├── architecture/                                   # [DIR] Kiến trúc Hệ thống Tổng thể
│   │   │   └── PROJECT_PIPELINE_PLAN.md                    #   Kế hoạch Pipeline E2E (Ingestion → ASR → NLP → SOAP)
│   │   │
│   │   ├── technical/                                      # [DIR] Tài liệu Kỹ thuật Cốt lõi
│   │   │   └── Local-first Clinical Ambient Documentation  #   Báo cáo kỹ thuật: Kiến trúc Local-first cho
│   │   │       Assistant for Vietnamese Outpatient Care.md #     Hệ thống Hỗ trợ Khám Ngoại trú tại Việt Nam
│   │   │
│   │   └── whisper_phowhisper/                             # [DIR] Nghiên cứu chuyên sâu mô hình Whisper & PhoWhisper
│   │       └── ASR_Whisper_PhoWhisper_Clinical_Ambient_    #   Deep Research: So sánh Whisper vs PhoWhisper
│   │           VI_Deep_Research.pdf.md                     #     trong ứng dụng bóc băng lâm sàng tiếng Việt
│   │
│   ├── reports/                                            # [DIR] Báo cáo chính thức (Formal Reports)
│   │   └── latex/                                          # [DIR] Bản LaTeX cho báo cáo in ấn/xuất bản
│   │
│   └── research_data_source/                               # [DIR] Nguồn dữ liệu tham khảo cho nghiên cứu
│       └── master_research_report_clinical_ambient_        #   Báo cáo nghiên cứu tổng hợp gốc (Master Report)
│           documentation_vi.md                             #     làm nền tảng cho toàn bộ các module nghiên cứu
│
│
│   ══════════════════════════════════════════════════════
│   SCRIPTS LAYER — Tập lệnh Tự động hóa
│   ══════════════════════════════════════════════════════
│
├── scripts/                                                # [DIR] Tập lệnh pipeline & Tự động hóa hệ thống
│   └── data_ingestion/                                     # [DIR] Script nạp dữ liệu vào Data Lake (Bronze Layer)
│
│
│   ══════════════════════════════════════════════════════
│   BUILD & OUTPUT (Git-ignored)
│   ══════════════════════════════════════════════════════
│
└── report/                                                 # [DIR] Output biên dịch (LaTeX PDF) — Git-ignored
```

---

## Kiến trúc Pipeline

```text
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│  Thu âm      │───→│  ASR Engine  │───→│  NLP / Fact   │───→│  SOAP Note   │
│  Hội thoại   │    │  (Whisper/   │    │  Extraction   │    │  Generator   │
│  Lâm sàng    │    │  PhoWhisper) │    │  (Clinical)   │    │  (Auto-draft)│
└─────────────┘    └──────────────┘    └───────────────┘    └──────────────┘
       │                  │                    │                     │
       ▼                  ▼                    ▼                    ▼
   Bronze Layer      Silver Layer         Gold Layer          Bác sĩ Review
   (Raw Audio)       (Clean Audio +       (Structured         (Human-in-the-
                      Transcript)          Clinical Facts)     Loop / HITL)
```

## Nguyên tắc Thiết kế

| Nguyên tắc | Mô tả |
|---|---|
| **Local-first** | Toàn bộ pipeline chạy on-premise, không gửi PHI ra cloud |
| **Privacy-first** | Tuân thủ quy định bảo mật dữ liệu y tế Việt Nam |
| **Medallion Architecture** | Data Lake 3 tầng: Bronze → Silver → Gold |
| **Schema-driven** | Mọi dữ liệu tuân theo JSON Schema nghiêm ngặt |
| **Human-in-the-Loop** | Bác sĩ luôn là người xác nhận cuối cùng |
| **Synthetic-first Dev** | Phát triển & test trên dữ liệu giả lập, không dùng dữ liệu thật |
