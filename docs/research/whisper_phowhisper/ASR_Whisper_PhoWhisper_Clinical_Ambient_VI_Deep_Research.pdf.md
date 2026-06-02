# Whisper và PhoWhisper cho trợ lý ghi chép lâm sàng ngoại trú tiếng Việt theo kiến trúc local-first

## Tóm tắt điều hành

Bộ tài liệu dự án đã xác định rất rõ một hướng đi đúng về mặt an toàn và kỹ thuật: hệ thống phải là **local-first**, chạy **batch-after-stop** thay vì streaming mặc định, đặt **evidence-first** làm nguyên tắc cốt lõi, và bắt buộc **human-in-the-loop/doctor review** ở các bước quyết định. Quyết định này phù hợp một cách tự nhiên với Whisper-family, vì chính model card của Whisper lưu ý rằng Whisper không phải là giải pháp real-time “out of the box”, đồng thời OpenAI cũng cảnh báo không nên dùng các model này trong các bối cảnh ra quyết định rủi ro cao. Với bài toán của dự án là **hỗ trợ tài liệu hóa sau khám**, không chẩn đoán, không kê đơn, không tự ghi HIS/EHR, kiến trúc “ASR trước, fact sau, note cuối cùng chỉ từ accepted/edited facts” là an toàn hơn nhiều so với pipeline đen “audio → SOAP” một bước. fileciteturn0file1 fileciteturn0file2 fileciteturn0file3 fileciteturn0file5 citeturn19view0turn19view1

Kết luận kỹ thuật quan trọng nhất là: **faster-whisper không phải là model mới**, mà là **runtime/inference engine** cho Whisper qua CTranslate2; còn **Whisper large-v3**, **Whisper large-v3-turbo**, **PhoWhisper-medium**, **PhoWhisper-large** là các **checkpoint** khác nhau. Vì vậy, khuyến nghị tốt nhất cho MVP là tách bạch hai quyết định: **chọn runtime** và **chọn checkpoint**. Về runtime, mặc định thực dụng nhất cho local-first hiện nay là **faster-whisper**, vì đây là reimplementation dùng CTranslate2, có benchmark công khai về tốc độ/bộ nhớ và còn hỗ trợ convert cả các Whisper-compatible fine-tuned models; nghĩa là về nguyên tắc có thể chạy cả checkpoint PhoWhisper sau khi convert. Về checkpoint, baseline nên gồm ít nhất hai nhánh: **Whisper large-v3 hoặc large-v3-turbo** cho baseline production tổng quát, và **PhoWhisper-medium/large** cho baseline chuyên biệt tiếng Việt. citeturn17view0turn21view4turn18view1turn16view3turn5view0turn3view6

Với bài toán **Vietnamese outpatient ambient clinical ASR**, đánh giá hiện có cho thấy **Whisper** mạnh ở độ phủ ngôn ngữ rộng, tính robust tổng quát, hệ sinh thái triển khai lớn, và nhiều công cụ downstream như faster-whisper, WhisperX, stable-ts, whisper-timestamped. Tuy nhiên, Whisper cũng có các failure mode rất đáng ngại trong y tế: hallucination, lặp lại, sai lệch theo ngôn ngữ/giọng, và thậm chí paper gốc còn ghi nhận khuynh hướng đoán sai tên người nói một cách “plausible but almost always incorrect”. Với hồ sơ khám ngoại trú, lỗi kiểu này có thể chuyển thành sai tên bệnh nhân, sai tên bác sĩ, hoặc gán nhầm phát ngôn. citeturn14view0turn19view0turn19view1

**PhoWhisper** đáng chú ý vì đây là một nỗ lực chuyên biệt hóa Whisper cho tiếng Việt: paper chính thức mô tả PhoWhisper được fine-tune từ các multilingual Whisper checkpoints trên **844 giờ** dữ liệu ASR tiếng Việt, gồm Common Voice tiếng Việt, VIVOS, VLSP 2020 và một phần private data; phần private data này được mô tả là trải rộng **26.000 người** qua **63 tỉnh/thành** và training còn có augmentation tiếng ồn trên một nửa tập train. Do đó, về mặt kỳ vọng trước benchmark, PhoWhisper có lý do hợp lý để tốt hơn Whisper tổng quát ở các hiện tượng thuần tiếng Việt như accent Bắc/Trung/Nam, tính tự nhiên của chính tả có dấu, và các mẫu hội thoại tiếng Việt đời thường. Nhưng hiện chưa có bằng chứng công khai nào trong paper/model card cho thấy PhoWhisper đã được đánh giá trên **outpatient ambient clinical dialogues**, với các lỗi nguy hiểm như phủ định “không/chưa”, thuốc-liều-đường dùng-tần suất, lab/vital, người nhà chen lời, hay code-switching Anh–Việt mang tính lâm sàng. Vì thế PhoWhisper là **mandatory benchmark**, chưa phải “auto-winner” cho môi trường lâm sàng ngoại trú. citeturn6view0turn6view1turn6view2turn27view0turn27view1turn3view3turn3view6

**Recommendation MVP** nên được chốt như sau. Về production baseline, dùng **faster-whisper + Whisper large-v3** nếu ưu tiên chất lượng tổng quát và có đủ tài nguyên; dùng **faster-whisper + Whisper large-v3-turbo** nếu ưu tiên latency/VRAM và chỉ cần transcription, không cần translation. Turbo là phiên bản pruned/finetuned của large-v3 với decoder giảm từ 32 xuống 4 layer, nhanh hơn rõ rệt nhưng có một mức suy giảm chất lượng nhỏ; vì bài toán dự án là transcription tiếng Việt sau khi bác sĩ bấm stop, turbo là baseline latency rất hợp lý nhưng không được coi là mặc định “đủ an toàn” nếu chưa qua benchmark lâm sàng. Song song, bắt buộc benchmark **PhoWhisper-medium** và **PhoWhisper-large** trên cùng pipeline. Nếu sau benchmark, PhoWhisper-large thắng ở các metric clinical-safety quan trọng mà chi phí vận hành còn chấp nhận được, nó có thể trở thành baseline tiếng Việt chính. citeturn12view1turn16view3turn17view2turn17view3turn21view4turn27view1

Khuyến nghị quan trọng nhất về fine-tuning là: **chưa nên fine-tune** nếu dự án vẫn thiếu **gold transcript/evaluation set đã freeze**, thiếu **dataset registry audit**, thiếu **annotation guideline** ổn định, hoặc thiếu **legal/consent clearance** cho real-patient audio. Điều này không chỉ là vấn đề governance; về mặt học thuật, Whisper paper cho biết họ chủ động lọc transcript machine-generated vì dữ liệu kiểu đó có thể làm hỏng chất lượng mô hình. Trong dự án này, nếu dùng `raw_asr` hoặc transcript “sửa sơ” làm gold mà không tách sạch khỏi dữ liệu human-reviewed, rất dễ tạo ra vòng lặp tự củng cố lỗi của chính ASR. Vì thế, **Stage 0 benchmark** và **Stage 1 decoding/post-processing adaptation** phải hoàn thành trước; **Stage 2 PEFT** chỉ bắt đầu khi có gold tốt; **Stage 3** cho real-patient data chỉ mở khi đã đủ approval. fileciteturn0file1 fileciteturn0file2 fileciteturn0file4 fileciteturn0file5 fileciteturn0file6 citeturn14view0

Bảng dưới đây tóm tắt các rủi ro lớn nhất của MVP ASR lâm sàng và cách giảm thiểu.

| Rủi ro | Tại sao nguy hiểm | Giảm thiểu nên áp dụng ngay |
|---|---|---|
| Sai phủ định `không/chưa/không còn/chưa từng` | Đảo nghĩa lâm sàng hoàn toàn | Red-team set phủ định; metric Negation Error Rate; boundary overlap ở VAD; doctor review bắt buộc |
| Sai thuốc/liều/đường dùng/tần suất | Dẫn đến note sai điều trị | Tách Medication Error Rate riêng; không auto-correct nếu không chắc; chỉ sinh note từ accepted facts |
| Sai số đo/lab/vital | Thay đổi đánh giá mức độ nặng | Numeric/unit metric; fallback segment-level evidence nếu word alignment yếu |
| Sai speaker role | Gán nhầm bác sĩ ↔ bệnh nhân ↔ người nhà | pyannote chỉ cho speaker IDs; role mapping phải manual; khóa role trước fact extraction |
| Hallucination/lặp text | Tạo fact không được nói | VAD, decoding guardrails, unsupported-fact validator, condition settings benchmarked |
| Sai tên người nói hoặc tên riêng | Lộ/sai PHI, sai attribution | Không tin speaker names tự động; kiểm tra evidence quote/timestamp/speaker |
| Code-switching Anh–Việt | Sai tên thuốc quốc tế, xét nghiệm, viết tắt | Tạo evaluation subset mixed-language; code-switching error metric; dictionary surface-form review |
| Leakage train/eval | Làm metric ảo, chọn sai model | Split theo encounter_id; freeze holdout; transcript fingerprint dedup |
| License/governance mismatch | Chặn pilot dù kỹ thuật tốt | License matrix cho model/runtime/alignment/diarization; review artifact-level |
| Quá sớm fine-tune trên data thật | Overfit + legal risk + khó rollback | Chỉ benchmark trước; synthetic/volunteer first; real-patient fine-tune cần consent/governance rõ ràng |

Nguồn cho các rủi ro kỹ thuật và pháp lý: project plan/schemas nội bộ, Whisper paper/model cards, PhoWhisper paper/model cards, WhisperX repo, faster-whisper repo, pyannote repo, stable-ts repo, whisper-timestamped repo. fileciteturn0file1 fileciteturn0file3 fileciteturn0file4 fileciteturn0file5 fileciteturn0file6 citeturn14view0turn19view0turn19view1turn21view4turn27view1turn19view4turn9view6turn11view0turn11view1

## Whisper dưới góc nhìn học thuật, toán học và kỹ thuật

### Bài toán xác suất và biểu diễn tín hiệu

Về mặt toán học, bài toán ASR của Whisper có thể được phát biểu như sau. Gọi \(x(t)\) là waveform liên tục, hoặc sau lấy mẫu là dãy rời rạc \(x[n]\). Từ tín hiệu này, ta xây dựng đặc trưng âm học \(X \in \mathbb{R}^{T \times F}\) dưới dạng log-Mel spectrogram; đầu ra là chuỗi token \(y=(y_1,\dots,y_N)\). Mục tiêu của mô hình là cực đại hóa xác suất có điều kiện \(p(y\mid X)\), tương đương tối thiểu hóa negative log-likelihood của chuỗi token đích. Whisper paper mô tả rõ đây là một **encoder-decoder Transformer sequence-to-sequence** được huấn luyện để dự đoán token sequence cho nhiều speech tasks dưới cùng một giao diện token. citeturn14view0turn15academia1

Đặc trưng âm học có thể viết theo các bước tuyến tính cổ điển. Với cửa sổ \(w[n]\), hop \(H\), và FFT size \(N\), STFT có thể biểu diễn là
\[
S_{m,k}=\sum_{n=0}^{N-1} x[n+mH]\,w[n]\,e^{-j2\pi kn/N}.
\]
Năng lượng phổ là \(P_{m,k}=|S_{m,k}|^2\). Nếu \(H_{\text{mel}}\in\mathbb{R}^{K\times F}\) là ma trận Mel filterbank, khi đó
\[
M = P H_{\text{mel}},\qquad
X=\log(\max(M,\varepsilon)).
\]
Whisper gốc resample audio về **16 kHz**, dùng **25 ms window**, **10 ms stride**, và tạo **80-channel log-magnitude Mel spectrogram**; riêng checkpoint **large-v3** giữ cùng large-class architecture nhưng đổi frontend sang **128 Mel bins** và thêm token ngôn ngữ cho Cantonese. citeturn14view0turn18view0

Điểm đáng lưu ý cho tiếng Việt là: tone không phải phụ kiện ngữ điệu tùy ý mà là thông tin từ vựng quan trọng; nghiên cứu gần đây về spoken language models còn cho thấy lexical tone được mã hóa đáng kể trong biểu diễn speech, có cả case studies với tiếng Việt. Suy ra về mặt kỹ thuật, các quyết định tiền xử lý như VAD cắt quá sát, denoising quá mạnh, hoặc augmentation làm méo đặc tính cao độ/suprasegmental có thể bào mòn thông tin phân biệt nghĩa. Trong môi trường clinical ambient, điều này liên quan trực tiếp tới các cặp cực kỳ nguy hiểm về mặt semantically-near nhưng clinically-far khi dấu/âm/tone bị lệch. Đây là một suy luận kỹ thuật từ đặc trưng tonal của tiếng Việt và cơ chế biểu diễn của speech models, không phải benchmark lâm sàng trực tiếp. citeturn26academia1turn14view0

Một hệ quả kỹ thuật rất thực dụng là chunking. Vì Whisper paper cho biết dữ liệu huấn luyện được cắt theo **30-second segments**, còn OpenAI repo ghi rõ `transcribe()` xử lý file bằng cửa sổ trượt **30 giây**, nên trong triển khai cho audio khám ngoại trú, chunk ASR không nên vượt xa nhịp 30 giây native của Whisper. Nếu dùng STFT hop 10 ms thì 30 giây tương ứng xấp xỉ \(3000\) frames; sau stem convolution có stride 2 ở lớp conv thứ hai, số bước thời gian đi vào encoder còn khoảng \(1500\), tức là mô hình đã được thiết kế quanh thang thời gian đó. Đây là một suy ra trực tiếp từ cấu hình frontend/stem của paper và repo. citeturn14view0turn12view1

### Encoder decoder Transformer và attention

Whisper dùng một encoder-decoder Transformer “off-the-shelf” theo tinh thần của Transformer gốc. Phần encoder nhận \(X\), đi qua một stem gồm **hai convolution layers** với kernel width 3, GELU activation, trong đó convolution thứ hai có **stride 2**; sau đó thêm **sinusoidal position embeddings** rồi đi vào các encoder blocks. Phần decoder dùng **learned position embeddings** và **tied input-output embeddings**. Paper cũng ghi rõ encoder và decoder có cùng width và số block trong mỗi model size. citeturn14view0

Ở mức đại số tuyến tính, nếu \(H\in\mathbb{R}^{T\times d}\) là biểu diễn ẩn của một layer, một head attention tiêu chuẩn tạo ra ba phép chiếu tuyến tính
\[
Q = HW_Q,\qquad K = HW_K,\qquad V = HW_V,
\]
với \(W_Q,W_K,W_V \in \mathbb{R}^{d\times d_k}\). Scaled dot-product attention là
\[
\operatorname{Attn}(Q,K,V)=\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.
\]
Nếu có \(h\) heads, multi-head attention là
\[
\operatorname{MHA}(H)=\operatorname{Concat}(\text{head}_1,\dots,\text{head}_h)W_O.
\]
Decoder tự hồi quy factor hóa xác suất theo
\[
p(y\mid X)=\prod_{i=1}^{N} p(y_i\mid y_{<i},X).
\]
Đây là cấu trúc chuẩn của Transformer encoder-decoder và là nền toán học trực tiếp cho Whisper. citeturn15academia1turn14view0

Trong ngữ cảnh ASR, cần phân biệt ba loại attention. **Encoder self-attention** gom thông tin dài hạn giữa các frames âm học; **decoder self-attention** mô hình hóa phụ thuộc ký hiệu-ngôn ngữ trong chuỗi token; còn **cross-attention** cho decoder “đọc” các biểu diễn âm học của encoder khi phát sinh token mới. Với tài liệu hóa lâm sàng ngoại trú, cross-attention là nơi các ambiguity dạng “thở nhanh” so với “thở ngắt”, hoặc “đau bụng” so với “đau ngực”, được giải theo ngữ cảnh âm học thực tế; nhưng decoder side cũng có thể gây ra lỗi “fluently wrong” vì đây vẫn là một sequence generator chứ không phải bộ aligner ràng buộc cứng. citeturn15academia1turn14view0turn19view0

### Tokenization, mục tiêu huấn luyện và suy diễn

Whisper paper cho biết mô hình dùng **byte-level BPE** kiểu GPT-2 cho English-only models, còn với multilingual models thì **refit vocabulary** cùng kích thước để tránh fragmentation quá mức trên các ngôn ngữ khác ngoài tiếng Anh. Đồng thời, Whisper không nhắm tới một pipeline ASR cổ điển nhiều tầng mà huấn luyện decoder phát sinh một chuỗi token đa nhiệm, trong đó có token bắt đầu transcript, token ngôn ngữ, token task (`transcribe`/`translate`), token chỉ có/không có timestamps, token `nospeech`, và cả timestamp tokens lượng tử hóa theo bước **20 ms**. citeturn14view0

Với tiếng Việt, tác động của tokenizer cần được nhìn theo hai lớp. Lớp thứ nhất là **linguistic surface fidelity**: dấu, diacritics, tên thuốc quốc tế, viết tắt xét nghiệm, và code-switching Anh–Việt có thể bị tách thành nhiều subword/byte pieces, làm tăng độ nhạy với lỗi bề mặt. Lớp thứ hai là **clinical semantics**: một lỗi nhỏ ở dấu hay ký hiệu đôi khi ít quan trọng với hiểu-nghĩa chung, nhưng trong y khoa lại có thể đổi entity hoặc đổi nghĩa của token số/đơn vị. Tác động chính xác của tokenizer Whisper lên các chuỗi clinical Vietnamese chưa có benchmark chính thức trong tài liệu đã tìm thấy; đây là suy luận hợp lý từ cơ chế multilingual byte-level BPE của Whisper và thuộc tính bề mặt của văn bản y khoa tiếng Việt, nên **needs verification** trên tập gold của dự án. citeturn14view0

Về objective, Whisper paper mô tả mô hình được train để dự đoán các token transcript/timestamp/task, và chỉ mask loss trên phần context trước đó chứ vẫn dự đoán các token còn lại; đây tương thích với huấn luyện autoregressive cross-entropy chuẩn dưới teacher forcing ở encoder-decoder seq2seq. Một điểm rất đáng chú ý là OpenAI nhấn mạnh họ cố ý train Whisper để dự đoán **raw text of transcripts without significant standardization**, thay vì đẩy mạnh normalization trong chính ASR model. Với dự án này, điều đó là một gợi ý rất hữu ích: **ASR nên giữ vai trò tạo transcript gần bằng lời nói**, còn normalization lâm sàng, dictionary standardization và fact extraction nên để ở các tầng downstream có provenance tốt hơn. Nếu ép model ASR trực tiếp tạo “normalized clinical text”, dự án sẽ làm mờ ranh giới giữa ASR và IE, và làm khó yêu cầu “mọi fact phải có quote/timestamp”. citeturn14view0turn0file1turn0file3

Ở pha suy diễn, repo OpenAI liệt kê turbo như default CLI model, còn faster-whisper repo nhắc một chi tiết rất quan trọng cho benchmark công bằng: `openai/whisper` mặc định transcribe với **beam size 1**, trong khi faster-whisper dùng default **beam size 5**. Nếu không khóa cùng decoding config, so sánh tốc độ/độ chính xác giữa các implementation sẽ sai lệch. Model cards cũng lưu ý Whisper dễ bị repetitive text; beam search và temperature scheduling có thể giảm phần nào nhưng không loại bỏ được. citeturn12view1turn21view4turn19view0turn19view1

### Điểm mạnh và điểm yếu của Whisper trong khám ngoại trú tiếng Việt

Điểm mạnh lớn nhất của Whisper cho dự án là **robust generalization**. Paper gốc cho thấy Whisper generalize tốt zero-shot từ weak supervision quy mô lớn; model card large-v3 tiếp tục tuyên bố checkpoint này cải thiện robustness với accents, background noise và technical language, đồng thời large-v3 được train trên tổng cộng hơn 5 triệu giờ dữ liệu weakly/pseudo-labeled ở card của checkpoint. Với một dự án local-first chịu nhiều biến thiên microphone/phòng khám/giọng nói, đây là lợi thế đáng kể. citeturn13view5turn18view3

Nhưng điểm yếu của Whisper cũng đúng vào nơi y tế cần nghiêm ngặt nhất. OpenAI cảnh báo model có thể hallucinate văn bản không thật sự được nói; performance không đều giữa các ngôn ngữ, accent và dialect; và sequence-to-sequence architecture dễ lặp lại. Paper còn mô tả một failure mode đặc biệt: mô hình có xu hướng đoán tên speaker một cách nghe-có-vẻ-hợp-lý nhưng gần như luôn sai. Trong một hệ thống clinical ambient documentation tiếng Việt, điều này dẫn tới ba yêu cầu thiết kế cứng: không tự tin vào speaker names, không dùng raw ASR để sinh fact không có evidence, và không dùng chính Whisper để làm classification cho doctor/patient/caregiver roles. citeturn14view0turn19view0turn19view1

Một điểm cuối cùng rất thực tiễn là sự phù hợp với kiến trúc batch-after-stop. Vì Whisper không real-time “out of the box”, project decision chuyển sang xử lý local sau khi bác sĩ bấm stop thực ra không phải nhượng bộ, mà là thiết kế ăn khớp với bản chất của model: sau khi có full audio, hệ thống có thể thêm VAD, alignment, diarization, provenance và validator mà không phải đánh đổi quá nhiều cho latency streaming. Với ambient clinical documentation, đây là lựa chọn đúng hơn việc cố ép một stack seq2seq lớn vào luồng gần real-time rồi phải xử lý transcript chưa ổn định. fileciteturn0file1 citeturn19view0turn19view1

## PhoWhisper và so sánh thực chiến với các checkpoint Whisper

### PhoWhisper là gì và khác Whisper ở đâu

PhoWhisper là một họ checkpoint cho ASR tiếng Việt do VinAI công bố, paper chính thức nêu rõ có **5 phiên bản**: PhoWhisper-tiny, base, small, medium và large, dùng **cùng architecture** với các multilingual Whisper models tương ứng; riêng bản large tương ứng với **Whisper large-v2**, không phải large-v3. Đây là điểm cực kỳ quan trọng: khi so PhoWhisper-large với Whisper large-v3, thực chất đang so một checkpoint được **language-specialize hóa** trên nền large-v2 với một checkpoint **OpenAI thế hệ mới hơn** có frontend 128-Mel và training recipe mới hơn. citeturn6view0turn5view0turn18view1

Paper PhoWhisper mô tả tập train khoảng **844 giờ**, gồm Common Voice tiếng Việt, VIVOS, VLSP 2020 Task 1, và private data; phần private data được mô tả là cung cấp accent diversity từ **26.000 người** trải trên **63 tỉnh/thành**. Để tăng robustness với nhiễu tự nhiên, authors chia train thành hai nửa, augment một nửa bằng environmental sounds qua `audiomentations`, rồi hợp lại thành tập train cuối. Họ fine-tune từ các multilingual Whisper checkpoints tương ứng bằng `transformers`, dùng **8 A100 40GB**, batch toàn cục 64, và **48.000 updating steps**, xấp xỉ **5 epochs**. citeturn6view1turn6view2turn27view0turn27view1

Từ các dữ kiện này, có thể rút ra một kết luận khá chắc chắn: PhoWhisper không đổi lớp toán học nền của Whisper, nhưng đổi **miền dữ liệu** và **phân bố ngôn ngữ**, nên nơi nó có thể tốt hơn không nằm ở kiến trúc mới, mà ở **specialization cho tiếng Việt**. Đây là lý do hợp lý để kỳ vọng PhoWhisper mạnh hơn trong accent Bắc/Trung/Nam, từ vựng tiếng Việt thường dùng, và orthography có dấu. Đồng thời, chính vì evidence hiện có tập trung vào ASR Vietnamese nói chung chứ không phải outpatient clinical ambient speech, khoảng cách domain vẫn còn rất lớn. citeturn6view0turn6view1turn27view0

### Điểm mạnh của PhoWhisper và giới hạn còn lại cho môi trường lâm sàng

Trên các benchmark công khai tiếng Việt trong paper, PhoWhisper-medium và PhoWhisper-large đều đạt kết quả mạnh hơn các baseline wav2vec2 được so trong paper đó; riêng PhoWhisper-large đạt WER thấp nhất trên CMV-Vi, VIVOS, VLSP Task 1 và VLSP Task 2 của bảng công bố. Đây là evidence tốt rằng checkpoint này thực sự có hiệu quả cho Vietnamese ASR nói chung. citeturn27view1

| Checkpoint | Số tham số theo paper | CMV-Vi WER | VIVOS WER | VLSP Task 1 WER | VLSP Task 2 WER |
|---|---:|---:|---:|---:|---:|
| PhoWhisper-medium | 769M | 8.27 | 4.97 | 14.12 | 26.85 |
| PhoWhisper-large | 1.55B | 8.14 | 4.67 | 13.75 | 26.68 |

Nguồn: bảng kết quả chính thức trong paper PhoWhisper; đây là benchmark ASR tiếng Việt công khai, **không phải** benchmark outpatient clinical ambient. citeturn27view1

Tuy nhiên, không nên ngoại suy quá mức từ bảng trên sang khám ngoại trú. Các failure modes quan trọng của phòng khám như tên thuốc quốc tế, tên generic-brand, liều/tần suất, lab abbreviations, số đo sinh hiệu, caregiver chen lời, overlap, và negation lâm sàng thường không được đại diện đầy đủ trong các benchmark công khai ASR tiếng Việt. Hơn nữa, ACI-Bench nhấn mạnh rằng clinic encounter dialogues rất khó chia sẻ vì bảo mật bệnh nhân, nên benchmark note generation/clinical ambient speech vốn đã thiếu dữ liệu công khai lớn và chuẩn. Vì vậy, dù PhoWhisper có bằng chứng tốt ở public Vietnamese ASR, **chưa đủ bằng chứng** để tuyên bố nó vượt Whisper large-v3/turbo trên outpatient clinical audio. citeturn27view1turn24academia1

Tokenizer của PhoWhisper cũng là một điểm cần nói rõ. Paper/model cards xác nhận PhoWhisper khởi tạo từ các multilingual Whisper checkpoints tương ứng và dùng cùng architecture, nhưng tài liệu công khai đã tìm thấy **không nói rõ** PhoWhisper có thay tokenizer hay chỉnh vocabulary hay không. Suy luận hợp lý nhất hiện nay là nó **thừa hưởng tokenizer Whisper-compatible** của checkpoint gốc hoặc một cấu hình tương thích với `transformers`/`openai-whisper`, nhưng điều này **needs verification** ở mức artifact/config trước khi đưa vào pipeline huấn luyện hay convert sang CTranslate2. citeturn6view0turn3view3turn3view6

### Phân biệt architecture runtime checkpoint alignment diarization và fine tuning

Một nhầm lẫn rất phổ biến trong các dự án ASR là trộn lẫn khái niệm model với runtime. Bảng dưới đây tách bạch các lớp thành phần cho dự án này.

| Lớp thành phần | Nó là gì | Ví dụ trong dự án | Nếu thay nó thì cái gì đổi |
|---|---|---|---|
| Model architecture | Lớp toán học nền | Whisper encoder-decoder Transformer | Đổi class mô hình và phép biến đổi học được |
| Checkpoint | Trọng số cụ thể trên cùng hoặc gần cùng architecture | `whisper-large-v3`, `whisper-large-v3-turbo`, `vinai/PhoWhisper-medium`, `vinai/PhoWhisper-large` | Đổi chất lượng/độ lệch miền/ngôn ngữ |
| Inference runtime | Engine chạy checkpoint | `openai/whisper`, `transformers`, `faster-whisper` | Đổi speed, memory, batching, deployment ergonomics |
| Alignment tool | Công cụ timestamp/alignment hậu xử lý hoặc bổ trợ | WhisperX, stable-ts, whisper-timestamped | Đổi chất lượng word timing, confidence, license |
| Diarization tool | Công cụ tách speaker identities | pyannote | Đổi speaker segmentation/DER, không tự sinh clinical roles |
| Fine-tuning method | Cách cập nhật trọng số | full FT, LoRA/adapters | Đổi cost, rollback risk, overfit risk |
| Evaluation dataset | Chuẩn đo dự án | synthetic/volunteer/public/real-patient holdout | Đổi độ tin cậy của kết luận |

Nguồn: Whisper paper/repo, PhoWhisper paper/model card/repo, faster-whisper repo, WhisperX repo, stable-ts repo, whisper-timestamped repo, pyannote repo. citeturn14view0turn12view1turn6view0turn3view6turn21view4turn19view4turn11view1turn11view0turn10view1

Từ bảng trên, khuyến nghị quan trọng là: **dùng faster-whisper như runtime mặc định**, nhưng đừng nhầm nó với checkpoint. faster-whisper repo ghi rõ có thể convert **bất kỳ Whisper models compatible with Transformers**, kể cả **user fine-tuned models**. Điều này mở ra khả năng rất phù hợp cho dự án: benchmark OpenAI checkpoints bằng faster-whisper trước; nếu sau này PhoWhisper hoặc một adapter nội bộ thắng, vẫn có thể đưa vào cùng interface runtime sau khi convert. citeturn21view4turn17view0

### So sánh checkpoint cho bài toán outpatient ambient clinical ASR

| Tùy chọn | Bản chất | Điểm mạnh chính | Điểm yếu chính | Khuyến nghị |
|---|---|---|---|---|
| Whisper large-v3 qua faster-whisper | OpenAI checkpoint large-class, runtime tối ưu CTranslate2 | Robust tổng quát, hệ sinh thái mạnh, large-v3 có frontend 128-Mel và recipe mới hơn | Không chuyên biệt tiếng Việt; hallucination/repetition vẫn là rủi ro; metadata license trên bề mặt release cần review | **Baseline chất lượng tổng quát nên có** |
| Whisper large-v3-turbo qua faster-whisper | Checkpoint pruned/finetuned từ large-v3, 4 decoder layers | Nhanh hơn rõ, ít tốn VRAM hơn, hợp batch-after-stop | Có suy giảm chất lượng nhỏ; không phù hợp translation; vẫn không chuyên biệt tiếng Việt | **Baseline latency bắt buộc nên có** |
| PhoWhisper-medium | Checkpoint Whisper-medium được specialize cho tiếng Việt | Nhẹ hơn bản large, có evidence tốt trên public Vietnamese ASR | Chưa có evidence outpatient clinical; tokenizer/config chi tiết cần verify | **Baseline tiếng Việt bắt buộc** |
| PhoWhisper-large | Checkpoint large-v2-class được specialize cho tiếng Việt | Khả năng tốt nhất cho tiếng Việt trong họ PhoWhisper công khai | Chậm hơn medium; vẫn chưa có outpatient clinical benchmark | **Benchmark rất nghiêm túc; có thể lên baseline chính nếu thắng holdout** |

Nguồn cho các cột về nguồn gốc checkpoint, số layer turbo, và tính khả dụng deployment: OpenAI repo/model cards, PhoWhisper paper/model cards, faster-whisper repo. Ước lượng feasibility phần cứng của PhoWhisper-medium/large là **suy luận theo cùng parameter class** với Whisper-medium/large-v2, nên cần verify bằng benchmark thực nghiệm trên máy đích. citeturn12view1turn16view3turn18view1turn18view3turn6view0turn3view6turn21view4

Về hardware và latency, OpenAI repo ước lượng class **medium** khoảng 5 GB VRAM, class **large** khoảng 10 GB VRAM, còn **turbo** khoảng 6 GB VRAM với tương đối tốc độ khoảng 8x so với large trong benchmark A100 của họ; faster-whisper repo còn công bố benchmark triển khai cho thấy tăng tốc rõ rệt và hỗ trợ int8 quantization trên CPU/GPU. Nhưng đây đều là benchmark của repo trên hardware cụ thể, nên chỉ nên dùng làm mốc planning, không dùng thay cho benchmark nội bộ trên audio khám ngoại trú. citeturn12view1turn17view1turn17view2

Ở góc độ license và legal risk, cần cực kỳ cẩn thận. OpenAI repo nói code và weights Whisper phát hành theo **MIT**, nhưng Hugging Face card của `openai/whisper-large-v3` hiện hiển thị **Apache-2.0**, trong khi card của `whisper-large-v3-turbo` hiển thị **MIT**. PhoWhisper model cards/repo hiển thị **BSD-3-Clause**. faster-whisper là **MIT**. WhisperX là **BSD-2-Clause**. stable-ts là **MIT** nhưng repo thông báo development đang pause vô thời hạn. whisper-timestamped là **AGPL-3.0** và repo tự mô tả là experimental. pyannote-audio repo là **MIT**, nhưng community-1 diarization pipeline yêu cầu chấp nhận **user conditions** trên Hugging Face và cấp token khi tải. Với pilot y tế, ma trận license phải khóa theo **artifact cụ thể** chứ không theo “tên model family” nói chung. citeturn12view1turn18view4turn16view4turn3view3turn4view0turn17view0turn19view4turn11view2turn11view0turn10view1turn9view6

## Mapping schema sang bài toán ML, dữ liệu và governance

Các schema được cung cấp là phần mạnh của dự án. Chúng đã mã hóa khá rõ ràng các gate về consent, license, governance, holdout, commercial pilot và doctor confirmation. Quan trọng hơn, chúng tạo một ranh giới lành mạnh giữa **transcript segment**, **clinical fact**, và **final note**, thay vì gộp mọi thứ vào một object “ASR output”. Tuy vậy, một số policy mà project mô tả ở mức nguyên tắc vẫn chưa được schema ép cứng hoàn toàn, nên cần validator rules bổ sung. fileciteturn0file1 fileciteturn0file3 fileciteturn0file4 fileciteturn0file5 fileciteturn0file6

### Encounter và dataset metadata

`encounter.schema` yêu cầu các trường cốt lõi như `encounter_id`, `source_type`, `setting`, `specialty`, `language`, `audio_path`, `transcript_path`, `contains_phi`, `consent_status`, `license_status`, `allowed_use`, `review_status`, `version`, `created_at`, `updated_at`, `governance_status`. Nó còn chứa nested metadata cho `audio` và `transcript`, cùng các gate cho retention/access/audit và pilot eligibility. `dataset_metadata.schema` lặp lại các gate governance ở cấp dataset, và thêm `target_zone`. fileciteturn0file5 fileciteturn0file6

| Cụm trường | Ý nghĩa ML/governance | Nên dùng vào quyết định gì |
|---|---|---|
| `source_type`, `setting`, `specialty`, `language` | Phân tầng dữ liệu theo nguồn và miền | Chọn subset outpatient; stratify split theo language=`vi/vi-VN/mixed`; tạo subset code-switching |
| `audio_path`, `transcript_path`, `audio.*`, `transcript.*` | Trỏ tới media và metadata kỹ thuật | Kiểm tra integrity, sample rate, format, checksum, engine/version |
| `contains_phi`, `consent_status`, `license_status`, `governance_status` | Cổng pháp lý/quản trị | Quyết định train/eval/demo/pilot có hợp lệ hay không |
| `allowed_use`, `is_holdout`, `commercial_pilot_status`, `target_zone` | Cổng sử dụng và release gating | Quyết định train/dev/test/benchmark/pilot |
| `retention_policy`, `access_control_policy`, `audit_log_required` | Kiểm soát lưu trữ và truy cập | Bắt buộc cho real_patient; nên dùng làm release blocker |

Về logic điều kiện, encounter và dataset metadata đều encode khá tốt: nếu `allowed_use` chứa `training`, thì `license_status` phải thuộc `internal/clear`, `consent_status` phải thuộc `synthetic/not_applicable/consented`, và `governance_status` phải thuộc `approved_internal/legal_approved`; nếu `allowed_use` chứa `holdout_only` thì không được đồng thời chứa `training` và `is_holdout` phải là `true`; nếu `source_type=real_patient` thì phải có `contains_phi` là `yes` hoặc `depends_on_source`, `consent_status=consented`, và có `retention_policy`, `access_control_policy`, `audit_log_required`. Đây là một nền tảng governance rất tốt để chặn misuse trước cả khi model chạy. fileciteturn0file5 fileciteturn0file6

Tuy nhiên vẫn còn vài khoảng trống cần vá. `target_zone` là một **array**, nên schema cho phép một dataset đồng thời nằm ở nhiều zone; điều này tiện cho metadata, nhưng với `evaluation` thì nguy hiểm vì dự án cần một holdout bất khả xâm phạm. Khuyến nghị là thêm validator nội bộ: nếu `evaluation` xuất hiện trong `target_zone`, thì bắt buộc `is_holdout=true` và `allowed_use` phải chứa `holdout_only`, không được chứa `training`. Ngoài ra, `encounter.provenance` hiện đã có `capture_device`, `recording_environment`, `collection_method`, `deidentification_status`, nhưng **không có accent label, noise rating, overlap density, speaker count thực tế, hoặc SNR**; đây là thiếu sót đáng kể nếu muốn stratified evaluation cho ASR lâm sàng tiếng Việt. fileciteturn0file5 fileciteturn0file6

### Transcript segment và đơn vị học có giám sát cho ASR

`transcript_segment.schema` là nơi bài toán ASR được mô hình hóa rõ nhất. Các trường cốt lõi gồm `segment_id`, `encounter_id`, `start_time`, `end_time`, `speaker_id`, `speaker_role`, `text`, `confidence`, `audio_span`, `asr_engine`, `asr_model_version`, `diarization_engine`, `role_label_source`, `segment_status`, `created_at`, `version`. Enum `segment_status` hiện là `raw_asr`, `corrected`, `reviewed`, `rejected`; `role_label_source` gồm `manual`, `model`, `rule_based`, `synthetic_gold`, `unknown`; và `speaker_role` hỗ trợ `doctor`, `patient`, `caregiver`, `nurse`, `interpreter`, `admin_staff`, `unknown`. fileciteturn0file4

Với schema này, supervised ASR sample nên được xây như sau. **Input** là span audio lấy từ `audio_span.start_time/end_time` hoặc từ segment timetable tương ứng. **Target** nên là `text`, nhưng chỉ khi `segment_status` thuộc `corrected`, `reviewed` hoặc `synthetic_gold` theo policy dự án; `raw_asr` phải bị loại khỏi tập gold vì chính Whisper paper đã cảnh báo rủi ro transcript machine-generated. **Metadata** đi kèm nên giữ `speaker_role`, `role_label_source`, `asr_engine`, `asr_model_version`, `diarization_engine`, encounter-level `source_type/setting/language`, để sau này stratify và audit self-training contamination. fileciteturn0file4 fileciteturn0file5 citeturn14view0

Một insight rất quan trọng là schema này cho phép dự án tránh “độc dược machine transcript”. OpenAI nói họ phải lọc mạnh transcript do máy sinh ra để tránh học “transcript-ese”; trong dự án này, các trường `segment_status`, `asr_engine`, `asr_model_version` chính là công cụ để phân biệt transcript do model tạo, transcript đã được sửa, và transcript đã reviewed. Nếu đội ngũ sau này trộn `raw_asr` vào supervised fine-tuning mà không kiểm soát, rủi ro self-reinforcement là rất cao. Do đó, **`raw_asr` chỉ nên ở Bronze**, `corrected/reviewed` mới đủ điều kiện vào Silver/Gold training candidates, và `rejected` thì chỉ đi vào Audit/Failure Analysis. fileciteturn0file4 fileciteturn0file2 citeturn14view0

Khoảng trống của transcript schema là chưa có **word-level timestamps**, chưa có **token-level confidence**, và chưa có **overlap flag**. Điều này không làm schema sai, nhưng có nghĩa là nếu dự án muốn click-back chính xác ở mức từ, hoặc đánh giá word alignment lâm sàng, sẽ cần một bảng phụ hoặc extension schema cho word spans/alignment objects. Đây là việc nên làm trước pilot nếu reviewer UX thực sự cần click vào từng số đo hoặc tên thuốc. fileciteturn0file4

### Clinical fact và đánh giá semantic safety

`clinical_fact.schema` là trọng tâm để biến transcript thành đánh giá an toàn lâm sàng downstream. Nó yêu cầu `fact_id`, `encounter_id`, `fact_type`, `original_text`, `normalized_text`, `assertion`, `speaker_role`, `clinical_subject`, `source_segment_ids`, `doctor_confirmation_status`, `confidence`, `created_at`, `created_by`, `version`. `fact_type` bao trùm nhiều loại thực thể/lập luận lâm sàng như `symptom`, `diagnosis`, `medication`, `allergy`, `procedure`, `vital_sign`, `lab_result`, `history`, `assessment`, `plan`, `instruction`, `follow_up`, `red_flag`, `administrative`, `other`. `assertion` cho phép mô hình hóa polarity và modality như `present`, `absent`, `possible`, `conditional`, `historical`, `planned`, `ordered`, `recommended`, `unknown`. `clinical_subject` tách rõ người nói và chủ thể lâm sàng. fileciteturn0file3

Schema này cho phép định nghĩa một bộ metric vượt ra ngoài WER/CER. `Medical Term Error Rate` có thể tính trên spans fact-type trọng yếu hoặc dictionary-matched medical terms. `Negation Error Rate` nên đo trên các facts có assertion polarity, đặc biệt với `present/absent/possible/conditional/historical`. `Critical Entity Error Rate` nên gom các fact types có risk cao như `medication`, `allergy`, `vital_sign`, `lab_result`, `diagnosis`, `plan`. `Source Attribution Accuracy` kiểm tra fact có đúng `source_segment_ids` và evidence span hay không. `Speaker Attribution Accuracy` kiểm tra đúng `speaker_role`; còn `Clinical Subject Accuracy` kiểm tra fact nói về patient hay family member/caregiver/fetus. Đây chính là lớp metric an toàn mà Whisper và PhoWhisper phải được chấm, thay vì chỉ dừng ở edit distance ký tự/từ. fileciteturn0file3

Cũng chính ở schema này lộ ra một khoảng trống quan trọng cần sửa trước pilot. Dự án đặt yêu cầu “mọi clinical fact phải có evidence: quote, timestamp, speaker/speaker_role và link về transcript segment”, nhưng schema hiện **không bắt buộc** `source_evidence` ở mức required; object `source_evidence` nếu có thì `segment_id` là bắt buộc, còn `quote/start_time/end_time/char offsets` lại chưa bắt buộc. Nói cách khác, policy an toàn của dự án đang **mạnh hơn** ràng buộc schema. Khuyến nghị là bổ sung validator nội bộ rất cứng: bất kỳ `clinical_fact` nào có `doctor_confirmation_status ∈ {accepted, edited}` hoặc `review_status=gold` đều phải có ít nhất một `source_evidence` với `segment_id`, `quote`, `start_time`, `end_time`, và khớp `speaker_role`. fileciteturn0file1 fileciteturn0file3

Một điểm rất tốt khác là schema đã bắt buộc `reviewed_by` và `reviewed_at` khi fact được `accepted/edited` hoặc khi `review_status=gold`. Điều này hỗ trợ audit trail cho doctor review và làm cho pipeline “fact trước, note sau” có thể trace được người phê duyệt. Encounter schema cũng có logic tương tự cho `clinical_note` khi `review_status=gold`: note phải có `doctor_confirmation_status` là `accepted` hoặc `edited`, cùng `reviewed_by/reviewed_at`. Đây là một safeguard phù hợp với các cảnh báo của OpenAI về không dùng Whisper cho quyết định rủi ro cao: model chỉ nên là upstream transcription engine, còn xác nhận lâm sàng phải thuộc về con người. fileciteturn0file3 fileciteturn0file5 citeturn19view0turn19view1

## Chiến lược dataset, benchmark và fine tuning

### Chiến lược dữ liệu theo zone và nguyên tắc không rò rỉ

Bộ schema và báo cáo nội bộ đã đủ để dựng một chiến lược dữ liệu chuẩn: **Bronze** cho raw/uncorrected audio và metadata; **Silver** cho transcript đã được sửa ở mức vận hành; **Gold** cho transcript/facts đã review nghiêm ngặt; **Evaluation** cho holdout cố định, không train; **Dictionary** cho thuật ngữ thuốc/bệnh/lab/vital/abbreviation; **Audit** cho correction events và review history; **Quarantine** cho data lỗi hoặc governance chưa ổn. Hướng này nhất quán với project plan và master report, và là cách tốt nhất để giữ cho local-first stack vừa audit được vừa không bị “overfit vào lòng tin chủ quan”. fileciteturn0file1 fileciteturn0file2 fileciteturn0file6

Train/dev/test phải split theo **`encounter_id`**, không split ngẫu nhiên theo segment, vì tất cả các segment trong cùng encounter chia sẻ speaker, acoustic setup, từ vựng, và clinical context. Whisper paper cũng nói họ làm transcript-level dedup để tránh contamination giữa training và evaluation; trên dữ liệu nội bộ, nên làm thêm fingerprint/dedup theo transcript normalized form hoặc acoustic hash ở mức encounter. Đồng thời phải stratify theo `specialty`, `setting`, `source_type`, `language`, và nếu có thể thì thêm accient/noise-derived tags từ metadata tương lai. fileciteturn0file2 fileciteturn0file5 citeturn14view0

Chiến lược **synthetic-first** là hoàn toàn hợp lý ở đây. Master report đã nhấn mạnh MVP không nên đặt mục tiêu train end-to-end từ đầu, mà nên dựng pipeline an toàn, tạo synthetic/volunteer dataset nhỏ có nhãn đầy đủ, bootstrap bằng public datasets, tạo riêng Evaluation Zone và buộc doctor review. Điều này cũng phù hợp với ACI-Bench: dữ liệu clinic dialogue-note chất lượng cao vốn hiếm do confidentiality, nên synthetic/actor data không chỉ là giải pháp “tạm”, mà thực tế là bước gần như bắt buộc để bootstrap và red-team. Trong bối cảnh dự án, mục tiêu tạo khoảng **20–50 synthetic/actor outpatient encounters** với đầy đủ doctor/patient/caregiver/nurse, accent Bắc/Trung/Nam, clinic noise, phủ định, thuốc-liều, lab/vital, transcript gold, speaker role, fact labels và SOAP-lite là hoàn toàn hợp lý như một engineering target ban đầu. Nhưng synthetic data **không đủ** để chứng minh readiness cho pilot thật. fileciteturn0file2 citeturn24academia1

### Lộ trình benchmark và fine tuning theo giai đoạn

Lộ trình phù hợp nhất cho dự án là bốn giai đoạn tuần tự. Bảng dưới đây tóm tắt logic điều hành.

| Giai đoạn | Cập nhật trọng số | Data tối thiểu cần có | Mục tiêu thực tế |
|---|---|---|---|
| Benchmark only | Không | Eval set frozen + config đồng nhất | Chọn baseline đúng |
| Decoding/domain adaptation nhẹ | Không | Benchmark logs + dictionary + review UI | Giảm lỗi an toàn mà chưa đụng weights |
| PEFT | Có, nhưng ít | Gold transcript đủ sạch + holdout + legal rõ | Hấp thụ từ vựng/âm vực chuyên biệt |
| Domain fine tuning sau pilot | Có | Real-patient approval + rollback + model card nội bộ | Chỉ mở khi governance cho phép |

Nguồn: chiến lược project nội bộ, schema governance, cảnh báo về machine-generated transcripts trong Whisper paper, và rationale của LoRA về giảm trainable parameters/rollback cost. fileciteturn0file1 fileciteturn0file2 fileciteturn0file5 fileciteturn0file6 citeturn14view0turn15academia0

**Stage benchmark** phải chạy ít nhất bốn tổ hợp checkpoint/runtimes sau trên cùng một audio, cùng preprocessing, cùng VAD, cùng segmentation: `Whisper large-v3`, `Whisper large-v3-turbo`, `PhoWhisper-medium`, `PhoWhisper-large`. Nếu dùng faster-whisper làm runtime thống nhất thì nên convert các checkpoint Whisper-compatible để giữ nhất quán runtime; nếu tạm thời benchmark PhoWhisper qua `transformers/openai-whisper`, cần khóa beam size và các decoding options cho công bằng. Đồng thời, phải benchmark text transcript và timestamp/alignment thành **hai bài toán tách biệt**, vì WhisperX repo nói rõ pipeline của họ thay một số transcription settings (`without_timestamps=True`, VAD-based segmentation, `condition_on_prev_text=False`) để phục vụ batching/alignment; do đó WER qua WhisperX không nên bị đem so trực diện với vanilla Whisper nếu không kiểm soát config. citeturn21view4turn21view0turn19view4

**Stage adaptation nhẹ** nên ưu tiên những thay đổi không động vào weights. Cụ thể: khóa một normalization policy cho transcript; viết controlled dictionary correction nhưng chỉ áp dụng trên **normalized copy**, không đụng raw quote; thêm validator cho những pattern nguy hiểm như phủ định, số đo, thuốc/liều; và nếu runtime/version thực sự hỗ trợ prompt-prefix hay hotword bias thì chỉ dùng như một biến benchmark, không bật mặc định khi chưa đo tác động. Trong bộ tài liệu ngoài đã tìm thấy, tính năng prompt/hotword cho chính các runtime này **chưa đủ bằng chứng thống nhất**, nên mọi feature kiểu đó nên gắn nhãn **needs verification** ở mức phiên bản runtime cụ thể. fileciteturn0file1 fileciteturn0file3

**Stage PEFT** chỉ hợp lý khi đã có gold transcript đủ sạch. Ở đây, LoRA là lựa chọn phù hợp hơn full fine-tune cho MVP vì lý do kinh điển: LoRA đóng băng base weights và chèn low-rank updates vào các linear layers, giảm mạnh số tham số trainable, tiết kiệm bộ nhớ và giúp rollback đơn giản hơn. Nhưng đội dự án không nên khóa cứng một pattern adapter placement duy nhất trước benchmark. Kế hoạch thực nghiệm bảo thủ nhất là so ba cấu hình: decoder-attention-only; encoder-top-half-attention-only; và hybrid encoder-top-half + decoder-cross-attention. Về mặt trực giác, nếu lỗi chủ yếu là **âm học/giọng/clinic noise**, adaptation phía encoder có thể có ích hơn; nếu lỗi chủ yếu là **từ vựng/orthography/medication names/code-switching**, adaptation phía decoder có thể hiệu quả hơn. Đây là khuyến nghị kỹ thuật suy luận từ cơ chế Whisper + LoRA, không phải một kết luận benchmark đã được xác lập cho bài toán này. citeturn15academia0turn14view0

Dữ liệu PEFT nên giữ cặp input-target ở mức **audio → transcript text**, không dùng `clinical_fact` làm target ASR trực tiếp. Nếu có hai bản transcript, nên lưu song song `text_raw_gold` và `text_norm_gold`; target train nên là bản **lightly normalized** với policy ổn định, còn raw quote giữ cho provenance/evidence. Cần batch theo duration thay vì số câu thuần túy; mask/padding theo chuẩn seq2seq; augmentation chỉ nên nhẹ như gain/noise/reverb/speed perturbation nhỏ. Tránh augmentation hoặc preprocessing làm sai F0/prosodic contour quá mức vì tiếng Việt mang nghĩa qua tonal information. PhoWhisper paper cho thấy noise augmentation có ích ở mức general Vietnamese ASR, nhưng điều đó không biện hộ cho augmentation mạnh trên clinical speech nơi thuốc/liều/số đo cực nhạy cảm. citeturn27view0turn26academia1

**Stage domain fine tuning sau pilot** chỉ mở với real-patient data khi đã thỏa đủ cả bốn điều kiện: có consent/governance rõ, có holdout freeze riêng, có internal model card nêu rõ artifact và nguồn dữ liệu, và có rollback plan. Các schema hiện đã chuẩn bị một phần cổng này qua `consent_status`, `governance_status`, `commercial_pilot_status`, `retention_policy`, `access_control_policy`, `audit_log_required`; nhưng vì `dataset_registry.csv` chưa được cung cấp và chưa có evidence về registry-level audit, readiness cho giai đoạn này vẫn chưa thể coi là đầy đủ. fileciteturn0file5 fileciteturn0file6

### Giao thức đánh giá quốc tế và reproducible

Giao thức đánh giá nên chia làm bốn lớp metric. Lớp đầu là **ASR surface metrics**:
\[
WER=\frac{S + D + I}{N},\qquad
CER=\frac{S_c + D_c + I_c}{N_c}.
\]
Ngoài ra nên có `Vietnamese Diacritic Error`, `Number/Unit Normalization Error`, và `Code-switching Error Rate`. Việc thêm metric riêng cho diacritics là đặc biệt quan trọng vì bề mặt chữ tiếng Việt mang nghĩa nhiều hơn so với nhiều ngôn ngữ non-tonal dùng Latin script. citeturn14view0turn26academia1

Lớp hai là **clinical safety metrics** được suy ra trực tiếp từ `clinical_fact.schema`. Một định nghĩa thực dụng là:
\[
NegER = \frac{\#\text{facts có assertion sai}}{\#\text{gold facts có assertion cần phân cực}},
\]
\[
CEER = \frac{\#\text{critical entities sai}}{\#\text{gold critical entities}},
\]
trong đó critical entities nên bao gồm tối thiểu `medication`, `allergy`, `vital_sign`, `lab_result`, `diagnosis`, `red_flag`, `plan`. Tương tự, `Medical Term Error Rate`, `Medication Error Rate`, `Dosage/Route/Frequency Error`, `Allergy Error Rate` và `Lab/Vital Numeric Error` nên được chấm riêng, không gộp vào WER/CER. Vì một transcript có WER khá thấp vẫn có thể cực kỳ nguy hiểm nếu sai một token phủ định hoặc một con số liều dùng. fileciteturn0file3

Lớp ba là **evidence/provenance metrics**. `Timestamp Usefulness` không nên chỉ là “có timestamps hay không”, mà nên là tỉ lệ fact được click-back tới audio đúng ngữ cảnh trong tolerance đã định trước. `Source Attribution Accuracy` đo fact có link đúng tới `source_segment_ids` và `source_evidence` hay không. `Quote Exactness` đo quote trong `source_evidence` có thật sự khớp transcript reviewed hay không. `Audio Click-back Success` đo reviewer có mở lại được đoạn audio tương ứng mà không bị lệch offset. Vì toàn bộ giá trị an toàn của hệ thống dự án nằm ở việc mọi fact có thể truy vết ngược về bằng chứng. fileciteturn0file1 fileciteturn0file3 fileciteturn0file4

Lớp bốn là **speaker/downstream metrics**. Với diarization, dùng `DER` ở mức kỹ thuật; nhưng metric vận hành cần hơn là `Speaker Attribution Accuracy`, `Role Mapping Accuracy`, `Overlap Handling`, `ClinicalFact Precision/Recall/F1`, `Unsupported Fact Rate`, `Hallucinated Plan Rate`, `Doctor Correction Burden`, `Review Time per Encounter`, và `Note Usability Score`. ACI-Bench cho thấy benchmarking cho automatic visit note generation là một bài toán riêng; vì vậy pipeline ASR của dự án phải được chấm cả upstream lẫn downstream, chứ không chỉ giải quyết transcript rồi mặc định xem note generation là xong. fileciteturn0file2 fileciteturn0file3 citeturn24academia1

Pseudo-code dưới đây thể hiện một protocol benchmark có thể tái lập.

```python
def benchmark_models(encounters, models, vad_cfg, decode_cfg, align_cfg, diar_cfg):
    eligible = [
        e for e in encounters
        if is_eligible_for_eval(e) and e["is_holdout"] is True
    ]

    report = []
    for model in models:
        for encounter in eligible:
            wav = preprocess_audio(encounter["audio_path"])       # mono, 16kHz, offset map
            speech_chunks = run_vad(wav, vad_cfg)                 # preserve global offsets
            asr_segments = transcribe_chunks(model, speech_chunks, decode_cfg)
            aligned = align_segments(asr_segments, wav, align_cfg)
            diarized = diarize_audio(wav, diar_cfg)               # speaker_0, speaker_1, ...
            merged = merge_asr_alignment_diarization(aligned, diarized)

            metrics = score_against_gold(
                encounter_id=encounter["encounter_id"],
                predicted_segments=merged,
                gold_transcript=load_gold_transcript(encounter),
                gold_facts=load_gold_facts(encounter),
            )
            report.append({
                "encounter_id": encounter["encounter_id"],
                "model": model.name,
                "metrics": metrics,
                "versions": collect_versions(model, vad_cfg, align_cfg, diar_cfg),
            })

    return summarize_with_bootstrap_ci(report, cluster_key="encounter_id")
```

Pseudo-code này phản ánh đúng tinh thần schema/project docs: split theo encounter, giữ offset map, đo ASR lẫn fact safety, và log version của mọi engine. fileciteturn0file1 fileciteturn0file3 fileciteturn0file4 fileciteturn0file5 fileciteturn0file6 citeturn21view4turn19view4turn20view0turn10view1

## Tích hợp vào pipeline local first và các bổ sung bắt buộc trước pilot

### Tích hợp khuyến nghị cho từng tầng pipeline

Project plan đã gần như mô tả sẵn một pipeline đúng: audio preprocessing → VAD/chunking → ASR → timestamp/alignment → diarization → manual role mapping → transcript normalization → rule/dictionary extraction → structured JSON extraction → schema validator → SOAP draft → doctor review → final confirmed note. Cách tích hợp tốt nhất hiện nay là giữ đúng tính “modular and inspectable” của pipeline này, không collapse sang một bước generative end-to-end. fileciteturn0file1

| Tầng pipeline | Khuyến nghị triển khai | Guardrail bắt buộc |
|---|---|---|
| Audio preprocessing | FFmpeg decode, mono/16kHz, loudness normalization; denoising chỉ là tùy chọn noisy-clinic mode | Giữ offset map từ file gốc đến chunk đã xử lý |
| VAD/chunking | Silero VAD vì nhẹ, CPU-friendly, permissive license | Boundary overlap nhỏ để bảo vệ `không/chưa`, số đo, và tên thuốc ở biên chunk |
| ASR | Interface chung: `runtime + checkpoint`; mặc định benchmark trên faster-whisper | Khóa beam size/config khi so sánh |
| Timestamp/alignment | WhisperX default nếu có aligner tốt và chấp nhận extra deps; stable-ts hoặc whisper-timestamped là fallback | Tách evaluation text khỏi evaluation timing |
| Diarization | pyannote tạo `speaker_0/speaker_1/...` | Không tự suy diễn doctor/patient từ speaker ID |
| Role mapping | Manual first, có UI khóa role | Chỉ facts với role đã xác nhận mới được đi tiếp |
| Transcript normalization | Lưu song song raw transcript và normalized copy | Không overwrite raw evidence |
| Fact extraction | Chỉ tạo fact khi đủ evidence/provenance | Thiếu quote/time/speaker thì reject hoặc flag |
| SOAP/note draft | Sinh từ accepted/edited facts, không sinh trực tiếp từ raw transcript | Không cho unsupported fact lọt vào note |
| Export | Chỉ sau doctor confirmation | Không auto write-back HIS/EHR |

Nguồn: project plan/master report, encounter/transcript/fact schemas, cùng tài liệu chính thức của Silero VAD, faster-whisper, WhisperX, pyannote, stable-ts, whisper-timestamped. fileciteturn0file1 fileciteturn0file2 fileciteturn0file3 fileciteturn0file4 fileciteturn0file5 citeturn20view0turn21view4turn19view4turn10view1turn11view1turn11view0

Về timestamp/alignment, nên rất rõ ràng khi nào dùng công cụ nào. **WhisperX** là default hợp lý nếu cần word-level timestamps và có GPU, vì repo mô tả batched inference nhanh, dùng wav2vec2 alignment cho word-level timestamps, có pyannote-based diarization, và VAD preprocessing giúp giảm hallucination. Nhưng repo cũng cảnh báo những từ không có trong alignment dictionary như dạng số/tiền tệ có thể không align được, overlap speech được xử lý kém, và cần language-specific wav2vec2 model. Với lâm sàng, đây là lý do phải có **fallback segment-level evidence** khi word timing của số đo/lab không ổn. citeturn19view4

**stable-ts** phù hợp khi cần stack permissive/MIT, ít phụ thuộc hơn, và chấp nhận timestamp quality cần kiểm chứng thêm; nhưng vì repo thông báo development đang pause vô thời hạn, đây nên là **fallback maintainability-conscious**, không nên là lựa chọn chiến lược duy nhất cho lâu dài. **whisper-timestamped** hấp dẫn ở chỗ dùng cross-attention + DTW, có word confidence, hỗ trợ fine-tuned HF models và VAD như Silero/Auditok, nhưng lại mang license **AGPL-3.0** và chính repo mô tả là experimental, có thể ảnh hưởng đáng kể tới performance. Trong môi trường bệnh viện/doanh nghiệp, công cụ này thường chỉ nên vào nhánh benchmark hoặc internal research trừ khi legal sign-off rõ ràng. citeturn11view1turn11view2turn11view0

Về diarization, pyannote là lựa chọn tốt cho local pipeline, nhưng cần phân biệt very clearly giữa **speaker diarization** và **clinical role attribution**. pyannote cho speaker segmentation/identities, không cho doctor/patient semantics; còn Whisper model cards lại cảnh báo chính Whisper không nên dùng cho classification hay suy diễn thuộc tính con người. Kết hợp hai điểm này, rule vận hành đúng là: diarization chỉ tạo `speaker_n`; role mapping phải manual-first, ít nhất cho mọi encounter đi vào Gold/Evaluation hoặc mọi fact đi vào final note. citeturn10view1turn9view6turn19view0turn19view1

### Những phần còn thiếu phải bổ sung trước khi benchmark nghiêm túc hoặc pilot

Dự án hiện có nền governance và schema tốt hơn rất nhiều prototype ASR thông thường, nhưng vẫn còn những thiếu sót quan trọng trước khi fine-tune hoặc pilot.

| Thiếu sót | Tại sao quan trọng |
|---|---|
| Model card nội bộ cho từng artifact ASR/alignment/diarization | Vì license và training metadata hiện không đồng nhất trên mọi bề mặt phát hành |
| Dataset card cho từng tập | Để khóa nguồn, consent, allowed_use, deidentification, target_zone, checksum |
| Annotation guideline cho transcript/role/fact/negation/medication/dosage/allergy | Không có guideline thì “gold” không thực sự gold |
| Dataset registry thực tế | `dataset_registry.csv` không có trong tài liệu đã cung cấp, nên chưa audit được nguồn theo dataset |
| Explicit risk taxonomy cho clinical ASR | Để error analysis không chỉ dừng ở WER/CER |
| Red-team set phủ định, thuốc/liều, dị ứng, số đo, code-switching, overlap | Đây là nơi model tốt trên WER vẫn có thể thất bại nguy hiểm |
| UX review hỗ trợ click-back audio, accept/edit/reject fact, lock speaker role, audit log | Không có UX phù hợp thì doctor review sẽ trở thành nút thắt cổ chai |
| Holdout governance cứng hơn schema hiện tại | Vì `target_zone=evaluation` chưa mặc định kéo theo `holdout_only` |
| Schema validator mạnh hơn cho `clinical_fact.source_evidence` | Vì policy evidence-first hiện mạnh hơn ràng buộc required fields |
| Metadata mở rộng về accent/noise/overlap/SNR/device | Để benchmark phản ánh đúng outpatient ambient Vietnamese |

Nguồn và cơ sở suy luận cho các thiếu sót này đến từ project plan, master report và bốn schema upload; riêng yêu cầu về benchmark note-generation scarcity được củng cố thêm bởi ACI-Bench. fileciteturn0file1 fileciteturn0file2 fileciteturn0file3 fileciteturn0file4 fileciteturn0file5 fileciteturn0file6 citeturn24academia1

Một thiếu sót rất đáng chú ý là license review matrix. Nếu tổ chức cần một stack hoàn toàn permissive và dễ đóng gói nội bộ, thì `faster-whisper`/`PhoWhisper`/`WhisperX`/`stable-ts` có vẻ dễ xử lý hơn `whisper-timestamped`; nhưng `pyannote` community-1 lại có bước accept conditions/token gating, và `whisper-large-v3` đang có metadata license không thống nhất giữa OpenAI repo và HF card. Do đó “legal readiness” của stack hiện chưa thể coi là self-evident, dù về mặt mô hình nó khả dụng. citeturn12view1turn18view4turn10view1turn11view0turn11view2turn17view0turn3view3

Pseudo-code sau mô tả pipeline tạo tập fine-tuning sạch từ schema.

```python
def build_asr_training_set(encounters, segments, datasets):
    train_samples = []

    for seg in segments:
        enc = encounters[seg["encounter_id"]]
        ds = datasets[enc["dataset_id"]]

        if not governance_allows_training(enc, ds):
            continue
        if enc["is_holdout"] is True or ds["is_holdout"] is True:
            continue
        if seg["segment_status"] not in {"corrected", "reviewed"}:
            continue
        if not valid_audio_span(seg["audio_span"]):
            continue
        if is_machine_transcript_only(seg):
            continue

        raw_text = seg["text"]
        target_text = canonicalize_for_asr(raw_text)   # light normalization only
        audio = cut_audio(enc["audio_path"], seg["audio_span"])

        train_samples.append({
            "encounter_id": enc["encounter_id"],
            "segment_id": seg["segment_id"],
            "audio": audio,
            "target_text": target_text,
            "speaker_role": seg["speaker_role"],
            "language": enc["language"],
            "specialty": enc["specialty"],
            "source_type": enc["source_type"],
        })

    return split_by_encounter_id(train_samples)
```

Logic chính ở đây là: **không train trên raw_asr**, **không train trên holdout**, **không train khi governance chưa cho phép**, và **không để normalization làm mất evidence surface form**. fileciteturn0file4 fileciteturn0file5 fileciteturn0file6 citeturn14view0

## Kết luận, ma trận quyết định và checklist

### Kết luận và quyết định đề xuất

**Best immediate baseline** cho dự án là: **runtime mặc định = faster-whisper**, **checkpoint baseline chất lượng = Whisper large-v3**, **checkpoint baseline latency = Whisper large-v3-turbo**, và **baseline tiếng Việt bắt buộc phải benchmark = PhoWhisper-medium/large**. Điều này bám đúng project plan, tận dụng được hệ sinh thái Whisper hiện có, đồng thời vẫn mở cánh cửa cho specialization tiếng Việt mà không commit sớm vào một model family chưa được chấm trên outpatient clinical holdout. fileciteturn0file1 citeturn21view4turn18view1turn16view3turn27view1

**Fine-tuning readiness** nên đánh giá là **partially ready overall**, nhưng **not ready for real-patient ASR fine-tuning**. Dự án đã có schema tốt, governance gates khá mạnh, và kiến trúc evidence-first đúng. Tuy nhiên, tài liệu hiện cung cấp chưa chứng minh có một **gold/evaluation set đã freeze**, chưa có `dataset_registry.csv` để audit nguồn, chưa có annotation guideline đầy đủ trong tập tài liệu upload, và còn tồn tại các điểm cần legal review ở artifact/licensing. Vì thế: Stage benchmark và Stage adaptation nhẹ là sẵn sàng; PEFT chỉ nên mở sau khi có gold set đủ tốt; real-patient fine-tuning thì chưa nên mở. fileciteturn0file1 fileciteturn0file2 fileciteturn0file5 fileciteturn0file6

**Dataset readiness** nên tách theo nguồn. Synthetic data: **ready to build** và rất nên làm ngay. Volunteer/actor simulated data: **partially ready**, nên dùng để stress-test accent/noise/overlap. Public data: **ready for benchmark/bootstrap only after license review**. Real-patient data: **not ready for training**, nhưng có thể dùng cho evaluation hoặc pilot review workflow chỉ khi consent/governance/access policy thỏa schema và policy nội bộ. fileciteturn0file2 fileciteturn0file5 fileciteturn0file6

**Safety readiness** là “kiến trúc có hướng đúng, vận hành chưa đủ bằng chứng”. Các schema đã hỗ trợ provenance, doctor confirmation, retention/access control, và project plan đã chặn diagnosis/prescription/autowriteback. Nhưng clinical-safe deployment không đến từ schema một mình; nó đến từ benchmark đỏ, validator mạnh, role mapping manual, và việc final note chỉ tạo từ accepted/edited facts đã đủ evidence. Kiến trúc hiện tại làm được điều đó về mặt thiết kế, nhưng chưa có số liệu holdout nội bộ để xác nhận readiness vận hành. fileciteturn0file1 fileciteturn0file3 fileciteturn0file5

### Ma trận khuyến nghị sử dụng

| Thành phần | Use as baseline | Benchmark only | Fine tune later | Avoid for pilot until legal review | Ghi chú |
|---|---|---|---|---|---|
| faster-whisper | Có |  | Có |  | Runtime mặc định hợp lý |
| Whisper large-v3 | Có |  | Có thể |  | Baseline chất lượng tổng quát |
| Whisper large-v3-turbo | Có |  | Không ưu tiên |  | Baseline latency/transcription |
| PhoWhisper-medium | Có |  | Có |  | Baseline tiếng Việt chi phí vừa |
| PhoWhisper-large | Có thể sau benchmark | Có | Có |  | Ứng viên mạnh cho tiếng Việt |
| WhisperX |  | Có |  |  | Alignment default nếu toolchain phù hợp |
| stable-ts |  | Có |  |  | Fallback permissive, nhưng maintainability yếu hơn |
| whisper-timestamped |  | Có |  | **Có** | AGPL-3.0 và experimental |
| pyannote community-1 |  | Có |  | Có thể | Cần accept conditions/token; vẫn hữu ích cho local diarization |
| Full fine-tune trên real-patient audio |  |  |  | **Có** | Chưa đủ readiness/governance theo bằng chứng hiện có |

Nguồn cho matrix: project plan và tài liệu chính thức của từng model/tool. Trường hợp “Avoid for pilot until legal review” phản ánh rủi ro artifact-specific, không phải phủ nhận giá trị kỹ thuật của công cụ. fileciteturn0file1 citeturn21view4turn18view1turn16view3turn27view1turn19view4turn11view1turn11view0turn10view1turn9view6

### Checklist cuối báo cáo

- [ ] Khóa **artifact list** chính xác: runtime, checkpoint, alignment tool, diarization tool, validator version.  
- [ ] Lập **license review matrix** cho từng artifact, giải quyết dứt điểm chênh lệch metadata license của Whisper large-v3.  
- [ ] Freeze **Evaluation Zone** theo `encounter_id`, thêm validator bắt buộc `evaluation => holdout_only`.  
- [ ] Tạo **20–50 synthetic/actor outpatient encounters** có gold transcript, speaker role, facts, SOAP-lite.  
- [ ] Viết **annotation guideline** cho transcript, negation, medication, dosage, allergy, speaker role, clinical subject.  
- [ ] Bổ sung validator bắt buộc **`source_evidence.quote/start_time/end_time`** cho accepted/edited facts.  
- [ ] Benchmark tối thiểu 4 cấu hình: large-v3, turbo, PhoWhisper-medium, PhoWhisper-large trên cùng preprocessing/VAD/decoding.  
- [ ] Chấm đủ **WER/CER + Negation Error Rate + Medication Error Rate + Critical Entity Error Rate + Source Attribution Accuracy + Speaker Attribution Accuracy**.  
- [ ] Thêm **hardware benchmark** CPU/GPU/RAM/latency/throughput trên máy đích local-first.  
- [ ] Bắt buộc **manual role mapping** trước khi fact được phép vào final note.  
- [ ] Giữ song song **raw transcript** và **normalized copy**; không để dictionary correction overwrite evidence.  
- [ ] Không fine-tune trên real-patient audio trước khi có **gold/eval set đủ tốt** và **legal/consent approval** rõ ràng.  

Kết luận ngắn gọn nhất là: **dùng Whisper large-v3/turbo qua faster-whisper để dựng baseline production-local trước; benchmark PhoWhisper-medium/large một cách bắt buộc; chỉ fine-tune khi dữ liệu gold, holdout và governance đã thật sự sẵn sàng**. Ở thời điểm hiện tại, quyết định kỹ thuật an toàn nhất không phải là “fine-tune sớm”, mà là **đo thật kỹ, chặn lỗi nguy hiểm, và ép mọi output lâm sàng quay về evidence có thể click-back**. fileciteturn0file1 fileciteturn0file2 fileciteturn0file3 fileciteturn0file4 fileciteturn0file5 fileciteturn0file6 citeturn21view4turn18view1turn16view3turn27view1turn14view0turn19view0