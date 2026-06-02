# Synthetic Vietnamese Outpatient Dataset v0.1

## Purpose

Dataset giả lập phục vụ MVP Local-first Clinical Ambient Documentation Assistant cho bối cảnh khám ngoại trú tiếng Việt.

Dataset này dùng để kiểm thử pipeline:

audio/script
→ transcript segment
→ speaker role
→ clinical fact extraction
→ source attribution
→ SOAP-lite draft
→ simulated doctor review
→ Gold/Evaluation seed.

## Data policy

- Không chứa dữ liệu bệnh nhân thật.
- Không dùng tên, số điện thoại, địa chỉ thật.
- Tất cả thông tin cá nhân nếu có đều là PII giả lập.
- Dataset được phép dùng cho internal development, demo, training baseline và evaluation nội bộ.
- Mọi clinical fact phải link về `source_segment_ids`.
- Mọi SOAP statement phải có evidence từ transcript/facts.
- Output chỉ là draft, không phải chẩn đoán hay chỉ định điều trị thật.

## Version

v0.1

## Cases

| Case ID | Specialty | Main scenario | Key labels |
|---|---|---|---|
| SYN_OUT_001 | Internal Medicine | Ho, sốt nhẹ, không đau ngực | symptom, negation, medication, allergy |
| SYN_OUT_002 | Gastroenterology | Đau bụng, tiêu chảy | symptom, negation, duration, plan |
| SYN_OUT_003 | Neurology/Internal Medicine | Đau đầu, mất ngủ | symptom, negation, red flag |