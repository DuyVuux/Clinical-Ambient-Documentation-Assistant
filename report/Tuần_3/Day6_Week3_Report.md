# Báo Cáo Tổng Hợp Đánh Giá ASR Lâm Sàng – Ngày 6 (Tuần 3)

**Dự án:** Clinical Ambient Documentation Assistant (Tiếng Việt)
**Người lập báo cáo:** Senior AI Research Engineer / Clinical NLP Safety Specialist
**Mục tiêu Tuần 3:** Đạt Word Error Rate (WER) < 20% và tối thiểu hóa rủi ro lỗi lâm sàng.

---

## 1. Tóm tắt Thực thi Ngày 6 (Executive Summary)

Ngày 6 tập trung vào việc **thẩm định tính hợp lệ của mô hình (Validation)**, chạy lại các kết quả trên tập Dev để đảm bảo tính tái lập, kiểm tra các tiêu chuẩn Hygiene của Benchmark, và đặc biệt là thực hiện **Phân tích Lỗi Y khoa (Medical Error Analysis)**. 

Tất cả các khâu kiểm tra đều đạt (**PASS**), cung cấp cơ sở dữ liệu vững chắc để chốt phương án chạy thử nghiệm trên tập `test_holdout` ở Ngày 7 và lập kế hoạch Fine-tuning cho Tuần 4.

### Các hạng mục đã hoàn thành:
- **Kiểm tra rò rỉ dữ liệu (Leakage check):** Không có sự trùng lặp giữa tập train (600), dev (200), và test_holdout (200).
- **Tính tái lập (Reproducibility):** Chạy lại mô hình ChunkFormer trên 200 mẫu dev cho kết quả WER exatly match với Day 5 (12.90%).
- **Phân tích Lỗi Y khoa tự động & Audit thủ công:** Hoàn thành audit 30 mẫu có rủi ro cao trên 3 mô hình tiềm năng.
- **Tính toàn vẹn của Benchmark (Benchmark Hygiene):** Data, Metric, và Model integrity đều đạt chuẩn PASS.

---

## 2. Kết quả Đánh giá Mô hình (Dev Leaderboard & Clinical Errors)

Báo cáo đã so sánh 3 mô hình triển vọng nhất (loại bỏ `openai/whisper-small` do WER quá cao 53.23%). Không chỉ dựa vào WER ngôn ngữ tổng quát, đánh giá còn xét trên **6 nhóm rủi ro lâm sàng** (Missing Negation, Symptom, Medication, Dose/Unit, Allergy, Red flag).

| Mô hình | Strict WER | Runtime | Lỗi Lâm sàng Tới hạn (Critical/High) | Đánh giá Trọng tâm |
|---|---:|---|---|---|
| **khanhld/chunkformer-ctc-large-vie** | **12.90%** | Chậm (~1.23s/sample) | **7 samples** (7 phủ định, 7 triệu chứng, 1 liều) | WER tổng quát xuất sắc, tốt nhất. Tuy nhiên, rủi ro y khoa vẫn tương đương họ Whisper. |
| **vinai/PhoWhisper-medium** | 24.64% | Nhanh (~0.42s/sample) | **7 samples** (7 phủ định, 7 triệu chứng, 1 liều) | Tính ổn định (robustness) trong bắt keyword y khoa rất tốt dù WER cao hơn ChunkFormer. |
| **vinai/PhoWhisper-base** | 26.75% | Cực nhanh (~0.14s) | **6 samples** (6 phủ định, 9 triệu chứng, 1 liều) | Phù hợp làm phương án dự phòng cấu hình thấp (edge deployment). |

**Nhận định chuyên sâu từ Clinical NLP Safety Specialist:**
- Mặc dù ChunkFormer có WER xuất sắc (<20%), mô hình này vẫn bỏ sót từ phủ định và triệu chứng với tần suất tương đương `PhoWhisper-medium`. 
- **Kết luận an toàn:** Không có mô hình nào đạt mức "Zero Clinical Risk" dưới dạng off-the-shelf. Lỗi phổ biến nhất và nguy hiểm nhất là **bỏ sót từ phủ định (Negation)**. 

---

## 3. Quyết định Tuyển chọn Mô hình (Model Selection Decision)

Dựa trên nguyên tắc ưu tiên "Độ chính xác tổng quát (Overall Accuracy)" ở giai đoạn baseline để giảm tải công sức hậu kiểm (post-editing), cấu trúc mô hình được chốt như sau:

1. **Primary Model (Dành cho Test Holdout Ngày 7):**
   - Lựa chọn: **`khanhld/chunkformer-ctc-large-vie`**
   - Lý do: Đạt WER xuất sắc nhất (12.90%), vượt xa mục tiêu đề ra. Các lỗi lâm sàng sẽ được ghi nhận và có giải pháp riêng.

2. **Backup & Fine-tuning Candidates (Chiến lược Tuần 4):**
   - Lựa chọn hàng đầu để Fine-tune: **`vinai/PhoWhisper-medium`**
   - Lý do: Kiến trúc Seq2Seq mạnh mẽ, tốc độ inference cực tốt. Mô hình bắt keyword lâm sàng tốt tương đương ChunkFormer và có dư địa lớn để giảm thiểu hiện tượng bỏ sót "từ phủ định" thông qua quá trình fine-tuning có trọng số (weighted loss) tập trung vào Medical Entities.
   - Fallback Option: `vinai/PhoWhisper-base`.

---

## 4. Kế hoạch Ngày 7 (Test Holdout Readiness)

Mô hình ChunkFormer đã được xác nhận sẵn sàng cho giai đoạn đánh giá cuối cùng trên tập `test_holdout`.

**Các hành động ĐƯỢC PHÉP trong Ngày 7:**
- [ ] Chạy ChunkFormer đúng 1 lần duy nhất trên tập `test_holdout`.
- [ ] Tính toán Strict WER / Normalized WER / Strict CER / Normalized CER.
- [ ] Chạy pipeline phân tích lỗi y khoa trên kết quả test.
- [ ] Hoàn thiện Báo cáo Tuần 3 và Quyết định Chọn Mô hình.

**Các quy tắc NGHIÊM CẤM (Safety Guardrails):**
- KHÔNG chạy toàn bộ các mô hình trên tập test để rồi "chọn kết quả tốt nhất".
- KHÔNG điều chỉnh bộ Text Normalization sau khi đã xem kết quả test.
- KHÔNG train/fine-tune trên tập test.
- KHÔNG sửa thủ công (manual fix) các dự đoán của tập test.

*(Chỉ kích hoạt chạy thử nghiệm `PhoWhisper-medium` trên test_holdout nếu ChunkFormer thất bại nghiêm trọng về mặt y khoa, vi phạm license, hoặc có yêu cầu đối chứng đặc biệt từ mentor).*

---

## 5. Cấu trúc Dự án (Project Skeleton)

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
│       └── validation/                 # Kiểm chứng mô hình (Leakage check, audit thủ công, day6 summary)
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

---

## 6. Quyết định Tiền xử lý (Preprocessing Final Decision)

**selected preprocessing = p03_safe_hybrid_v0_1**

p03 is selected by default.
Risky samples with suspected speech truncation are reverted to original clean audio.

## 7. Manual inspection of VAD risky samples

The selected p03 preprocessing produced a small number of VAD-risk cases.

| Split | Rows | VAD fallback | Duration shrink risky | Minimum duration delta | Mean duration delta |
|---|---:|---:|---:|---:|---:|
| train | 600 | 2 | 4 | -2.056s | -0.0599s |
| dev | 200 | 0 | 1 | -1.144s | -0.0724s |

Manual inspection was required before freezing the preprocessing pipeline.

### Manual review outcome

| Decision | Count |
|---|---:|
| keep_p03 | 3 |
| fallback_original | 4 |
| needs_recheck | 0 |

### Final selected manifest

- If no truncation: `vietmed_train_preprocessed_selected_v0_1.jsonl`
- If fallback applied: `vietmed_train_preprocessed_selected_safe_v0_1.jsonl`

---
**Báo cáo này được tổng hợp tự động để làm Context Baseline cho việc lên kế hoạch Fine-tuning Tuần 4.**
