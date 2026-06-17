# Hướng Dẫn Chạy Đánh Giá Model ASR (Mentor Benchmark)

Đây là tài liệu hướng dẫn nhanh dành cho quản lý (Mentor/Manager) để đánh giá mô hình ASR (Automatic Speech Recognition) độc lập, không làm ảnh hưởng đến mã nguồn dự án đang phát triển.

## 1. Cấu trúc dữ liệu yêu cầu
Để script chạy được, bạn cần chuẩn bị một bộ dữ liệu (`testset`) có cấu trúc như sau:

```text
testset/
├── transcript.txt
└── audio/
    ├── file1.wav
    ├── file2.wav
    └── ...
```

**Lưu ý:**
- `transcript.txt`: Chứa văn bản gỡ băng tương ứng. Định dạng chuẩn là `tên_file.wav <khoảng_trống/tab> văn_bản`.
- `audio/`: Thư mục con chứa toàn bộ các file `.wav`.

*Ví dụ:* Đặt toàn bộ bộ dữ liệu này vào đường dẫn: `data/raw/testset/`

## 2. Cách chạy công cụ Benchmark

Mở Terminal (Command Line) tại thư mục gốc của dự án `Clinical Ambient Documentation Assistant`.

**Cài đặt thư viện (Chỉ làm 1 lần nếu môi trường chưa có):**
```bash
pip install torch transformers soundfile tqdm pandas
```

**Lệnh chạy đánh giá:**
Sử dụng script Python đã được thiết kế sẵn. Bạn có thể sử dụng trực tiếp Model ID từ Hugging Face của dự án để chạy (hệ thống sẽ tự động tải trực tuyến về bộ nhớ đệm, sếp **không cần tự tải gì về thư mục gốc**).

Model ID chuẩn của tuần 5: `DukeShy/phowhisper-medium-medical-vi-run01`

```bash
# Chạy trực tuyến bằng Model ID của Hugging Face (Không cần tải file về máy)
python mentor_evaluation/run_benchmark.py \
  --testset-dir data/raw/testset \
  --model-path DukeShy/phowhisper-medium-medical-vi-run01
```

*(Lưu ý: Nếu sếp muốn dùng file offline, sếp cũng có thể điền đường dẫn đến thư mục chứa checkpoint đã tải về máy vào tham số `--model-path`)*

**Các tham số nâng cao (Tùy chọn):**
- `--run-label <tên_phiên>`: Tên phiên chạy (VD: `run_test_week5`). Kết quả sẽ lưu vào thư mục này.
- `--smoke-test`: Thêm cờ này vào cuối lệnh nếu bạn chỉ muốn chạy thử nhanh với 3 file âm thanh đầu tiên để kiểm tra lỗi.
- `--no-resume`: Buộc script phải chạy lại toàn bộ từ đầu, thay vì tiếp tục từ những file đã chạy xong.

*Ví dụ lệnh chạy đầy đủ sử dụng model online:*
```bash
python mentor_evaluation/run_benchmark.py \
  --testset-dir data/raw/testset \
  --model-path DukeShy/phowhisper-medium-medical-vi-run01 \
  --run-label mentor_test_1
```

## 3. Xem kết quả (Outputs)

Toàn bộ kết quả sẽ được tạo tự động và lưu vào thư mục `mentor_evaluation_outputs/<tên_phiên>/`.

Bạn nên mở các file sau để kiểm tra:

1. **`reports/BENCHMARK_REPORT.md`**: File Báo cáo trực quan (Markdown). Bao gồm:
   - **WER (Word Error Rate)**: Tỉ lệ lỗi từ (Càng thấp càng tốt).
   - **CER (Character Error Rate)**: Tỉ lệ lỗi ký tự.
   - **Negation Miss Rate**: Tỉ lệ model nghe trượt (bỏ sót) các từ khóa phủ định quan trọng ("không", "chưa", "chẳng").
2. **`reports/benchmark_per_sample_errors.jsonl`**: Lưu chi tiết lỗi của **từng file âm thanh một** để bạn dễ dàng debug xem model bị sai đoạn nào.
3. **`predictions/prediction.tsv`**: File chứa kết quả văn bản mà model nghe được (dạng bảng dễ mở bằng Excel/Google Sheets).

Đồng thời, script sẽ đóng gói tất cả các file kết quả này vào một tệp nén `.tar.gz` (`mentor_evaluation_outputs/<tên_phiên>_artifacts.tar.gz`) để bạn tiện lợi gửi email hoặc chia sẻ.
