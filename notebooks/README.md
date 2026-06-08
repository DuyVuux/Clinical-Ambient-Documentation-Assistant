# Notebooks

Thư mục này chứa toàn bộ các Jupyter Notebooks dùng cho mục đích phân tích, huấn luyện (training), chạy thử nghiệm (evaluation) và demo dự án. Việc tổ chức theo chuẩn quốc tế (như Cookiecutter Data Science) giúp tách biệt môi trường thử nghiệm khỏi mã nguồn chính (`scripts/`) và dễ dàng theo dõi quá trình phát triển.

## 📂 Cấu trúc thư mục (Skeleton)

- **`01_eda/`**: Khám phá và phân tích dữ liệu (Exploratory Data Analysis). Các notebook dùng để phân tích phân phối độ dài audio, kiểm tra transcript, visualize waveform, v.v.
- **`02_preprocessing/`**: Thử nghiệm các logic tiền xử lý dữ liệu trước khi đưa vào hàm chạy chính (ví dụ: VAD padding, noise reduction, chuẩn hóa text).
- **`03_training/`**: Nơi đặt các notebook dùng để fine-tune hoặc train các mô hình ASR (ví dụ: huấn luyện Whisper bằng LoRA).
- **`04_evaluation/`**: Chạy inference thử (chạy thử model) và tính toán các metrics (WER, CER) độc lập để kiểm chứng kết quả trước khi đưa vào pipeline tự động.
- **`05_demo/`**: Các notebook hoàn chỉnh, sạch sẽ và có comment đầy đủ dùng để demo kết quả, pipeline hoặc show case mô hình hoạt động end-to-end.

## 📝 Quy chuẩn đặt tên (Naming Convention)

Để dễ dàng tra cứu và đảm bảo thứ tự logic, tất cả các file notebook phải tuân thủ chuẩn đặt tên sau:

```text
<số_thứ_tự>-<chủ_đề_hoặc_mục_đích>.ipynb
```

**Ví dụ:**
- `01-audio-length-distribution.ipynb` (trong thư mục `01_eda`)
- `01-test-vad-padding-logic.ipynb` (trong thư mục `02_preprocessing`)
- `01-finetune-whisper-small-lora.ipynb` (trong thư mục `03_training`)
- `01-run-inference-chunkformer.ipynb` (trong thư mục `04_evaluation`)

## ⚠️ Lưu ý quan trọng
- **Không đưa code định tuyến (hardcode path) cá nhân vào notebook.** Cố gắng dùng đường dẫn tương đối hoặc đọc biến môi trường để code có thể chạy được trên các máy khác nhau.
- **Giữ cho notebook sạch sẽ:** Xóa bớt các cell output quá dài hoặc các cell in ra log lỗi rác trước khi commit lên git.
- Không để thông tin cá nhân (tên tác giả, v.v) vào trong notebook theo chuẩn bảo mật dự án.
