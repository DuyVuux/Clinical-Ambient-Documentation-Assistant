## Mục tiêu file
Hướng dẫn intern/dev/AI coding assistant cần đọc phần nào từ research evaluation metrics trước khi build hoặc đánh giá MVP.

## Tài liệu nguồn
Clinical ASR_NLP Evaluation Metrics and International Benchmarks for Ambient Clinical Documentation Assistants.md

## Nguyên tắc chính
Không đánh giá MVP bằng WER hoặc ROUGE đơn thuần.

Trong clinical documentation, một lỗi chính tả thường có thể không nguy hiểm, nhưng các lỗi sau có thể gây hại:
- sai thuốc;
- sai liều;
- sai dị ứng;
- đảo nghĩa phủ định;
- bỏ sót red flag;
- tự bịa diagnosis;
- đưa lời caregiver/nurse thành plan của bác sĩ;
- gán nhầm speaker.

## Các phần bắt buộc đọc kỹ

### 1. Executive Summary
Cần hiểu:
- Generic WER không đủ.
- ROUGE không đủ.
- Đánh giá phải tập trung vào clinical safety.
- MVP phải có Linked Evidence và audit trail.
- Doctor review burden là metric quan trọng.

### 2. Evaluation Metric Framework
Cần dùng 5 cấp độ đánh giá:
1. ASR-Level
2. NLP Extraction-Level
3. Note-Generation-Level
4. Doctor-Review-Level
5. Clinical-Safety-Level

### 3. ASR Clinical Metrics
Cần đọc kỹ:
- Medical Word Error Rate, viết tắt là mWER.
- Diarization Error Rate, viết tắt là DER.
- Lỗi thuật ngữ y khoa.
- Lỗi speaker attribution.

Lưu ý:
Không dùng "CER" một cách mơ hồ.
Trong ASR, CER có thể là Character Error Rate.
Trong DeepScore, CER có thể là Captured Entity Rate.
Trong project này nên gọi rõ:
- CharER = Character Error Rate
- CapturedEntityRate = Captured Entity Rate

### 4. NLP and SOAP Metrics
Cần rút thành metric MVP:
- Captured Entity Rate
- Accurate Entity Rate
- Unsupported Fact Count
- SOAP Section Classification Accuracy
- Hallucination Rate
- Omission Rate
- Critical Clinical Error Rate

### 5. DeepScore
Không cần implement full DeepScore production.
Nhưng nên dùng phiên bản rút gọn:
- MDFR: Major Defect-Free Rate
- CDFR: Critical Defect-Free Rate
- Captured Entity Rate
- Accurate Entity Rate
- MNR: Minimally-Edited Note Rate
- MWHR: Medical Word Hit Rate

### 6. Failure Modes
Cần chuyển thành error taxonomy:
- hallucination;
- wrong medication;
- wrong dosage;
- negation error;
- omission;
- over-certainty;
- speaker confusion;
- temporal confusion;
- SOAP section misclassification;
- over-summarization.

### 7. Doctor Review Workflow
Cần lấy các metric:
- edit distance;
- time to review;
- safety flags resolved;
- note usable after light edits;
- doctor trust score;
- error feedback count.

### 8. Maturity Model
MVP không nên dừng ở Level 3: Draft SOAP Generation.
MVP nên hướng tới Level 4: Draft SOAP + safety checkpoints + doctor review + linked evidence + audit trail.

## Phần chỉ cần đọc lướt
- International vendor comparison: dùng làm benchmark tham khảo, không copy.
- 6-week pilot plan: dành cho pilot thật, không áp dụng nguyên xi cho intern MVP.
- 500–800 real visits: không áp dụng cho intern MVP.
- Production thresholds: chỉ dùng để biết hướng phát triển dài hạn.