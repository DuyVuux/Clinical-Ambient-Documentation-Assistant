# 00_schema_reading_guide_for_intern_mvp.md

## Mục tiêu file
Hướng dẫn intern/dev/AI coding assistant cần đọc phần nào trong file research "Future-Proof Canonical Clinical Schema Design.md" để build MVP đúng scope.

## Kết luận rút gọn cho intern MVP
Không implement full FHIR server.
Không lưu raw FHIR resources làm database chính.
Không tích hợp HIS/EHR trong MVP.
Không cần SMART on FHIR.
Không cần strict FHIR validation.
Không cần terminology server ở giai đoạn đầu.

MVP cần dùng hướng:
"FHIR-Informed Internal Model + Facade Pattern"

Nghĩa là:
- Dùng schema nội bộ đơn giản, dễ build.
- Nhưng field design phải lấy cảm hứng từ FHIR.
- Dùng các primitive quan trọng như:
  - Identifier
  - Reference
  - CodeableConcept
  - Quantity
  - Period
  - AuditMetadata
- Lưu narrative note có cấu trúc, không lưu một cục free-text duy nhất.
- Mọi clinical fact/note phải gắn Patient + Encounter + nguồn transcript + audit.

## Phần cần đọc kỹ trong file research

### 1. Executive Summary
Cần đọc để hiểu quyết định kiến trúc chính:
- MVP không nên dùng native FHIR server.
- MVP không nên lưu raw FHIR resources làm DB chính.
- MVP cần Canonical Clinical Schema đơn giản nhưng future-proof.
- Tránh bẫy "free-text only note".

Ý chính cần nhớ:
"Build internal canonical schema now, map to FHIR later."

### 2. Architectural Foundations and Security Considerations
Cần đọc để hiểu tại sao mọi entity phải có audit/provenance:
- createdAt
- updatedAt
- createdBy
- updatedBy
- versionId

Với intern MVP, không cần build _history tables phức tạp.
Nhưng tối thiểu mỗi record phải có audit metadata.

### 3. Patient, Practitioner, Encounter Dynamics
Cần đọc kỹ.
Đây là phần cực quan trọng cho schema MVP.

Quy tắc:
- Patient là subject của hồ sơ.
- Practitioner/Clinician là người tạo/duyệt/chỉnh sửa.
- Encounter là lần khám cụ thể.
- Không được gắn clinical findings trực tiếp vào Patient mà bỏ Encounter.

Trong MVP, mọi note/fact nên có:
- patientId
- encounterId
- createdBy hoặc reviewedBy

### 4. Condition versus Observation
Cần đọc để tránh nhầm triệu chứng với chẩn đoán.

Quy tắc MVP:
- Patient nói "đau thượng vị 3 ngày" → Observation hoặc ClinicalFact type = symptom.
- Doctor nói "nghi viêm dạ dày" → Condition/DiagnosisMention, requires_doctor_confirmation = true.
- Không tự biến symptom thành diagnosis.

### 5. DiagnosticReport versus Observation
Cần đọc ở mức hiểu khái niệm.
Với intern MVP:
- Lab đơn lẻ như HbA1c 7.2% → Observation.
- Một nhóm xét nghiệm/panel → DiagnosticReport, optional.
- Nếu chưa làm lab panel phức tạp thì defer DiagnosticReport.

### 6. MedicationRequest versus MedicationStatement
Cần đọc rất kỹ vì liên quan an toàn.

Quy tắc MVP:
- Patient nói "tôi đang uống paracetamol" → Medication with assertionType = "history".
- Doctor nói "uống paracetamol 500mg..." → Medication with assertionType = "order".
- Nếu speaker không phải Doctor thì không được coi là order.
- Medication/dosage luôn cần doctor confirmation.

### 7. Composition versus DocumentReference
Cần đọc để thiết kế note.

Quy tắc MVP:
- SOAP note do app tạo nên lưu như ClinicalNote có sections.
- Không chỉ lưu một string dài.
- Audio file hoặc external file upload thì coi như Attachment/DocumentReference metadata.
- ClinicalNote sau này có thể map sang FHIR Composition.

### 8. Terminology and Code-System Considerations
Cần đọc nhưng không overbuild.

Với MVP:
- Dùng CodeableConcept.text là bắt buộc.
- coding có thể để trống.
- Sau này mới map SNOMED CT, LOINC, ICD-10, RxNorm/ATC.
- Nếu dùng local code thì dùng system dạng custom URI.

Ví dụ MVP:
{
  "code": {
    "text": "Đau thượng vị",
    "coding": []
  }
}

### 9. Canonical Clinical Schema Proposal
Đây là phần dùng trực tiếp để build schema.

Entity nên implement trong MVP:
- Patient
- Practitioner/Clinician
- Encounter
- TranscriptSegment
- ClinicalFact
- ClinicalNote
- Medication
- Allergy
- SafetyFlag
- AuditEvent

Entity nên để optional hoặc phase sau:
- DiagnosticReport
- Attachment
- Full FHIR Bundle export
- FHIR bidirectional mapping

### 10. MVP Implementation Recommendation: Staged Roadmap
Chỉ làm Stage 1 cho intern MVP:
- Canonical schema without HIS integration.
- Local DB hoặc SQLite/PostgreSQL.
- JSON fields cho CodeableConcept/Identifier/Reference.
- Free-text input vẫn được, nhưng phải lưu trong CodeableConcept.text.

Không làm Stage 2/3/4 trong intern MVP:
- Terminology server mapping.
- FHIR Bundle export.
- SMART on FHIR.
- Bidirectional HIS/EHR integration.

### 11. Anti-Patterns and Architectural Risks
Cần đọc để tránh lỗi thiết kế.

Không được:
- Lưu clinical note như một free-text blob duy nhất.
- Gắn symptom/lab/medication trực tiếp vào Patient mà không có Encounter.
- Trộn thuốc bác sĩ kê và thuốc bệnh nhân tự khai.
- Mất thông tin ai tạo, ai sửa, sửa lúc nào.
- Ghi lab panel thành một text khổng lồ.
- Overwrite external patient identifier bằng internal UUID.
