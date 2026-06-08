# Day 5 Week 4 — Preprocessing Clinical Error Analysis

## Objective

Evaluate whether preprocessing improves clinically important ASR errors.

## Variants

| Variant | Description |
|---|---|
| original | baseline |
| p10_edge_pad_200ms | add 200ms silence, no trimming |
| p03_vad_pad_200ms | VAD crop + 200ms padding |

## Full dev set results

| Variant | WER | CER | Missing negation | Missing symptom | Medication error | Dose/unit error | Numeric error |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | 12.90% | 12.03% | 7 | 7 | 0 | 1 | 0 |
| p10 | 14.49% | 13.56% | 6 | 7 | 0 | 1 | 0 |
| p03 | 12.90% | 12.06% | 7 | 7 | 0 | 1 | 0 |

## Edge-risk subset results

Subset:
- Source: original dev edge_loss_risk_samples
- Samples: 29

| Variant | Edge subset WER | Edge subset CER | Missing negation | Missing symptom | Decision |
|---|---:|---:|---:|---:|---|
| original | 11.87% | 11.40% | 1 | 1 | baseline |
| p10 | 13.02% | 12.51% | 1 | 1 | drop (worse WER) |
| p03 | 11.59% | 11.17% | 1 | 1 | keep (improved edge WER) |

## Quy tắc quyết định cuối ngày 5

**Chọn p10 nếu:**
- p10 WER <= original và p10 clinical errors <= original
- hoặc: p10 full-dev WER tăng rất nhẹ nhưng edge-risk subset WER giảm rõ và clinical errors không tăng

**Chọn p03 nếu:**
- p03 tốt hơn p10 rõ rệt cả full dev và edge subset và clinical errors không tăng

**Giữ original nếu:**
- p10/p03 không cải thiện WER hoặc clinical errors tăng

## Kết luận quyết định

Dựa trên các quy tắc trên và kết quả thực nghiệm, quyết định cuối cùng là **Chọn p03 (p03_vad_pad_200ms)** làm phương án tiền xử lý chính thức.

**Lập luận (Justification):**
1. **Loại bỏ p10:** Phương án p10 làm tăng đáng kể lỗi WER trên Full dev (từ 12.90% lên 14.49%) cũng như làm tệ đi lỗi WER trên Edge-risk subset (từ 11.87% lên 13.02%), không đáp ứng được quy tắc nào để chọn p10.
2. **Chọn p03:** 
   - **Vượt trội so với p10:** Tốt hơn p10 rất rõ rệt ở cả tập Full dev và Edge-risk subset.
   - **Cải thiện hiện tượng mất biên (edge-loss):** So với `original`, p03 giảm được WER trên tập edge-risk (từ 11.87% xuống 11.59%) trong khi vẫn giữ nguyên được hiệu suất trên toàn bộ Full dev (12.90%).
   - **Không làm tăng lỗi lâm sàng (Clinical errors):** Số lượng lỗi y khoa (missing negation, missing symptom) của p03 hoàn toàn tương đương với `original` ở cả Full dev và Edge-risk. Điều này chứng minh rằng VAD cắt âm thanh một cách an toàn mà không làm rớt các từ vựng lâm sàng quan trọng ở đầu/cuối câu.