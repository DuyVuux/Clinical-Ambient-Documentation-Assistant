# Báo cáo Đánh giá Mô hình ASR Tiếng Việt Lâm sàng

**Dự án:** Clinical Ambient Documentation Assistant  
**Ngày lập:** 2026-06-06  
**Người lập:** Senior ML Engineer / Clinical ASR Evaluation Specialist  
**Phiên bản:** v1.0  

---

## 1. Tóm tắt điều hành

| Hạng mục | Kết luận |
|---|---|
| **Mô hình chính xác nhất** | `khanhld/chunkformer-ctc-large-vie` — WER 12.90%, vượt xa mục tiêu < 20% |
| **Mô hình thực tiễn nhất** | `vinai/PhoWhisper-medium` — WER 21.51% (normalized), runtime ~0.42s/sample |
| **Đánh đổi chính** | ChunkFormer chính xác nhất nhưng chậm nhất (~1.23s/sample); PhoWhisper nhanh hơn 3–9× nhưng WER cao hơn ~2× |
| **Rủi ro lâm sàng chính** | Tất cả mô hình đều bỏ sót từ phủ định (6–7 lỗi/200 mẫu) — có thể đảo nghĩa lâm sàng |
| **Hành động tiếp theo** | Chạy ChunkFormer trên `test_holdout`; chuẩn bị fine-tuning PhoWhisper-medium cho Tuần 4 |

---

## 2. Mục tiêu đánh giá

Benchmark được thực hiện nhằm:

1. **So sánh các mô hình ASR** cho ngữ cảnh lâm sàng tiếng Việt (ambient clinical documentation).
2. **Đo lường WER/CER** theo cả hai chế độ: strict (nguyên bản) và normalized (chuẩn hóa y khoa).
3. **Phân tích lỗi thuật ngữ lâm sàng** — phát hiện các lỗi bỏ sót/ảo giác từ phủ định, triệu chứng, thuốc, liều lượng.
4. **Đánh giá tính khả thi runtime** cho ứng dụng ghi chép lâm sàng thời gian thực.

**Mục tiêu định lượng:** WER < 20% (theo `experiments/asr/asr_target.md`).  
**Baseline tham chiếu:** Whisper-small fine-tuned trên VietMed, WER ~31% (theo báo cáo mentor).

---

## 3. Dữ liệu và giao thức đánh giá

### 3.1. Tập dữ liệu

| Trường | Giá trị | Nguồn |
|---|---|---|
| Dataset | VietMed (medical speech) | `experiments/asr/ASR_SPLIT_STRATEGY.md` |
| Split đánh giá | dev | `data/data_lake/silver/asr_manifests/splits/vietmed_dev_v0_1.jsonl` |
| Số mẫu | 200 | `experiments/asr/baseline/baseline_leaderboard_dev.md` |
| Train allowed | Không | Quy tắc holdout |

### 3.2. Chiến lược chia tập dữ liệu

- **train_candidate:** 600 mẫu  
- **dev:** 200 mẫu (dùng cho leaderboard/model selection)  
- **test_holdout:** 200 mẫu (chưa sử dụng, dành cho đánh giá cuối)  

> Nguồn: `experiments/asr/ASR_SPLIT_STRATEGY.md`, `experiments/asr/validation/BENCHMARK_HYGIENE_CHECKLIST.md`

### 3.3. Kiểm tra rò rỉ dữ liệu (Leakage Check)

- **Kết quả:** PASS — Không có trùng lặp `sample_id` giữa train/dev/test.
- **Script:** `scripts/asr_eval/check_split_leakage.py`
- **Báo cáo:** `experiments/asr/validation/leakage_check/split_leakage_report.json`

### 3.4. Giao thức đo lường

Theo `experiments/asr/WER_PROTOCOL.md`, báo cáo 4 chỉ số:

1. **Strict WER** — So sánh nguyên bản reference vs prediction
2. **Normalized WER** — Sau khi chuẩn hóa (lowercase, bỏ dấu câu, Unicode NFC, chuẩn hóa đơn vị y khoa)
3. **Strict CER** — Character Error Rate nguyên bản
4. **Normalized CER** — Character Error Rate sau chuẩn hóa

### 3.5. Text Normalization

Theo `scripts/asr_eval/text_normalization_vi.py`:

- Lowercase + Unicode NFC
- Loại bỏ dấu câu
- Chuẩn hóa khoảng trắng
- Chuẩn hóa đơn vị y khoa: `"năm trăm miligam"` → `"500 mg"`, `"ba mươi bảy độ tám"` → `"37.8 độ"`

### 3.6. Script tính WER/CER

- `scripts/asr_eval/compute_wer.py` (sử dụng thư viện `jiwer`)
- Cùng một script và cùng text normalization cho mọi mô hình (đã xác nhận qua Benchmark Hygiene Checklist)

---

## 4. Các mô hình được đánh giá

| Mô hình | Họ kiến trúc | Điểm mạnh | Điểm yếu | Ghi chú inference |
|---|---|---|---|---|
| `khanhld/chunkformer-ctc-large-vie` | CTC (ChunkFormer) | WER thấp nhất, trained trên dữ liệu tiếng Việt lớn | Runtime chậm, license CC BY-NC 4.0 | ~1.23s/sample, cần pipeline CTC riêng |
| `hynt/Zipformer-30M-RNNT-6000h` | ZipFormer RNNT | Norm WER tốt (19.35%), kiến trúc tối ưu | Strict WER cực cao do lỗi in hoa, cần chuẩn hóa | ~1.23s/sample (kể cả overhead) |
| `vinai/PhoWhisper-medium` | Seq2Seq (Whisper) | Cân bằng tốc độ-chất lượng, hệ sinh thái Whisper | WER chưa đạt target < 20% (zero-shot) | ~0.42s/sample trên T4 |
| `vinai/PhoWhisper-base` | Seq2Seq (Whisper) | Runtime cực nhanh, phù hợp edge device | WER cao nhất trong 3 model tiềm năng | ~0.14s/sample trên T4 |
| `nguyenvulebinh/ViStreamASR` | U2-style | Phù hợp streaming | WER khá cao (34.97%) | ~0.2s - 0.3s/clip |
| `openai/whisper-small` | Seq2Seq (Whisper) | Baseline đối chứng quốc tế | WER quá cao trên tiếng Việt y khoa | ~0.26s/sample trên T4 |

> Nguồn: `experiments/asr/asr_target.md`, `experiments/asr/validation/MODEL_SELECTION_DECISION.md`

---

## 5. Kết quả benchmark

### 5.1. Bảng kết quả tổng hợp

| Rank | Mô hình | Strict WER | Norm. WER | Strict CER | Norm. CER | Runtime |
|---:|---|---:|---:|---:|---:|---|
| 1 | `khanhld/chunkformer-ctc-large-vie` | 12.90% | 12.90% | 12.03% | 12.03% | ~1.23s/sample |
| 2 | `hynt/Zipformer-30M-RNNT-6000h` | 104.31% | 19.35% | 85.83% | 18.06% | ~1.23s/sample |
| 3 | `vinai/PhoWhisper-medium` | 24.64% | 21.51% | 19.83% | 19.54% | ~0.42s/sample (T4) |
| 4 | `vinai/PhoWhisper-base` | 26.75% | 24.11% | 21.05% | 20.73% | ~0.14s/sample (T4) |
| 5 | `nguyenvulebinh/ViStreamASR` | 34.97% | 34.97% | 31.48% | 31.48% | ~0.25s/sample |
| 6 | `openai/whisper-small` | 58.58% | 53.23% | 46.69% | 44.85% | ~0.26s/sample (T4) |

> **Nguồn dữ liệu:** `experiments/asr/baseline/baseline_leaderboard_dev.md`  
> **Tính tái lập:** ChunkFormer đã được chạy lại độc lập trên 200 mẫu dev → kết quả khớp chính xác (PASS). Xem `experiments/asr/validation/reproducibility/chunkformer_dev_rerun_metrics.json`

### 5.2. Nhận định

- **ChunkFormer** vượt trội về độ chính xác, đạt WER 12.90% — thấp hơn mục tiêu < 20% gần 40%. Đây là mô hình duy nhất đạt target trên tập dev.
- **Zipformer-30M-RNNT-6000h** có Normalized WER rất tốt (19.35%) đứng thứ 2, tuy nhiên Strict WER cực cao (104.31%) do model xuất ra chữ in hoa toàn bộ, đòi hỏi chuẩn hóa text bắt buộc.
- **PhoWhisper-medium** (Norm. WER 21.51%) gần sát target, có tiềm năng lớn nếu được fine-tuning trên dữ liệu y khoa.
- **PhoWhisper-base** nhanh nhất (0.14s/sample) nhưng Norm. WER 24.11% — phù hợp cho môi trường hạn chế tài nguyên.
- **ViStreamASR** (Norm. WER 34.97%) chưa phù hợp về độ chính xác, dù tốc độ phản hồi tốt.
- **Whisper-small** (Norm. WER 53.23%) không cạnh tranh được trên dữ liệu tiếng Việt y khoa → **loại khỏi pipeline**.

---

## 6. Phân tích lỗi lâm sàng

### 6.1. Phân loại lỗi y khoa (Error Taxonomy)

Theo `experiments/asr/error_analysis/MEDICAL_ASR_ERROR_TAXONOMY.md`, hệ thống phân tích 6 nhóm rủi ro:

| Nhóm lỗi | Mức nghiêm trọng | Ý nghĩa |
|---|---|---|
| Negation (bỏ sót/ảo giác từ phủ định) | **Critical** | Đảo hoàn toàn nghĩa lâm sàng |
| Allergy (sai dị ứng) | **Critical** | Có thể gây phản ứng dị ứng nghiêm trọng |
| Medication (sai tên thuốc) | **High** | Ảnh hưởng ghi chép điều trị |
| Dose/Unit (sai liều/đơn vị) | **High** | Nguy hiểm nếu sai 10× (500mg → 50mg) |
| Symptom (bỏ sót triệu chứng) | **High** | Thiếu thông tin chẩn đoán |
| Red flag (bỏ sót dấu hiệu nguy hiểm) | **High** | Bỏ sót đau ngực/khó thở/sốt cao |

### 6.2. Kết quả phân tích lỗi tự động (3 mô hình, 200 mẫu dev)

**Nguồn:** `experiments/asr/baseline/clinical_error_report_dev.md`

| Mô hình | Bỏ sót Phủ định | Ảo giác Phủ định | Bỏ sót Từ khóa Y khoa | Ảo giác Từ khóa Y khoa | Tổng lỗi y khoa |
|---|---:|---:|---:|---:|---:|
| PhoWhisper-base | 6 | 3 | 13 | 8 | **30** |
| PhoWhisper-medium | 6 | 6 | 8 | 13 | **33** |
| Whisper-small | 20 | 4 | 55 | 1 | **80** |

> Nguồn: `experiments/asr/error_analysis/vietmed_dev_error_analysis_v0_1.md`

### 6.3. Kết quả phân tích lỗi mở rộng (bao gồm ChunkFormer)

**Nguồn:** `experiments/asr/validation/medical_error_analysis/reports/MEDICAL_ASR_ERROR_REPORT.md`

| Mô hình | Phủ định missing | Triệu chứng missing | Thuốc missing | Liều/đơn vị missing | Dị ứng missing | Red flag missing | Mẫu Critical/High |
|---|---:|---:|---:|---:|---:|---:|---:|
| ChunkFormer | 7 | 7 | 0 | 1 | 0 | 0 | **7** |
| Zipformer-30M | 6 | 7 | 0 | 1 | 0 | 0 | **7** |
| PhoWhisper-medium | 7 | 7 | 0 | 1 | 0 | 0 | **7** |
| PhoWhisper-base | 6 | 9 | 0 | 1 | 0 | 0 | **6** |
| ViStreamASR | 13 | 10 | 0 | 1 | 0 | 0 | **14** |

### 6.4. Ví dụ lỗi nguy hiểm (từ Manual Audit 30 mẫu)

**Nguồn:** `experiments/asr/validation/manual_audit/manual_audit_30_samples_3_models.md`

**Ví dụ 1 — Bỏ sót phủ định (Critical):**
- **Reference:** "ta **không** nên sờ nắn bóp vào đấy..."
- **ChunkFormer:** "ta nên sờ nắn bóp vào đấy..." → Mất "không nên", đảo nghĩa khuyến cáo y khoa.
- **PhoWhisper-medium/base:** Giữ được "không nên" → Pass.

**Ví dụ 2 — Bỏ sót phủ định (Critical), cả 3 model đều lỗi:**
- **Reference:** "...đau đớn thế nào thì bây giờ nó **không**"
- **Cả 3 model:** Đều mất từ "không" → Đảo nghĩa tình trạng đau.

**Ví dụ 3 — Ảo giác phủ định (Critical):**
- **Reference:** "...với cột sống ngực đâu bởi vì..."
- **PhoWhisper-medium:** "**không** phải là cổ sống lưng..." → Tự thêm từ phủ định, thay đổi chẩn đoán.

**Ví dụ 4 — Sai thuật ngữ bệnh lý (High):**
- **Reference:** "...người bệnh **parkinson**..."
- **PhoWhisper-medium:** "...người bệnh **bạc kinh doanh**..." → Sai hoàn toàn tên bệnh.

### 6.5. Ma trận rủi ro lâm sàng

| Loại lỗi | Ví dụ thực tế | Mức rủi ro | Giải pháp đề xuất |
|---|---|---|---|
| Bỏ sót phủ định | "không đau" → "đau" | **Critical** | Post-processing LLM + highlight cho bác sĩ |
| Ảo giác phủ định | Tự thêm "không" vào câu | **Critical** | Audio-text anchoring, HITL review |
| Sai tên bệnh | "parkinson" → "bạc kinh doanh" | **High** | Từ điển y khoa (ICD-10) + dictionary enforcing |
| Bỏ sót triệu chứng | Mất "khó thở", "đau ngực" | **High** | Red flag keyword detection |
| Sai liều/đơn vị | "500 mg" → "50 mg" | **High** | Regex extraction + double-check UI |
| Sai thời lượng | "năm năm" → "năm" | **Moderate** | Numeric post-processing |

---

## 7. Đánh đổi tốc độ vs. độ chính xác

### 7.1. Phân tích thực tiễn

| Mô hình | WER (Norm.) | Runtime | Tốc độ tương đối | Phù hợp cho |
|---|---:|---|---|---|
| ChunkFormer | 12.90% | ~1.23s/sample | 1× (chậm nhất) | Offline batch, safety-critical |
| Zipformer-30M | 19.35% | ~1.23s/sample | 1× | CPU deployment, RNNT |
| PhoWhisper-medium | 21.51% | ~0.42s/sample | ~3× nhanh hơn | Near-real-time, fine-tuning candidate |
| PhoWhisper-base | 24.11% | ~0.14s/sample | ~9× nhanh hơn | Real-time, edge device |
| ViStreamASR | 34.97% | ~0.25s/sample | ~5× nhanh hơn | Streaming (cần cải thiện WER) |

### 7.2. Ma trận khuyến nghị theo use case

| Kịch bản sử dụng | Mô hình khuyến nghị | Lý do |
|---|---|---|
| **Batch transcription (offline)** | ChunkFormer | Chính xác nhất, runtime không quan trọng |
| **Interactive clinical assistant** | PhoWhisper-medium (sau fine-tuning) | Cân bằng tốc độ-chất lượng |
| **Baseline cho fine-tuning Tuần 4** | PhoWhisper-medium | Kiến trúc Seq2Seq linh hoạt, runtime tốt |
| **Safety-critical documentation** | ChunkFormer + HITL review | Cần WER thấp nhất + con người kiểm tra |
| **Edge/mobile deployment** | PhoWhisper-base | Runtime 0.14s, chấp nhận WER cao hơn |

---

## 8. Kết luận và khuyến nghị

### 8.1. Kết luận

1. **ChunkFormer-ctc-large-vie** là mô hình tốt nhất về WER (12.90%), vượt mục tiêu < 20%. Đây là benchmark accuracy hiện tại.
2. **Không mô hình nào đạt "Zero Clinical Risk"** ở trạng thái off-the-shelf. Lỗi phủ định (negation) xuất hiện ở cả 3 mô hình với tần suất tương đương (6–7 lỗi/200 mẫu).
3. **PhoWhisper-medium** có tiềm năng lớn nhất cho fine-tuning nhờ runtime nhanh và khả năng bắt keyword y khoa tốt.

### 8.2. Khuyến nghị

| # | Khuyến nghị | Mức ưu tiên |
|---:|---|---|
| 1 | Giữ ChunkFormer làm accuracy benchmark; chạy test_holdout để xác nhận | **Cao** |
| 2 | Sử dụng PhoWhisper-medium/base làm speed-oriented baseline | **Cao** |
| 3 | Ưu tiên giảm lỗi thuật ngữ y khoa, đặc biệt negation deletion | **Cao** |
| 4 | Xây dựng từ điển lâm sàng (ICD-10 + thuốc) cho post-ASR correction | **Cao** |
| 5 | Fine-tuning PhoWhisper-medium trên dữ liệu VietMed (Tuần 4) với weighted loss cho medical entities | **Trung bình** |
| 6 | Bắt buộc Human-in-the-Loop review trước mọi sử dụng lâm sàng | **Cao** |
| 7 | Rà soát license ChunkFormer (CC BY-NC 4.0) nếu triển khai thương mại | **Trung bình** |

---

## 9. Việc cần làm tiếp theo

- [ ] Chạy ChunkFormer trên `test_holdout` (200 mẫu) — đúng 1 lần duy nhất
- [ ] Tính WER/CER strict + normalized trên test_holdout
- [ ] Chạy phân tích lỗi y khoa trên kết quả test_holdout
- [ ] Xác nhận kết quả có tái lập được (reproducibility check)
- [ ] Lưu toàn bộ commands, configs, logs
- [ ] Mở rộng bộ phân loại lỗi lâm sàng (thêm red flag, allergy edge cases)
- [ ] Xây dựng hệ thống flagging confidence thấp cho các đoạn transcript nghi ngờ
- [ ] Đánh giá trên tập test_holdout riêng biệt (chưa từng dùng cho model selection)
- [ ] Chuẩn bị kế hoạch fine-tuning PhoWhisper-medium (data augmentation, weighted loss)
- [ ] Bổ sung biểu đồ/figures cho báo cáo nếu cần

---

## 10. Phụ lục

### 10.1. Lệnh tái tạo kết quả

```bash
# Tính WER/CER cho từng mô hình
cd scripts/asr_eval/
python compute_wer.py \
  --predictions ../../experiments/asr/baseline/predictions/dev/<model>_dev_predictions.jsonl \
  --output ../../experiments/asr/baseline/metrics/dev/<model>_dev_metrics.json

# Kiểm tra leakage
python check_split_leakage.py

# Phân tích lỗi y khoa
python clinical_error_analysis.py
python asr_medical_error_analysis.py
```

### 10.2. Tệp tin tham chiếu trong repository

| Tệp | Nội dung |
|---|---|
| `experiments/asr/WER_PROTOCOL.md` | Giao thức WER/CER |
| `experiments/asr/ASR_SPLIT_STRATEGY.md` | Chiến lược chia tập dữ liệu |
| `experiments/asr/asr_target.md` | Mục tiêu WER < 20% |
| `experiments/asr/baseline/baseline_leaderboard_dev.md` | Bảng xếp hạng dev (4 models) |
| `experiments/asr/baseline/clinical_error_report_dev.md` | Báo cáo lỗi y khoa (3 models PhoWhisper/Whisper) |
| `experiments/asr/error_analysis/vietmed_dev_error_analysis_v0_1.md` | Phân tích lỗi dev v0.1 |
| `experiments/asr/error_analysis/MEDICAL_ASR_ERROR_TAXONOMY.md` | Hệ thống phân loại lỗi ASR lâm sàng |
| `experiments/asr/error_analysis/MODEL_EXPANSION_REPORT.md` | Báo cáo mở rộng ChunkFormer |
| `experiments/asr/validation/MODEL_SELECTION_DECISION.md` | Quyết định chọn mô hình |
| `experiments/asr/validation/BENCHMARK_HYGIENE_CHECKLIST.md` | Checklist vệ sinh benchmark (PASS) |
| `experiments/asr/validation/DAY6_SUMMARY.md` | Tóm tắt validation Day 6 |
| `experiments/asr/validation/medical_error_analysis/reports/MEDICAL_ASR_ERROR_REPORT.md` | Báo cáo lỗi y khoa 3 models (bao gồm ChunkFormer) |
| `experiments/asr/validation/manual_audit/manual_audit_30_samples_3_models.md` | Audit thủ công 30 mẫu |
| `scripts/asr_eval/compute_wer.py` | Script tính WER/CER |
| `scripts/asr_eval/text_normalization_vi.py` | Script chuẩn hóa text tiếng Việt |
| `scripts/asr_eval/clinical_error_analysis.py` | Script phân tích lỗi lâm sàng |
| `scripts/asr_eval/asr_medical_error_analysis.py` | Script phân tích lỗi thuật ngữ y khoa |

### 10.3. Dữ liệu prediction và metrics

| Tệp | Kích thước |
|---|---|
| `experiments/asr/baseline/predictions/dev/chunkformer_ctc_large_vie_dev_predictions.jsonl` | 126 KB |
| `experiments/asr/baseline/predictions/dev/phowhisper_medium_dev_predictions.jsonl` | 118 KB |
| `experiments/asr/baseline/predictions/dev/phowhisper_base_dev_predictions.jsonl` | 118 KB |
| `experiments/asr/baseline/predictions/dev/whisper_small_dev_predictions.jsonl` | 117 KB |
| `experiments/asr/baseline/metrics/dev/chunkformer_ctc_large_vie_dev_metrics.json` | 186 KB |
| `experiments/asr/baseline/metrics/dev/phowhisper_medium_dev_metrics.json` | 189 KB |
| `experiments/asr/baseline/metrics/dev/phowhisper_base_dev_metrics.json` | 189 KB |
| `experiments/asr/baseline/metrics/dev/whisper_small_dev_metrics.json` | 187 KB |

### 10.4. Giả định

1. Tất cả số liệu WER/CER được lấy trực tiếp từ các file trong repository, không phải số liệu tự tạo.
2. Runtime được đo trên Google Colab T4 GPU (cho PhoWhisper/Whisper) và môi trường tương đương cho ChunkFormer.
3. Tập dev (200 mẫu) được dùng cho model selection; tập test_holdout (200 mẫu) chưa được sử dụng.
4. Phân tích lỗi y khoa dựa trên từ điển tại `experiments/asr/error_analysis/medical_terms_for_asr_check.json` gồm 6 nhóm: negation, symptom, medication, allergy, dose_unit, red_flag.

### 10.5. Thông tin còn thiếu

| Thông tin | Trạng thái | Cần thực hiện |
|---|---|---|
| Kết quả trên test_holdout | Chưa chạy | Chạy ChunkFormer trên test_holdout (Ngày 7) |
| Phân tích lỗi Whisper-small chi tiết (medical) | Đã có trong error_analysis nhưng model đã bị loại | Không cần hành động |
| Fine-tuning results | Chưa thực hiện | Kế hoạch Tuần 4 |
| Đánh giá trên dữ liệu lâm sàng thực (non-VietMed) | Chưa có | Cần thu thập dữ liệu mới |

---

*Báo cáo này được tổng hợp từ dữ liệu thực tế trong repository dự án. Mọi con số đều có nguồn tham chiếu cụ thể.*
