# 00. Hướng dẫn Đọc Tài liệu Nghiên cứu ASR (ASR Research Reading Guide)

## Giới thiệu chung
Thư mục này chứa toàn bộ các phân tích, khung đánh giá và khuyến nghị chiến lược được trích xuất từ **Báo cáo Nghiên cứu Chuyên sâu: Đánh giá và Lựa chọn Mô hình Nhận dạng Tiếng nói Tiếng Việt cho Hệ thống Tài liệu Lâm sàng Tự động**. 

Mục tiêu của bộ tài liệu này là cung cấp nền tảng kiến thức, tiêu chuẩn quốc tế và quy trình nghiêm ngặt để đội ngũ kỹ thuật và y tế xây dựng hệ thống Nhận dạng Tiếng nói Tự động (ASR) an toàn, chính xác trong môi trường lâm sàng thực tế tại Việt Nam.

## Cấu trúc Thư mục

Để nắm bắt toàn diện, đội ngũ nên đọc các tài liệu theo trình tự sau:

1. **`01_asr_context_for_ai_build.md`**: Tóm tắt thực thi và bằng chứng về ASR trong môi trường y tế/lâm sàng. Cung cấp bối cảnh cốt lõi cho việc phát triển AI.
2. **`02_candidate_asr_model_matrix.md`**: Đánh giá cảnh quan các mô hình ứng viên (Whisper, PhoWhisper, VietASR, wav2vec2, MMS) và phân tích điểm mạnh, điểm yếu cốt lõi.
3. **`03_vietnamese_asr_benchmark_summary.md`**: Tổng quan về hệ sinh thái các bộ dữ liệu benchmark tiếng Việt hiện tại và những lỗ hổng khi áp dụng vào môi trường Ambient.
4. **`04_clinical_asr_error_taxonomy.md`**: Phân loại chi tiết các mẫu lỗi ASR đặc thù và nguy hiểm trong y khoa tiếng Việt (tên thuốc, liều lượng, chuyển mã, v.v.).
5. **`05_asr_metric_framework_mvp.md`**: Khung đo lường tiêu chuẩn vượt ra ngoài WER truyền thống, tập trung vào Tỷ lệ Lỗi Thực thể Trọng yếu (CEER) và an toàn lâm sàng.
6. **`06_local_asr_benchmark_protocol.md`**: Quy trình Thao tác Chuẩn (SOP) để xây dựng tập dữ liệu vàng và đánh giá benchmark nội bộ.
7. **`07_model_decision_matrix.md`**: Ma trận chấm điểm có trọng số giúp đội ngũ lãnh đạo (CTO, AI Lead, PM) ra quyết định lựa chọn mô hình.
8. **`08_asr_pipeline_recommendation_mvp.md`**: Khuyến nghị cuối cùng về kiến trúc và quy trình tinh chỉnh mô hình ASR cho dự án.
9. **`09_asr_safety_acceptance_checklist.md`**: Danh sách kiểm tra nghiệm thu an toàn lâm sàng, đảm bảo tuân thủ "Human-in-the-Loop".
10. **`10_context_for_ai_build_asr_module.md`**: Tổng hợp các khoảng trống nghiên cứu và rủi ro hệ thống cần phòng tránh (ảo giác y khoa, phân phối dữ liệu chênh lệch).

## Nguyên tắc Cốt lõi
- **Bảo mật và Riêng tư**: Mọi dữ liệu y tế (PHI) phải được xử lý tuân thủ quy định bảo mật, ưu tiên triển khai cục bộ (on-premise).
- **An toàn là Số 1**: Tỷ lệ Lỗi Từ (WER) không phản ánh độ an toàn. Quyết định triển khai phụ thuộc hoàn toàn vào Tỷ lệ Lỗi Thực thể Trọng yếu (CEER).
- **Con người trong vòng lặp (Human-in-the-Loop)**: ASR là công cụ hỗ trợ, không thay thế quyết định lâm sàng. Luôn cần bước thẩm định từ chuyên gia y tế.
