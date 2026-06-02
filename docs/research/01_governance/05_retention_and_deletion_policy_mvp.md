## Mục tiêu file
Quy định lưu/xóa dữ liệu trong MVP.

## Default MVP Retention
Với synthetic/actor data:
- Raw audio: giữ trong local demo folder cho đến khi xóa session.
- Transcript: giữ theo session.
- Clinical facts: giữ theo session.
- SOAP draft: giữ theo session.
- Audit log: giữ theo session.
- Có nút Delete Session để xóa toàn bộ dữ liệu session.

## Safer Option
Nếu muốn nghiêm ngặt hơn:
- Raw audio tự động xóa sau khi transcript thành công.
- Chỉ giữ transcript, facts, SOAP draft, safety flags cho demo.

## Real Patient Data Retention
Không áp dụng cho intern MVP nếu chưa được duyệt.
Nếu được duyệt riêng:
- raw audio lưu ngắn hạn;
- transcript và draft chỉ dùng cho review/evaluation được phê duyệt;
- không dùng để train mặc định;
- phải có audit log và deletion process.

## Required Delete Function
MVP nên có chức năng:
- Delete audio only
- Delete transcript/facts/note
- Delete entire session

## Deletion Log
Khi xóa dữ liệu, ghi audit event:
- event_type: audio_deleted hoặc session_deleted
- timestamp
- actor_role
- session_id
- deletion_scope

Không cần log nội dung audio/transcript đã xóa.