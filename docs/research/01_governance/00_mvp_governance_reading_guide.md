## Mục tiêu file
File này hướng dẫn intern/dev/AI coding assistant cần đọc phần nào từ research governance trước khi build MVP.

## Các phần bắt buộc phải đọc kỹ

### 1. Định hướng MVP
Cần hiểu rõ dự án không phải AI Doctor, không chẩn đoán tự động, không kê đơn tự động.
MVP là Local-first Clinical Ambient Documentation Assistant cho outpatient workflow.

Output cuối không phải transcript.
Output cuối là medical record draft/SOAP note được bác sĩ review và xác nhận.

### 2. North Star Architecture
Cần đọc để hiểu pipeline:
Audio Recording → Audio Preprocessing → ASR → Speaker Labeling → Clinical Post-processing → Clinical Fact Extraction → Canonical Clinical Schema → SOAP Renderer → Doctor Review → Confirmed Draft.

Nguyên tắc quan trọng:
Mọi clinical fact phải có source attribution gồm speaker, timestamp, confidence và trạng thái cần xác nhận.

### 3. Success Metrics
Không chỉ đo WER.
Phải đo thêm:
- Medical Term Error Rate
- Negation Error
- Critical Entity Error
- Latency sau khi bấm Stop
- AI note usable after light edits
- Time saved per visit

### 4. Data Governance
Cần đọc kỹ phần:
- Raw audio là dữ liệu rất nhạy cảm.
- Development dùng synthetic/actor data.
- Real patient data chỉ dùng evaluation nếu được duyệt.
- Cloud không phải default với dữ liệu bệnh nhân thật.
- Raw audio chỉ lưu ngắn hạn.
- Confirmed note mới là hồ sơ chính thức.

### 5. Day 2 — Data Governance, PII/PHI & Safety Framework
Cần chuyển thành các file MVP:
- data inventory
- PII/PHI policy
- consent model
- retention policy
- risk register
- audit log design

### 6. Day 5 — Speaker Labeling & Clinical Fact Attribution
Cần đọc để tránh sai logic:
Không được bỏ Patient speaker.
Patient là nguồn chính cho Subjective.
Doctor là nguồn chính cho Assessment/Plan.
Caregiver được đưa vào Subjective nhưng phải ghi source = caregiver.
Unknown speaker phải requires_review.

### 7. Day 6 — SOAP Draft Generation & Doctor Review Loop
Cần đọc để build guardrails:
AI không được bịa diagnosis, medication, dosage, allergy, test results, vital signs.
Nếu thiếu thông tin, ghi "not mentioned" hoặc "requires doctor confirmation".
Mọi nội dung quan trọng phải trace được về transcript.

### 8. Checklist cuối research
Cần dùng làm acceptance criteria trước khi demo:
- Không phải AI Doctor.
- MVP là outpatient.
- Transcript là intermediate evidence.
- Doctor confirmation bắt buộc.
- Synthetic/actor data là default.
- Không cloud với real data nếu chưa được duyệt.
- Missing allergy/medication phải flag.
- Negation như "không đau ngực" phải kiểm tra kỹ.