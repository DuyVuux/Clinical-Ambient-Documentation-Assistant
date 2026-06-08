# Clinical Ambient Documentation Assistant — README kỹ thuật & vận hành

> Phiên bản README này được viết để bàn giao cho mentor/sếp hoặc người mới vào dự án có thể hiểu bối cảnh, kiểm tra dữ liệu, chạy pipeline ASR, đánh giá WER/CER, phân tích lỗi lâm sàng và tiếp tục fine-tune một cách có kiểm soát.

---

## 0. Tóm tắt dự án

**Clinical Ambient Documentation Assistant** là hệ thống hỗ trợ bác sĩ ghi chép y bạ tự động từ hội thoại khám bệnh tiếng Việt.

Pipeline mục tiêu:

```text
Thu âm cuộc khám
→ ASR tiếng Việt / ASR y tế
→ transcript có timestamp
→ phân đoạn người nói
→ gán vai trò Doctor / Patient / Caregiver / Nurse / Unknown
→ trích xuất clinical facts có source evidence
→ sinh SOAP-lite note draft
→ bác sĩ review / chỉnh sửa / xác nhận
→ dữ liệu đã xác nhận mới được xem là Gold
```

Dự án ưu tiên triết lý:

```text
Local-first
Privacy-by-design
Doctor-in-the-loop
Evidence-first
Synthetic-first
Evaluation-before-training
```

Hệ thống **không phải AI doctor**, **không tự chẩn đoán**, **không tự kê đơn**, và **không được tự động ghi thẳng vào hồ sơ bệnh án nếu chưa có bác sĩ xác nhận**.

---

## 1. Trạng thái nghiên cứu hiện tại

### 1.1. Tuần 1–2: Synthetic outpatient data v0.1

Đã xây dựng bộ synthetic outpatient encounters để kiểm thử end-to-end downstream clinical NLP/SOAP.

Mỗi case trong:

```text
data/synthetic_data/outpatient_v0_1/
```

có cấu trúc logic:

```text
script.md
→ transcript_segments_gold.json
→ clinical_facts_candidate.json
→ clinical_facts_gold.json
→ soap_note_gold.md
→ soap_source_evidence.json
→ annotation_notes.md
→ encounter_metadata.json
→ encounter_outcome.json
```

Mục tiêu của synthetic data:

```text
- kiểm thử schema
- kiểm thử source attribution
- kiểm thử negation
- kiểm thử medication/dose/allergy
- kiểm thử caregiver attribution
- kiểm thử SOAP-lite note draft
- không dùng để đo WER nếu chưa có audio thật/TTS/volunteer audio
```

Ví dụ nhóm lỗi safety đã được đưa vào synthetic cases:

```text
- mất phủ định: "không đau ngực" → "đau ngực"
- mất dị ứng: "chưa từng dị ứng thuốc"
- sai thuốc/liều: paracetamol 500mg
- sai duration: 3 ngày, 2 ngày, 1 tuần
- gán nhầm clinical_subject khi caregiver nói thay patient
```

---

### 1.2. Tuần 3: ASR ingestion + benchmark foundation

Tuần 3 đã chuyển từ “ingest public data” sang **ASR benchmark track** vì mục tiêu thực tế là:

```text
Baseline sếp báo: Whisper-small trên VietMed WER khoảng 31%
Mục tiêu mới: dùng model bất kỳ đạt WER < 20%
```

Đã ingest VietMed vào data lake và tạo split:

```text
VietMed total: 1050 samples
train_candidate: 600
dev: 200
test_holdout: 200
train_allowed: 600
split_mode: full_dataset_split
```

Quy tắc split:

```text
train_candidate: dùng cho fine-tune nếu được phép
dev: dùng chọn model / chọn preprocessing / chọn checkpoint
test_holdout: chỉ dùng đánh giá cuối cùng, không dùng để tune
```

Kết quả dev đáng chú ý từ tuần 3:

```text
openai/whisper-small: WER rất cao, bị loại khỏi nhóm candidate chính
vinai/PhoWhisper-base: nhanh, WER khoảng 26.75% trên dev
vinai/PhoWhisper-medium: WER khoảng 24.64% trên dev
khanhld/chunkformer-ctc-large-vie: WER khoảng 12.90% trên dev
```

Kết luận tuần 3:

```text
ChunkFormer là primary inference baseline vì WER tốt nhất.
PhoWhisper-medium/base vẫn là fine-tuning candidate vì kiến trúc Whisper-family dễ thích nghi với pipeline Seq2Seq.
WER thấp chưa đủ vì vẫn còn lỗi lâm sàng như missing negation, symptom, dose/unit.
```

---

### 1.3. Tuần 4: Data preprocessing trước fine-tune

Sau phân tích lỗi, quyết định **không fine-tune ngay** mà dành tuần 4 để tiền xử lý dữ liệu.

Lý do:

```text
Vấn đề không chỉ nằm ở model.
Một phần lỗi ASR đến từ dữ liệu audio:
- năng lượng đầu/cuối câu yếu
- edge-loss risk
- boundary context chưa đủ
- VAD/chunking/padding cần được kiểm chứng
```

Kết quả Day 1 Week 4 audio QA:

```text
Train 600:
- edge_loss_risk: 110/600 ≈ 18.3%
- long_leading_silence: 2
- long_trailing_silence: 3
- too_quiet: 0
- clipping_detected: 0

Dev 200:
- edge_loss_risk: 29/200 ≈ 14.5%
- long_leading_silence: 1
- long_trailing_silence: 1
- too_quiet: 0
- clipping_detected: 0
```

Kết luận:

```text
Không ưu tiên loudnorm/compressor/noise reduction ở vòng đầu.
Ưu tiên kiểm thử padding và VAD-padding.
```

Các variant đã test:

```text
p03_vad_pad_200ms
p04_vad_pad_300ms
p05_vad_pad_500ms
p10_edge_pad_200ms
p11_edge_pad_300ms
p12_edge_pad_500ms
```

Sau padding-aware audit và ASR/clinical error analysis, quyết định Day 5:

```text
Selected preprocessing: p03_vad_pad_200ms
```

Lý do chọn p03:

```text
Full dev WER:
- original: 12.90%
- p10_edge_pad_200ms: 14.49%
- p03_vad_pad_200ms: 12.90%

Edge-risk subset WER:
- original: 11.87%
- p10: 13.02%
- p03: 11.59%

Clinical errors:
- p03 không làm tăng missing negation
- p03 không làm tăng missing symptom
- p03 không làm tăng medication/dose/numeric error
```

Lưu ý Day 6:

```text
p03 có một số mẫu duration_shrink_risky:
- train: 4 samples
- dev: 1 sample
Cần manual inspection trước khi freeze hoàn toàn.
Nếu có dấu hiệu VAD cắt speech, tạo p03_safe_hybrid_v0_1 bằng cách fallback riêng sample lỗi về original.
```

---

## 2. Nguyên tắc an toàn và governance

### 2.1. Không dùng real patient data khi chưa phê duyệt

Mọi dữ liệu bệnh nhân thật phải có:

```text
- phê duyệt governance/legal/clinical
- consent hoặc cơ sở pháp lý rõ
- retention policy
- access control
- audit log
- de-identification nếu phù hợp
```

Trong giai đoạn hiện tại:

```text
Synthetic data: dùng cho downstream NLP/SOAP/evidence pipeline
VietMed: dùng nội bộ cho ASR training/evaluation theo phê duyệt hiện tại
Common Voice/FOSD: dùng bootstrap/general ASR nếu license phù hợp
Real patient data: chưa dùng
```

### 2.2. Không trộn nhầm data lake zones

```text
Bronze:
  raw audio, raw transcript, raw metadata, checksum, license snapshot

Silver:
  clean audio, preprocessed audio, normalized transcript, ASR manifest, split manifest

Gold:
  transcript/facts/note đã review/xác nhận

Evaluation:
  frozen holdout sets, không train, không tune

Dictionary:
  terminology, aliases, medical terms, negation cues

Audit:
  review logs, model run logs, correction logs
```

### 2.3. Test holdout là bất khả xâm phạm

```text
Không train trên test_holdout.
Không chọn model bằng test_holdout.
Không chọn preprocessing bằng test_holdout.
Không chỉnh text normalization sau khi xem test.
Không manual fix prediction trên test.
```

---

## 3. Cấu trúc thư mục chính

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

---

## 4. Thiết lập môi trường

### 4.1. Yêu cầu hệ thống

Khuyến nghị:

```text
OS: Ubuntu 22.04/24.04 hoặc WSL2 Ubuntu
Python: 3.10+
RAM: ≥ 16GB
GPU: khuyến nghị nếu chạy Whisper/PhoWhisper/fine-tune
Disk: cần đủ dung lượng cho audio, predictions, checkpoints
```

Công cụ hệ thống:

```bash
sudo apt update
sudo apt install -y ffmpeg libsndfile1 git git-lfs
```

Kiểm tra:

```bash
ffmpeg -version
python --version
```

### 4.2. Tạo virtual environment

```bash
cd "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"

python -m venv .venv
source .venv/bin/activate

pip install -U pip setuptools wheel
```

### 4.3. Cài dependencies

Nếu repo đã có `requirements.txt`:

```bash
pip install -r requirements.txt
```

Nếu thiếu package khi chạy ASR/preprocessing:

```bash
pip install numpy pandas scipy soundfile librosa tqdm jiwer
pip install torch torchaudio transformers accelerate datasets
```

Nếu dùng Silero VAD qua `torch.hub`, cần internet lần đầu hoặc cache model sẵn.

### 4.4. Biến môi trường nên dùng

```bash
export PROJECT_ROOT="/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
export DATA_ROOT="$PROJECT_ROOT/data"
```

---

## 5. Kiểm tra data hiện có

### 5.1. Kiểm tra manifest split

```bash
cd "$PROJECT_ROOT"
source .venv/bin/activate

wc -l \
data/data_lake/silver/asr_manifests/splits/vietmed_train_candidate_v0_1.jsonl \
data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
data/data_lake/evaluation/asr_eval_v0_1/vietmed_test_holdout_v0_1.jsonl
```

Kỳ vọng:

```text
600 vietmed_train_candidate_v0_1.jsonl
200 vietmed_dev_v0_1.jsonl
200 vietmed_test_holdout_v0_1.jsonl
```

### 5.2. Kiểm tra manifest hợp lệ

```bash
python scripts/asr_eval/check_asr_manifest.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_train_candidate_v0_1.jsonl

python scripts/asr_eval/check_asr_manifest.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl
```

Kỳ vọng:

```text
Missing audio: 0
Missing transcript: 0
```

Với train:

```text
train_allowed_count: 600
```

Với dev:

```text
train_allowed_count: 0
```

### 5.3. Kiểm tra leakage

Nếu script `check_split_leakage.py` hỗ trợ các tham số train/dev/test:

```bash
python scripts/asr_eval/check_split_leakage.py \
  --train data/data_lake/silver/asr_manifests/splits/vietmed_train_candidate_v0_1.jsonl \
  --dev data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --test data/data_lake/evaluation/asr_eval_v0_1/vietmed_test_holdout_v0_1.jsonl
```

Kỳ vọng:

```text
PASS
No overlap between train/dev/test
```

---

## 6. Chạy ASR baseline trên dev

### 6.1. Chạy ChunkFormer trên dev

```bash
python scripts/asr_eval/run_chunkformer_ctc.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --model khanhld/chunkformer-ctc-large-vie \
  --output experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl
```

### 6.2. Tính WER/CER

```bash
python scripts/asr_eval/compute_wer.py \
  --predictions experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl \
  --output experiments/asr/baseline/metrics/dev/chunkformer_dev_metrics.json
```

Kỳ vọng tham chiếu hiện tại:

```text
ChunkFormer dev WER khoảng 12.90%
```

### 6.3. Chạy medical error analysis

```bash
python scripts/asr_eval/asr_medical_error_analysis.py \
  --predictions experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl \
  --terms experiments/asr/error_analysis/medical_terms_for_asr_check.json \
  --output experiments/asr/error_analysis/dev/chunkformer_dev_medical_errors.json
```

---

## 7. Chạy Week 4 preprocessing pipeline

### 7.1. Day 1 — Audio QA

Chạy audit cho train:

```bash
python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_train_candidate_v0_1.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/train \
  --project_root "$PROJECT_ROOT"
```

Chạy audit cho dev:

```bash
python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/dev \
  --project_root "$PROJECT_ROOT"
```

Các chỉ số cần đọc:

```text
edge_loss_risk
long_leading_silence
long_trailing_silence
too_quiet
clipping_detected
min_edge_to_middle_ratio
```

Kết quả hiện tại:

```text
train edge_loss_risk: 110/600
dev edge_loss_risk: 29/200
too_quiet: 0
clipping_detected: 0
```

---

### 7.2. Day 2 — Build preprocessing variants

Tạo VAD-padding variants:

```bash
python scripts/asr_preprocess/build_preprocess_variants.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --project_root "$PROJECT_ROOT" \
  --variants p03_vad_pad_200ms p04_vad_pad_300ms p05_vad_pad_500ms \
  --enable_vad
```

Tạo padding-only variants nếu cần:

```bash
python scripts/asr_preprocess/build_preprocess_variants.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --project_root "$PROJECT_ROOT" \
  --variants p10_edge_pad_200ms p11_edge_pad_300ms p12_edge_pad_500ms
```

Kiểm tra:

```bash
wc -l data/data_lake/silver/asr_manifests/preprocessing_variants/*.jsonl
```

Kỳ vọng mỗi dev variant có 200 dòng.

---

### 7.3. Day 3 — Audit variants

Audit từng variant:

```bash
python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p03_vad_pad_200ms.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/variants/p03_vad_pad_200ms \
  --project_root "$PROJECT_ROOT"

python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p04_vad_pad_300ms.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/variants/p04_vad_pad_300ms \
  --project_root "$PROJECT_ROOT"

python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p05_vad_pad_500ms.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/variants/p05_vad_pad_500ms \
  --project_root "$PROJECT_ROOT"
```

Tổng hợp:

```bash
python scripts/asr_preprocess/summarize_variant_audio_qa.py \
  --project_root "$PROJECT_ROOT"
```

Chạy padding-aware audit:

```bash
python scripts/asr_preprocess/audit_audio_quality_padding_aware.py \
  --manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p03_vad_pad_200ms.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/padding_aware/p03_vad_pad_200ms \
  --project_root "$PROJECT_ROOT"
```

Kết luận hiện tại:

```text
p03_vad_pad_200ms là variant tốt nhất để kiểm thử ASR.
p10_edge_pad_200ms không đủ tốt sau ASR/clinical error analysis.
p04/p05 300–500ms không được chọn.
```

---

### 7.4. Day 4 — ASR preprocessing A/B test

Chạy ChunkFormer cho original:

```bash
python scripts/asr_eval/run_chunkformer_ctc.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --model khanhld/chunkformer-ctc-large-vie \
  --output experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_original_dev_predictions.jsonl
```

Chạy cho p10:

```bash
python scripts/asr_eval/run_chunkformer_ctc.py \
  --manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p10_edge_pad_200ms.jsonl \
  --model khanhld/chunkformer-ctc-large-vie \
  --output experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_p10_edge_pad_200ms_dev_predictions.jsonl
```

Chạy cho p03:

```bash
python scripts/asr_eval/run_chunkformer_ctc.py \
  --manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p03_vad_pad_200ms.jsonl \
  --model khanhld/chunkformer-ctc-large-vie \
  --output experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_p03_vad_pad_200ms_dev_predictions.jsonl
```

Tính WER/CER:

```bash
python scripts/asr_eval/compute_wer.py \
  --predictions experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_original_dev_predictions.jsonl \
  --output experiments/asr/preprocessing/ablation/metrics/dev/chunkformer_original_dev_metrics.json

python scripts/asr_eval/compute_wer.py \
  --predictions experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_p10_edge_pad_200ms_dev_predictions.jsonl \
  --output experiments/asr/preprocessing/ablation/metrics/dev/chunkformer_p10_edge_pad_200ms_dev_metrics.json

python scripts/asr_eval/compute_wer.py \
  --predictions experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_p03_vad_pad_200ms_dev_predictions.jsonl \
  --output experiments/asr/preprocessing/ablation/metrics/dev/chunkformer_p03_vad_pad_200ms_dev_metrics.json
```

---

### 7.5. Day 5 — Clinical error + edge-risk subset analysis

Chạy medical error analysis:

```bash
python scripts/asr_eval/asr_medical_error_analysis.py \
  --predictions experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_original_dev_predictions.jsonl \
  --terms experiments/asr/error_analysis/medical_terms_for_asr_check.json \
  --output experiments/asr/preprocessing/clinical_error_ablation/original_medical_errors.json

python scripts/asr_eval/asr_medical_error_analysis.py \
  --predictions experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_p10_edge_pad_200ms_dev_predictions.jsonl \
  --terms experiments/asr/error_analysis/medical_terms_for_asr_check.json \
  --output experiments/asr/preprocessing/clinical_error_ablation/p10_edge_pad_200ms_medical_errors.json

python scripts/asr_eval/asr_medical_error_analysis.py \
  --predictions experiments/asr/preprocessing/ablation/predictions/dev/chunkformer_p03_vad_pad_200ms_dev_predictions.jsonl \
  --terms experiments/asr/error_analysis/medical_terms_for_asr_check.json \
  --output experiments/asr/preprocessing/clinical_error_ablation/p03_vad_pad_200ms_medical_errors.json
```

Kết luận hiện tại:

```text
Selected preprocessing = p03_vad_pad_200ms
```

---

### 7.6. Day 6 — Apply selected preprocessing

Apply p03 cho train:

```bash
python scripts/asr_preprocess/build_preprocess_variants.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_train_candidate_v0_1.jsonl \
  --project_root "$PROJECT_ROOT" \
  --variants p03_vad_pad_200ms \
  --enable_vad
```

Tạo selected manifest:

```bash
python scripts/asr_preprocess/create_selected_preprocessing_manifests.py \
  --train_p03_manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_train_candidate_p03_vad_pad_200ms.jsonl \
  --dev_p03_manifest data/data_lake/silver/asr_manifests/preprocessing_variants/vietmed_dev_p03_vad_pad_200ms.jsonl \
  --output_train_selected data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_v0_1.jsonl \
  --output_dev_selected data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_v0_1.jsonl \
  --project_root "$PROJECT_ROOT" \
  --selected_variant p03_vad_pad_200ms
```

Kiểm tra:

```bash
python scripts/asr_eval/check_asr_manifest.py \
  --manifest data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_v0_1.jsonl

python scripts/asr_eval/check_asr_manifest.py \
  --manifest data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_v0_1.jsonl
```

Kỳ vọng:

```text
train: 600 rows, train_allowed_count 600
dev: 200 rows, train_allowed_count 0
missing audio: 0
missing transcript: 0
```

---

## 8. Manual inspection cho VAD-risk samples

Sau khi apply p03, cần kiểm tra các sample bị VAD cắt ngắn đáng kể.

Kết quả hiện tại:

```text
Train:
- rows: 600
- vad_fallback: 2
- duration_shrink_risky: 4
- min_delta: -2.056s
- mean_delta: -0.0599s

Dev:
- rows: 200
- vad_fallback: 0
- duration_shrink_risky: 1
- min_delta: -1.144s
- mean_delta: -0.0724s
```

Quy tắc:

```text
Nếu nghe thủ công và p03 không mất speech → giữ p03.
Nếu p03 bị cắt mất chữ đầu/cuối → fallback riêng sample đó về original.
```

Nếu có fallback riêng sample lỗi, tạo variant:

```text
p03_safe_hybrid_v0_1
```

Ý nghĩa:

```text
Mặc định dùng p03_vad_pad_200ms.
Chỉ sample bị VAD cắt speech mới quay về original clean audio.
```

---

## 9. Fine-tune readiness cho tuần 5

Trước khi fine-tune, cần có:

```text
data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_v0_1.jsonl
data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_v0_1.jsonl
```

hoặc nếu dùng hybrid:

```text
data/data_lake/silver/asr_manifests/vietmed_train_preprocessed_selected_safe_v0_1.jsonl
data/data_lake/silver/asr_manifests/vietmed_dev_preprocessed_selected_safe_v0_1.jsonl
```

Không được fine-tune trên:

```text
data/data_lake/evaluation/asr_eval_v0_1/vietmed_test_holdout_v0_1.jsonl
```

---

## 10. Hướng dẫn Week 5 — Fine-tune

### 10.1. Mục tiêu

```text
Fine-tune model ASR trên train selected manifest.
Chọn checkpoint bằng dev selected manifest.
Chỉ chạy test_holdout sau khi model + preprocessing đã freeze.
```

### 10.2. Candidate models

```text
Primary inference baseline:
- khanhld/chunkformer-ctc-large-vie

Fine-tune candidates:
- vinai/PhoWhisper-medium
- vinai/PhoWhisper-base
- openai/whisper-small nếu cần đối chứng
```

### 10.3. Không được làm

```text
Không dùng dev để train.
Không dùng test để chọn checkpoint.
Không đổi normalization sau khi xem test.
Không báo WER nếu không nói rõ strict hay normalized.
```

---

## 11. Cách đọc kết quả WER/CER

Luôn báo cáo đủ:

```text
strict WER
normalized WER
strict CER
normalized CER
```

Trong clinical ASR, cần báo cáo thêm:

```text
missing negation
missing symptom
medication error
dose/unit error
allergy error
numeric error
red-flag term error
```

Ví dụ bảng chuẩn:

```markdown
| Model | Preprocessing | Split | Strict WER | Normalized WER | Missing negation | Missing symptom | Dose/unit error |
|---|---|---|---:|---:|---:|---:|---:|
| ChunkFormer | p03 | dev | 12.90% | TBD | 7 | 7 | 1 |
```

---

## 12. Troubleshooting

### 12.1. `Missing audio > 0`

Kiểm tra field trong manifest:

```text
clean_audio_path
preprocessed_audio_path
raw_audio_path
audio
```

Chạy:

```bash
python scripts/asr_eval/check_asr_manifest.py --manifest <manifest.jsonl>
```

### 12.2. `train_allowed_count` sai

Quy tắc:

```text
train manifest: train_allowed = true
dev manifest: train_allowed = false
test_holdout: train_allowed = false
```

### 12.3. Silero VAD lỗi

Nếu VAD không load được:

```bash
pip install torch torchaudio
```

Nếu vẫn lỗi, chạy padding-only hoặc fallback original. Không được tiếp tục nếu không hiểu VAD đang làm gì.

### 12.4. WER tăng sau preprocessing

Không cố ép preprocessing.

Quy tắc:

```text
Nếu preprocessing không cải thiện WER hoặc clinical errors, giữ original.
```

### 12.5. Duration shrink risky

Cần nghe thủ công.

```text
Nếu p03 chỉ cắt silence/noise → giữ.
Nếu p03 cắt speech → fallback sample đó về original.
```

---

## 13. Checklist bàn giao cho mentor/sếp

### Dữ liệu

```text
[ ] VietMed 1050 samples đã có trong Silver
[ ] train/dev/test = 600/200/200
[ ] test_holdout chưa dùng để tune
[ ] selected train/dev manifest đã có
[ ] raw audio không bị overwrite
```

### Benchmark

```text
[ ] ChunkFormer baseline dev WER khoảng 12.90%
[ ] Có WER/CER JSON
[ ] Có medical error analysis
[ ] Có leakage check
```

### Preprocessing

```text
[ ] Audio QA train/dev
[ ] Variant QA
[ ] Padding-aware QA
[ ] ASR ablation original/p10/p03
[ ] Selected preprocessing = p03_vad_pad_200ms hoặc p03_safe_hybrid_v0_1
[ ] Manual inspection cho duration_shrink_risky
```

### Fine-tune readiness

```text
[ ] selected train manifest ready
[ ] selected dev manifest ready
[ ] fine-tune config ready
[ ] test_holdout untouched
```

---

## 14. Lộ trình tiếp theo

### Week 5 — Fine-tune

```text
Day 1:
- kiểm tra selected manifests
- tạo HF train/dev format
- chạy smoke fine-tune

Day 2:
- fine-tune PhoWhisper-base/medium

Day 3:
- đánh giá dev WER/CER
- clinical error analysis

Day 4:
- tinh chỉnh training config nếu cần

Day 5:
- chọn checkpoint tốt nhất theo dev

Day 6:
- chạy test_holdout một lần nếu đã freeze model + preprocessing

Day 7:
- viết báo cáo Week 5
```

### Sau Week 5

```text
- bổ sung volunteer/actor audio từ synthetic scripts
- mở rộng dictionary y khoa
- nối ASR output sang clinical fact extraction
- chạy downstream NLP/SOAP evaluation
- xây review UI hoặc review JSON workflow
```

---

## 15. Quy tắc vàng của dự án

```text
Data trước, model sau.
Evidence trước, note sau.
Synthetic trước, real patient sau.
Gold review trước, training sau.
Dev để chọn, test để xác nhận.
WER thấp chưa đủ, clinical error phải thấp.
Không có source evidence thì không đưa vào note.
Không có doctor confirmation thì không thành Gold.
```

---

## 16. Quickstart cho người chỉ muốn chạy kiểm tra nhanh

```bash
cd "/home/duykhongngu28/massive/Clinical Ambient Documentation Assistant"
source .venv/bin/activate
export PROJECT_ROOT="$(pwd)"

# 1. Kiểm tra manifest
python scripts/asr_eval/check_asr_manifest.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl

# 2. Chạy ChunkFormer dev
python scripts/asr_eval/run_chunkformer_ctc.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --model khanhld/chunkformer-ctc-large-vie \
  --output experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl

# 3. Tính WER/CER
python scripts/asr_eval/compute_wer.py \
  --predictions experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl \
  --output experiments/asr/baseline/metrics/dev/chunkformer_dev_metrics.json

# 4. Chạy audio QA dev
python scripts/asr_preprocess/audit_audio_quality.py \
  --manifest data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl \
  --output_dir experiments/asr/preprocessing/audio_quality_audit/dev \
  --project_root "$PROJECT_ROOT"

# 5. Chạy medical error analysis
python scripts/asr_eval/asr_medical_error_analysis.py \
  --predictions experiments/asr/baseline/predictions/dev/chunkformer_dev_predictions.jsonl \
  --terms experiments/asr/error_analysis/medical_terms_for_asr_check.json \
  --output experiments/asr/error_analysis/dev/chunkformer_dev_medical_errors.json
```

---

## 17. Ghi chú quan trọng cho sếp/mentor

Hiện tại pipeline ASR đã đạt mục tiêu WER < 20% trên dev với ChunkFormer, nhưng dự án không dừng ở WER. Vì đây là clinical ASR, cần tiếp tục kiểm soát lỗi lâm sàng:

```text
- missing negation
- missing symptom
- medication error
- dose/unit error
- allergy error
- numeric error
```

Tuần 4 đã chứng minh cách làm đúng là:

```text
Không fine-tune ngay.
Audit audio trước.
Tạo preprocessing variants có version.
A/B test trên dev.
Chọn preprocessing bằng WER + clinical error.
Manual inspect các sample VAD-risk trước khi freeze.
```

Đây là nền tảng bắt buộc để Week 5 fine-tune không rơi vào tình trạng “train trên dữ liệu bẩn” hoặc đạt WER đẹp nhưng tăng rủi ro lâm sàng.
