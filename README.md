. (Clinical Ambient Documentation Assistant)
├── data/                                               # [DIR] Dữ liệu cốt lõi, Lược đồ (Schemas) và Script hệ thống
│   ├── data_governance/                                # [DIR] Quản trị dữ liệu (Data Governance / Compliance)
│   │   ├── dataset_registry.csv                        # Danh sách đăng ký & quản lý các tập dữ liệu
│   │   ├── dataset_registry_dictionary.md              # Từ điển siêu dữ liệu (Data Dictionary) cho registry
│   │   ├── license_matrix.md                           # Ma trận giấy phép & bản quyền của các nguồn dữ liệu
│   │   └── source_risk_register.md                     # Sổ đăng ký rủi ro pháp lý/bảo mật từ nguồn dữ liệu
│   ├── data_lake/                                      # [DIR] Hồ dữ liệu xây dựng theo kiến trúc Medallion
│   │   ├── audit/                                      # Nhật ký kiểm toán dữ liệu (Data Audit Logs)
│   │   ├── bronze/                                     # Bronze Layer: Dữ liệu thô (Raw Data) chưa qua xử lý
│   │   ├── dictionary/                                 # Từ điển dữ liệu nội bộ trong hệ thống Data Lake
│   │   ├── evaluation/                                 # Dữ liệu phục vụ đánh giá mô hình (Benchmark/Testing)
│   │   ├── gold/                                       # Gold Layer: Dữ liệu sạch chuẩn hóa cao (Ready-to-use)
│   │   └── silver/                                     # Silver Layer: Dữ liệu đã làm sạch cơ bản & loại bỏ trùng lặp
│   ├── docs/                                           # [DIR] Tài liệu hướng dẫn đặc thù cho kiến trúc dữ liệu
│   ├── schemas/                                        # [DIR] Lược đồ dữ liệu chuẩn hóa nội bộ (JSON Schemas)
│   │   ├── clinical_fact.schema.json                   # Cấu trúc lưu trữ các sự kiện/thực thể y khoa (Clinical Facts)
│   │   ├── dataset_metadata.schema.json                # Cấu trúc siêu dữ liệu (Metadata) cho các Dataset
│   │   ├── encounter.schema.json                       # Cấu trúc thông tin một phiên khám bệnh (Medical Encounter)
│   │   └── transcript_segment.schema.json              # Cấu trúc từng phân đoạn bóc băng giọng nói (ASR Transcript)
│   ├── scripts/                                        # [DIR] Tập lệnh xử lý dữ liệu (ETL, Data Validation, Cron)
│   └── synthetic_data/                                 # [DIR] Dữ liệu tổng hợp giả lập (Synthetic Data) để huấn luyện/Test
├── docs/                                               # [DIR] Hệ thống tài liệu dự án, nghiên cứu và kỹ thuật
│   ├── research/                                       # [DIR] Thư mục chứa các nghiên cứu chuyên sâu (Research)
│   │   ├── 01_governance/                              # Module 1: Pháp lý & Quản trị dữ liệu y tế (Governance Policy)
│   │   │   ├── 00_mvp_governance_reading_guide.md      # Hướng dẫn đọc tài liệu quản trị
│   │   │   ├── 01_mvp_data_governance_context_for_ai.md# Ngữ cảnh xây dựng hệ thống quản trị dữ liệu cho AI
│   │   │   ├── 02_data_inventory_mvp.md                # Kiểm kê và phân loại dữ liệu (Data Inventory)
│   │   │   ├── 03_dev_data_policy.md                   # Chính sách bảo mật dữ liệu trên môi trường Dev
│   │   │   ├── 04_consent_and_session_policy_mvp.md    # Chính sách xin phép (Consent) và quản lý phiên (Session)
│   │   │   ├── 05_retention_and_deletion_policy_mvp.md # Chính sách lưu giữ và hủy bỏ dữ liệu (Retention Policy)
│   │   │   ├── 06_access_control_and_audit_log_mvp.md  # Kiểm soát truy cập (RBAC) & Nhật ký kiểm toán (Audit Logs)
│   │   │   ├── 07_ai_safety_and_human_review_policy_mvp.md # Chính sách An toàn AI & Xét duyệt bởi con người (HITL)
│   │   │   ├── 08_context_for_ai_build_project.md      # Bối cảnh & Mục tiêu xây dựng dự án AI
│   │   │   └── 09_mvp_governance_checklist.md          # Danh sách kiểm tra nghiệm thu (Checklist) module Governance
│   │   ├── 02_ai_safety/                               # Module 2: An toàn Trí tuệ Nhân tạo (AI Safety & Risk)
│   │   │   ├── 00_ai_safety_reading_guide.md           # Hướng dẫn tìm hiểu và triển khai An toàn AI
│   │   │   ├── 01_ai_safety_context_for_ai_build.md    # Ngữ cảnh về các rủi ro an toàn AI trong y tế
│   │   │   ├── 02_mvp_ai_safety_requirements.md        # Tập hợp yêu cầu An toàn AI cho phiên bản MVP
│   │   │   ├── 03_hazard_log_mvp.md                    # Sổ ghi chép các mối nguy hiểm tiềm tàng (Hazard Log)
│   │   │   ├── 04_human_in_the_loop_doctor_review.md   # Giao thức xác nhận thông tin từ Bác sĩ (Human-in-the-loop)
│   │   │   ├── 05_clinical_error_taxonomy_creola_lite.md # Phân loại các lỗi y khoa (Clinical Error Taxonomy)
│   │   │   ├── 06_evaluation_protocol_mvp_safety.md    # Giao thức đánh giá rủi ro an toàn
│   │   │   ├── 07_prompt_grounding_and_generation_guardrails.md # Tiêu chuẩn Grounding và Guardrails cho Prompt
│   │   │   ├── 08_safety_flags_schema.md               # Lược đồ cắm cờ cảnh báo an toàn (Safety Flags Schema)
│   │   │   ├── 09_audit_and_version_log_safety.md      # Kiểm toán hệ thống & Quản lý lịch sử phiên bản
│   │   │   ├── 10_safety_acceptance_checklist.md       # Checklist kiểm định an toàn AI trước khi release
│   │   │   └── 11_safety_case_lite_for_intern_mvp.md   # Hồ sơ an toàn thu gọn chứng minh tính khả thi của MVP
│   │   ├── 03_clinical_ASR_NLP_evaluation_metrics/     # Module 3: Chỉ số Đo lường Hiệu suất (Evaluation Metrics)
│   │   │   ├── 00_clinical_evaluation_reading_guide.md # Hướng dẫn sử dụng các chỉ số Evaluation
│   │   │   ├── 01_evaluation_context_for_ai_build.md   # Lý do và bối cảnh cần hệ thống đo lường riêng biệt
│   │   │   ├── 02_mvp_metric_catalog.md                # Danh mục các chỉ số đánh giá cốt lõi (Metric Catalog)
│   │   │   ├── 03_asr_evaluation_protocol_mvp.md       # Giao thức đo lường độ chính xác ASR (WER, CER)
│   │   │   ├── 04_clinical_fact_extraction_metrics.md  # Chỉ số đánh giá trích xuất thực thể y khoa (NLP Extraction Metrics)
│   │   │   ├── 05_soap_note_quality_rubric_mvp.md      # Tiêu chí chất lượng viết tóm tắt y bạ chuẩn SOAP
│   │   │   ├── 06_doctor_review_and_edit_metrics.md    # Đo lường nỗ lực chỉnh sửa văn bản của bác sĩ
│   │   │   ├── 07_failure_modes_and_error_taxonomy_mvp.md # Các chế độ lỗi (Failure Modes) của hệ thống
│   │   │   ├── 08_demo_case_evaluation_template.md     # Biểu mẫu đánh giá các ca sử dụng mẫu (Demo Cases)
│   │   │   ├── 09_benchmark_and_maturity_positioning.md# Định vị mức độ trưởng thành & Benchmark so với đối thủ
│   │   │   ├── 10_evaluation_acceptance_checklist.md   # Checklist nghiệm thu module Đánh giá
│   │   │   └── 11_context_for_ai_build_evaluation_module.md # Ngữ cảnh xây dựng module Đánh giá
│   │   ├── 04_vietnamese_clinical_asr_benchmark/       # Module 4: Benchmark Mô hình ASR (Nhận diện giọng nói tiếng Việt)
│   │   │   ├── 00_asr_research_reading_guide.md        # Hướng dẫn tiếp cận nghiên cứu Benchmark ASR
│   │   │   ├── 01_asr_context_for_ai_build.md          # Tổng quan về nhận diện giọng nói trong lâm sàng
│   │   │   ├── 02_candidate_asr_model_matrix.md        # Ma trận chấm điểm các mô hình ASR tiềm năng
│   │   │   ├── 03_vietnamese_asr_benchmark_summary.md  # Tóm tắt kết quả Benchmark các mô hình tiếng Việt
│   │   │   ├── 04_clinical_asr_error_taxonomy.md       # Phân loại lỗi sai đặc thù khi bóc băng y khoa
│   │   │   ├── 05_asr_metric_framework_mvp.md          # Khung Framework đo lường chất lượng ASR
│   │   │   ├── 06_local_asr_benchmark_protocol.md      # Giao thức Benchmark mô hình chạy Local (On-premise)
│   │   │   ├── 07_model_decision_matrix.md             # Ma trận quyết định lựa chọn mô hình cuối cùng
│   │   │   ├── 08_asr_pipeline_recommendation_mvp.md   # Khuyến nghị thiết kế Pipeline ASR cho MVP
│   │   │   ├── 09_asr_safety_acceptance_checklist.md   # Checklist an toàn đặc thù cho phân hệ ASR
│   │   │   └── 10_context_for_ai_build_asr_module.md   # Ngữ cảnh định hướng xây dựng tính năng ASR
│   │   ├── 05_future-proof_schema_design/              # Module 5: Thiết kế Kiến trúc Lược đồ (Schema Design)
│   │   │   ├── 00_schema_reading_guide_for_intern_mvp.md # Hướng dẫn thiết kế cấu trúc dữ liệu chuẩn y tế
│   │   │   ├── 01_mvp_schema_scope.md                  # Xác định phạm vi và giới hạn của Schema MVP
│   │   │   ├── 02_foundation_types_for_ai.md           # Định nghĩa các kiểu dữ liệu nền tảng (Foundation Types)
│   │   │   ├── 03_canonical_entities_mvp.md            # Các thực thể dữ liệu kinh điển (Canonical Entities)
│   │   │   ├── 04_schema_mapping_rules_for_ai.md       # Quy tắc ánh xạ (Mapping Rules) giữa các Schema
│   │   │   ├── 05_context_for_ai_build_schema.md       # Bối cảnh vì sao hệ thống AI cần Schema khắt khe
│   │   │   ├── 06_minimal_json_schema_for_mvp.md       # Thiết kế khung JSON Schema tinh gọn
│   │   │   ├── 07_schema_acceptance_checklist.md       # Checklist rà soát chất lượng Lược đồ
│   │   │   ├── 08_schema_anti_patterns_to_avoid.md     # Những lỗi Anti-patterns thường gặp cần tránh
│   │   │   └── 09_future_phase_mapping_notes.md        # Ghi chú định hướng mở rộng (Scale-up) Schema
│   │   ├── architecture/                               # [DIR] Bản vẽ kiến trúc hệ thống tổng thể (System Architecture)
│   │   │   └── PROJECT_PIPELINE_PLAN.md                # Kế hoạch quy trình luồng dữ liệu E2E (Data Pipeline)
│   │   └── technical/                                  # [DIR] Tài liệu kỹ thuật cốt lõi (Technical Concepts)
