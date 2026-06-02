## Mục tiêu file
Hướng dẫn intern/dev/AI coding assistant cần đọc phần nào từ research AI safety/risk framework trước khi build MVP.

## Tài liệu nguồn
Khung an toàn AI cho tài liệu Y tế.md

## Phần bắt buộc đọc kỹ

### 1. Executive Summary
Cần hiểu rằng MVP không được thiết kế như một wrapper đơn giản gồm ASR + LLM.
MVP phải được định vị là Safe, Risk-Controlled Clinical Documentation Pipeline.

Hệ thống phải có:
- embedded safety checkpoints;
- human-in-the-loop;
- doctor confirmation;
- audit log;
- source traceability;
- clinical safety flags.

### 2. Core Thesis
Cần đọc kỹ để tránh lỗi thiết kế nguy hiểm:
- Không coi việc biến hội thoại khám bệnh thành bệnh án là tác vụ tóm tắt văn bản thông thường.
- Không để LLM tự suy diễn phần thiếu.
- Không tạo bản ghi y tế trôi chảy nhưng không có nguồn.
- Không cho AI ghi trực tiếp vào EHR/HIS.

Ba nguyên tắc chính:
- Epistemic Humility: AI phải biết nói "không biết / không được đề cập".
- Cognitive Friction: bác sĩ phải review chủ động, không được one-click approve quá dễ.
- Data Provenance & Traceability: mọi clinical fact phải truy ngược được về transcript/audio source.

### 3. WHO Product Requirements
Cần chuyển thành yêu cầu sản phẩm MVP:
- REQ-01: AI output luôn bắt đầu là AI-generated draft.
- REQ-02: Không tự động chèn ICD-10, diagnosis, treatment plan nếu bác sĩ không nói rõ.
- REQ-03: Có acoustic/audio quality gate.
- REQ-04: Có traceability UI.
- REQ-05: Có audit/version log.
- REQ-06: Test nhiều giọng vùng miền nếu có thể.
- REQ-07: Có nút bác sĩ flag lỗi trong UI.

### 4. NIST AI RMF Mapping
Dùng khung 4 bước:
- Govern: ai chịu trách nhiệm safety.
- Map: rủi ro có thể xảy ra ở đâu.
- Measure: đo lỗi bằng CREOLA, edit distance, critical safety errors.
- Manage: giảm rủi ro bằng prompt grounding, UI review, safety flags.

### 5. HITL and Doctor Confirmation
Cần đọc để thiết kế doctor review loop:
- AI draft không bao giờ là final.
- Bác sĩ phải xác nhận từng vùng rủi ro cao: thuốc, dị ứng, chẩn đoán/assessment, plan.
- UI phải hiển thị uncertainty và source.
- Không thiết kế "approve all" quá dễ.

### 6. Comprehensive Risk Register
Dùng làm mẫu tạo hazard log MVP.
Không cần bê nguyên bảng production.
Chỉ cần 8–12 rủi ro chính cho intern MVP.

### 7. CREOLA / Evaluation Framework
Dùng để chấm lỗi:
- hallucination;
- fabrication;
- negation error;
- assumed causality;
- context conflation;
- omission;
- medication/dosage error;
- allergy error;
- plan/order from non-doctor.

### 8. MVP Safety Requirements
Đây là phần quan trọng nhất cho build:
- Draft-only.
- Mandatory human sign-off.
- Traceability link.
- Immutable/append-only audit trail.
- Low input quality warning.
- Discrepancy flagging.
- Local PHI/PII scrubbing nếu có.
- Không autonomous prescribing.
- Không autonomous diagnosis.
- Không direct EHR write.

---

# Những phần chỉ cần đọc lướt

## Clinical Safety Case / CSCR full
Đọc để hiểu tinh thần, nhưng không cần làm full CSCR cho intern MVP.
Chỉ cần tạo bản rút gọn: Safety Case Lite.

## ALARP formal
Đọc để hiểu "risk must be reduced as much as reasonably practicable".
Không cần tuyên bố ALARP chính thức trong demo intern.

## Evidence Package production
Đọc để biết sau này pilot cần gì.
Intern MVP chỉ cần evidence pack rút gọn.

## 100–200 Golden Dataset
Đây là mục tiêu pilot/production.
Intern MVP chỉ cần 3–10 synthetic demo cases, tốt hơn là 10–20 nếu đủ thời gian.