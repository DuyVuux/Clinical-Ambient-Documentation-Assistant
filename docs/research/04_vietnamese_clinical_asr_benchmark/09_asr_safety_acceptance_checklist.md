# 09. Checklist Nghiệm thu An toàn Lâm sàng ASR (ASR Safety Acceptance Checklist)

Danh sách kiểm tra này đóng vai trò như cổng chặn (gatekeeper) trước khi hệ thống ASR được phép triển khai vào quy trình khám chữa bệnh thực tế.

## 1. Kiểm tra Kiến trúc Phòng ngừa Ảo giác (Hallucination Prevention)
- [ ] Tích hợp bộ lọc Phát hiện Hoạt động Giọng nói (VAD - Voice Activity Detection) trước khi giải mã.
- [ ] Hệ thống loại bỏ thành công các khoảng lặng dài và âm thanh không phải giọng nói, tránh lặp từ vô tận.

## 2. Kiểm tra Kết quả Benchmark An toàn Nội bộ
- [ ] Tỷ lệ Lỗi Thực thể Trọng yếu (CEER) < 5% (Tên thuốc, Liều lượng, Đường dùng).
- [ ] Tỷ lệ Lỗi Phủ định (NCER) < 2% (Không bỏ sót hoặc chèn sai từ "không", "chưa").
- [ ] Tỷ lệ Ảo giác Y khoa (Medical Hallucination Rate) < 1% (Mô hình tuyệt đối không "sáng tác" thêm thuốc không có trong file ghi âm).
- [ ] Tỷ lệ Lỗi Từ Tổng quát (WER) < 25% (Trong môi trường Ambient có nhiễu).

## 3. Kiểm tra Độ bền bỉ với Môi trường và Đặc tính Lâm sàng
- [ ] Vượt qua bài kiểm tra Chuyển mã (Code-Switching): Nhận diện chính xác thuật ngữ tiếng Anh y khoa (VD: "chụp MRI", "test PCR", "chỉ số HbA1c") khi chèn vào câu tiếng Việt.
- [ ] Vượt qua bài kiểm tra Tạp âm (Ambient Noise): Hoạt động ổn định trong môi trường tiếng quạt, còi xe, tiếng gõ bàn phím.
- [ ] Xử lý tốt các từ đồng âm/gần âm lâm sàng nguy hiểm (LASA Errors).

## 4. Kiểm tra Cơ chế "Con người trong vòng lặp" (Human-in-the-Loop)
- [ ] UI tự động trích xuất và bôi đậm (highlight) bằng màu cảnh báo các Thực thể Trọng yếu (Tên thuốc, Số lượng, Từ phủ định).
- [ ] Hệ thống YÊU CẦU bác sĩ/y tá liếc qua và xác nhận tính chính xác của các điểm nghẽn này trước khi lưu hồ sơ vào EMR/HIS.

## 5. Quy định Vận hành Bắt buộc
- [ ] **CHẶN:** KHÔNG ĐƯỢC sử dụng mô hình ASR công cộng gốc (out-of-the-box) mà không trải qua tinh chỉnh trên dữ liệu lâm sàng y khoa nội bộ.
- [ ] Hệ thống chạy cục bộ (on-premise) hoặc tuân thủ nghiêm ngặt bảo mật thông tin y tế bệnh nhân (PHI).
