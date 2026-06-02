## Mục tiêu file
Thiết kế quyền truy cập và audit log tối thiểu cho MVP.

## Roles
MVP có thể dùng role đơn giản:
- developer
- doctor_reviewer
- mentor
- admin_demo

## Role Permissions

### developer
Được:
- chạy pipeline;
- xem synthetic/actor transcript;
- debug ASR/NLP;
- xem audit log kỹ thuật.

Không được:
- xử lý real patient data nếu chưa được duyệt;
- export dữ liệu thật;
- gửi dữ liệu thật lên cloud.

### doctor_reviewer
Được:
- xem transcript;
- xem clinical facts;
- xem SOAP draft;
- edit/reject/confirm draft;
- đánh dấu lỗi clinical.

### mentor
Được:
- xem kết quả demo;
- xem báo cáo metric;
- review risk register;
- không cần xem raw audio nếu không cần thiết.

### admin_demo
Được:
- tạo/xóa session;
- cấu hình demo;
- export synthetic results.

## Minimum Audit Events
- session_created
- audio_uploaded
- audio_recorded
- transcript_generated
- speaker_labels_generated
- clinical_facts_extracted
- safety_flags_generated
- soap_draft_generated
- doctor_opened_review
- doctor_edited_note
- doctor_rejected_note
- doctor_confirmed_note
- audio_deleted
- session_deleted

## Audit Log Schema
{
  "event_id": "uuid",
  "timestamp": "ISO-8601",
  "session_id": "string",
  "actor_role": "developer | doctor_reviewer | mentor | admin_demo",
  "action": "string",
  "object_type": "session | audio | transcript | facts | soap_draft | safety_flags | note",
  "object_id": "string",
  "status": "success | failed",
  "details": "minimal non-PHI details only"
}

## Audit Rule
Không ghi full transcript, full SOAP note, tên bệnh nhân, số điện thoại, địa chỉ hoặc mã bệnh nhân vào audit log.
