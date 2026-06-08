# Day 4 Week 4 — ASR Preprocessing Ablation Report

## Objective

Đánh giá hiệu quả của các kỹ thuật tiền xử lý âm thanh (padding) trước khi đưa vào huấn luyện hoặc áp dụng trên tập test holdout. Báo cáo này tổng hợp kết quả chạy mô hình ASR (ChunkFormer) trên các phiên bản âm thanh khác nhau để chọn ra phương pháp tiền xử lý tốt nhất.

## Execution Checklist

- [x] Chạy ChunkFormer trên `original`
- [x] Chạy ChunkFormer trên `p10_edge_pad_200ms`
- [x] Chạy ChunkFormer trên `p03_vad_pad_200ms`
- [x] Có prediction JSONL cho 3 variant (lưu tại `predictions/dev/`)
- [x] Có WER/CER JSON cho 3 variant (lưu tại `metrics/dev/`)
- [x] Có DAY4_ASR_PREPROCESSING_ABLATION.md
- [x] Chưa dùng test_holdout
- [x] Chưa fine-tune

## Kết quả & Đánh giá (Leaderboard)

| Variant | Model | WER | CER | Medical errors | Edge-risk subset WER | Decision |
|---|---|---|---|---|---|---|
| original | ChunkFormer | 12.90% | 12.03% | 7 | 12.18% | baseline |
| p10_edge_pad_200ms | ChunkFormer | 14.49% | 13.56% | 6 | 13.49% | drop (worse WER) |
| p03_vad_pad_200ms | ChunkFormer | 12.90% | 12.06% | 7 | 11.81% | keep (improved edge WER) |

**Phân tích:**
- Variant `p10_edge_pad_200ms` làm tăng lỗi WER một cách rõ rệt trên tập dev (lên 14.49%), nên đã bị loại.
- Variant `p03_vad_pad_200ms` giữ vững được hiệu năng tổng thể (WER 12.90% bằng với baseline) nhưng đã giúp cải thiện đáng kể lỗi trên tập con những audio bị cắt quá sát rìa (Edge-risk subset WER giảm từ 12.18% xuống còn 11.81%). Số lượng medical errors không bị tăng thêm (vẫn duy trì ở mức 7 lỗi).

## Quyết định cuối cùng (Decision)
Dựa vào quy tắc đánh giá đã đề ra, phương án **`p03_vad_pad_200ms`** (VAD + 200ms padding) được chọn làm phương pháp preprocessing tối ưu để tiếp tục xử lý trên tập train phục vụ cho giai đoạn fine-tuning sắp tới. Không áp dụng padding ngây thơ (`p10`) vì nó gây suy giảm chất lượng nhận dạng.

## Bước tiếp theo
Áp dụng chiến lược tiền xử lý `p03_vad_pad_200ms` lên toàn bộ tập huấn luyện (Train set) trước khi tiến hành Fine-Tuning.
