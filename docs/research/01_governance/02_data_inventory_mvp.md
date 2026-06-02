## Mục tiêu file
Liệt kê các loại dữ liệu mà MVP xử lý, mức nhạy cảm, nơi lưu, thời gian lưu và quyền truy cập.

| Data object | Mô tả | Mức nhạy cảm | Nơi lưu MVP | Retention MVP | Ai được xem | Dùng để train không? |
|---|---|---|---|---|---|---|
| Session metadata | session_id, visit_type, specialty, demo_case_id, consent_status | Thấp nếu synthetic | Local DB | Đến khi xóa session | Intern/dev/mentor | Không |
| Raw audio | File ghi âm cuộc khám | Rất nhạy cảm nếu thật | Local folder | Demo: tạm thời. Real: không dùng nếu chưa duyệt | Dev/doctor reviewer nếu được phép | Không |
| Transcript | Văn bản ASR từ audio | Nhạy cảm | Local DB/file | Theo session demo | Dev/doctor reviewer | Không mặc định |
| Speaker segments | Đoạn thoại theo speaker/timestamp | Nhạy cảm | Local DB/file | Theo session demo | Dev/doctor reviewer | Không mặc định |
| Clinical facts | Triệu chứng, thuốc, dị ứng, xét nghiệm, plan | Nhạy cảm | Local DB/JSON | Theo session demo | Dev/doctor reviewer | Không mặc định |
| SOAP draft | Bản nháp ghi chú ngoại trú | Nhạy cảm | Local DB/file | Đến khi confirm/reject/xóa | Doctor reviewer/dev demo | Không |
| Safety flags | Cảnh báo thiếu/sai/không chắc | Nhạy cảm mức vừa-cao | Local DB/JSON | Theo session demo | Doctor reviewer/dev | Không |
| Doctor edits | Nội dung bác sĩ sửa | Nhạy cảm | Local DB/file | Theo session demo | Doctor reviewer/dev | Không |
| Confirmed draft | Bản nháp đã được bác sĩ xác nhận trong demo | Hồ sơ y tế nếu là dữ liệu thật | Local DB/file trong demo | Theo session demo | Doctor reviewer | Không |
| Audit log | Log hành động hệ thống | Có thể nhạy cảm | Local DB/log file | Theo session demo | Dev/mentor | Không |

## Nguyên tắc MVP
- Synthetic/actor data là mặc định.
- Không dùng real patient data trong development.
- Không đưa dữ liệu thật lên cloud.
- Không dùng raw audio/transcript thật để train/fine-tune.
- Dữ liệu demo phải xóa được.