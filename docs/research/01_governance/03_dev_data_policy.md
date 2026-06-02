## Mục tiêu file
Quy định loại dữ liệu được phép dùng khi intern build MVP.

## Allowed Data
Được dùng:
- Audio giả lập do intern/team tự đọc.
- Transcript giả lập.
- Actor data không chứa định danh thật.
- Case lâm sàng tổng hợp, không copy từ hồ sơ bệnh nhân thật.
- Tên giả, tuổi giả, triệu chứng giả, thuốc giả hoặc thuốc phổ biến dùng cho mục đích test.

## Restricted Data
Không được dùng mặc định:
- Audio bệnh nhân thật.
- Transcript cuộc khám thật.
- Ảnh chụp hồ sơ bệnh án.
- Đơn thuốc thật.
- Mã bệnh nhân thật.
- Số điện thoại, địa chỉ, CCCD, bảo hiểm, ngày sinh thật.
- Dữ liệu export từ HIS/EHR thật.

## Real Patient Data Rule
Real patient data chỉ được dùng nếu có đầy đủ:
- phê duyệt mentor/clinical lead;
- phê duyệt legal/security/data governance nếu cần;
- consent hợp lệ;
- mục đích sử dụng rõ ràng;
- quyền truy cập được giới hạn;
- audit log;
- retention policy;
- không dùng để train mặc định.

## Synthetic Case Rule
Mỗi case demo nên có:
- case_id;
- specialty;
- transcript ground truth;
- expected clinical facts;
- expected safety flags;
- expected SOAP draft;
- expected evaluation notes.

## Example Safe Demo Case
Case ID: GI_A01
Specialty: Tiêu hóa
Scenario: Bệnh nhân đau thượng vị 3 ngày, không sốt, không nôn máu, chưa ghi nhận dị ứng thuốc.
No real patient identity.
No real medical record.
