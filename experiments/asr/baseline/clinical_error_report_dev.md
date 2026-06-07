# Báo cáo Phân tích Lỗi Y Khoa (Clinical Error Analysis)

Báo cáo này phân tích các lỗi nghiêm trọng trong y tế: bỏ sót/tự thêm từ phủ định, từ khóa y khoa, và lỗi ảo giác lặp từ.

## Mô hình: `khanhld/chunkformer-ctc-large-vie`
- **Tổng số mẫu:** 200
- **Bỏ sót Phủ định (Missed Negation):** 7 lỗi
- **Ảo giác Phủ định (Hallucinated Negation):** 1 lỗi
- **Bỏ sót Từ khóa Y khoa (Missed Medical Term):** 7 lỗi
- **Ảo giác Từ khóa Y khoa (Hallucinated Medical Term):** 1 lỗi
- **Ảo giác lặp từ (Loop Hallucination):** 0 lỗi

### Cảnh báo: Lỗi Phủ định (Nguy hiểm)
| Loại | Từ khóa | Reference | Prediction |
|---|---|---|---|
| Bỏ sót | `không` | xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không | xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó |
| Bỏ sót | `không` | ta không nên sờ nắn bóp vào đấy đấy có một cái câu chuyện rất là nhiều người đấy là khi chúng ta đau ở đâu chúng ta hãy bóp vào đấy nhưng mà trong trường | ta nên sờ nắn bóp vào đấy có một cái câu chuyện rất là nhiều người đấy là khi chúng ta đau ở đâu chúng ta hay bóp vào đấy |
| Bỏ sót | `không` | trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bệnh cao tuổi đúng không ạ | chương trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bị bệnh |
| Bỏ sót | `không` | này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình không hai | mã này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình |
| Bỏ sót | `không` | giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó không có | giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó |
| Bỏ sót | `không có` | giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó không có | giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó |
| Bỏ sót | `không` | của chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh của chúng ta chứ không | chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh của chúng ta |
| Tự thêm | `không` | trình đó mình có thể vứt bỏ điện cực cùng mình tắt cái máy đi thì cái những cái tế bào não mà mình đi tới kích thích đó | trình đó mình có thể rút bỏ điện cực không mình tắt cái máy đi thì cái những cái tế bào não mà mình đi tới mình kích thích |

---

## Mô hình: `phowhisper_base`
- **Tổng số mẫu:** 200
- **Bỏ sót Phủ định (Missed Negation):** 6 lỗi
- **Ảo giác Phủ định (Hallucinated Negation):** 3 lỗi
- **Bỏ sót Từ khóa Y khoa (Missed Medical Term):** 13 lỗi
- **Ảo giác Từ khóa Y khoa (Hallucinated Medical Term):** 8 lỗi
- **Ảo giác lặp từ (Loop Hallucination):** 0 lỗi

### Cảnh báo: Lỗi Phủ định (Nguy hiểm)
| Loại | Từ khóa | Reference | Prediction |
|---|---|---|---|
| Bỏ sót | `không` | xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không | giải hắc ngày xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó |
| Bỏ sót | `hết` | chẩn đoán muộn ở trung bình là năm năm đấy có nghĩa là gì năm năm đầu là cứ chạy hết | mọi người được chẩn đoán muộn ở trung bình là năm năm đấy có nghĩa là gì năm năm đầu là |
| Bỏ sót | `không` | trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bệnh cao tuổi đúng không ạ | hỏi đến chương trình và chúc bác thử nhiều sức khoẻ vâng vừa rồi chúng ta thấy là rất là nhiều người bệnh |
| Bỏ sót | `không` | này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình không hai | cái mã này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin nhắc lại tầm đàn của chương trình |
| Bỏ sót | `không` | giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó không có | giai đoạn sau mười năm cái việc mà phẫu thuật thích thích nấu sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó |
| Tự thêm | `chẳng` | thấy làm sao cả nhưng mà bây giờ nó lại nặng như thế này thì chúng ta cũng cần phải hiểu rằng là rất nhiều trường hợp sau khi ngã xong sau khi thế nọ thế kia | đi kiểm tra chẳng thấy làm sao cả nhưng mà bây giờ nó lại nặng như thế này thì chúng ta cũng cần phải hiểu rằng là rất nhiều trường hợp sau khi ngã song sau khi |
| Tự thêm | `vô` | nó cũng có thể ảnh hưởng lên các cái bệnh lý mà nó đang có dạ vâng chính vì vậy cho nên là cái việc | hai nữa là cái đi đó nó cũng có thể ảnh hưởng lên các cái bệnh lý mà nó đang bị vô vài diệp rà vàng chính vì vậy cho nên là cái |
| Tự thêm | `hết` | lúc hoảng loạn lên hét tướng lên thế là tôi vùng dậy mà làm thế nào tôi vùng dậy xong tôi cứ | uổng liền trong lúc họ loạn lên thế là hết tướng lên thế là tôi nghĩ vùng dạy vừa làm là tôi vùng dậy trong tôi |

---

## Mô hình: `phowhisper_medium`
- **Tổng số mẫu:** 200
- **Bỏ sót Phủ định (Missed Negation):** 6 lỗi
- **Ảo giác Phủ định (Hallucinated Negation):** 6 lỗi
- **Bỏ sót Từ khóa Y khoa (Missed Medical Term):** 8 lỗi
- **Ảo giác Từ khóa Y khoa (Hallucinated Medical Term):** 13 lỗi
- **Ảo giác lặp từ (Loop Hallucination):** 0 lỗi

### Cảnh báo: Lỗi Phủ định (Nguy hiểm)
| Loại | Từ khóa | Reference | Prediction |
|---|---|---|---|
| Bỏ sót | `không` | xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không | hẳn ngày xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó |
| Bỏ sót | `hết` | chẩn đoán muộn ở trung bình là năm năm đấy có nghĩa là gì năm năm đầu là cứ chạy hết | mọi người được chẩn đoán muộn ở trung bình là năm năm đấy có nghĩa là gì năm năm đầu là |
| Bỏ sót | `không` | trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bệnh cao tuổi đúng không ạ | hỏi đến chương trình và chúc bác thật là nhiều sức khoẻ vâng vừa rồi chúng ta thấy là rất là nhiều người bệnh |
| Bỏ sót | `không` | này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình không hai | cái mã này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình |
| Bỏ sót | `không` | giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó không có | giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều |
| Tự thêm | `hết` | sướng và tự hào là mình đã sức khỏe coi như là quá tốt rồi chú sử dụng cái sản | và tự hào là mình đã sức khoẻ coi như là quá tốt rồi rồi chú dựng hết |
| Tự thêm | `không` | với cột sống ngực đâu bởi vì là sao bây giờ nó đã có những cái câu chuyện là tê liên quan đến cả tay nữa thậm chí là cả | không phải là cổ sống lưng với cổ sống ngực đâu bởi vì là sao bây giờ nó đã có những cái câu chuyện là tê liên quan đến cả tay nữa thậm chí là cả hai |
| Tự thêm | `không` | trình đó mình có thể vứt bỏ điện cực cùng mình tắt cái máy đi thì cái những cái tế bào não mà mình đi tới kích thích đó | mình có thể rút bỏ điện cửa không mình tắt cái máy đi thì những cái tế bào não mà mình đi tới mình kích thích đó |
| Tự thêm | `chẳng` | thấy làm sao cả nhưng mà bây giờ nó lại nặng như thế này thì chúng ta cũng cần phải hiểu rằng là rất nhiều trường hợp sau khi ngã xong sau khi thế nọ thế kia | đi kiểm tra chẳng thấy làm sao cả nhưng mà bây giờ nó lại nặng như thế này thì chúng ta cũng cần phải hiểu rằng là rất nhiều trường hợp sau khi ngã xong sau khi |
| Tự thêm | `hết` | lúc hoảng loạn lên hét tướng lên thế là tôi vùng dậy mà làm thế nào tôi vùng dậy xong tôi cứ | uổng hết trong lúc hoảng loạn lên nên là hét cứng lên nên là tôi vùng dậy một tám là tôi vùng dậy trong đôi |

---

## Mô hình: `whisper_small`
- **Tổng số mẫu:** 200
- **Bỏ sót Phủ định (Missed Negation):** 20 lỗi
- **Ảo giác Phủ định (Hallucinated Negation):** 4 lỗi
- **Bỏ sót Từ khóa Y khoa (Missed Medical Term):** 55 lỗi
- **Ảo giác Từ khóa Y khoa (Hallucinated Medical Term):** 1 lỗi
- **Ảo giác lặp từ (Loop Hallucination):** 0 lỗi

### Cảnh báo: Lỗi Phủ định (Nguy hiểm)
| Loại | Từ khóa | Reference | Prediction |
|---|---|---|---|
| Bỏ sót | `không` | xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không | đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó |
| Bỏ sót | `hết` | mà chúng ta lưu ý cũng như là duy trì các cái biện pháp điều trị duy trì của chúng ta là hết sức là quan trọng bởi | cái việc chúng ta lưu ý cũng là duy trì khác biện phát điều trì duy trì của chúng ta |
| Bỏ sót | `không` | cũng không có nhiều cho nên xin phép là chúng tôi cũng sẽ tư vấn ngắn gọn như này đi vào các vấn đề chính vấn đề số một | chúng tôi sẽ từ vấn ngắn gọn như thế này đi vào các vấn đề chính vấn đề xuống |
| Bỏ sót | `không` | ta không nên sờ nắn bóp vào đấy đấy có một cái câu chuyện rất là nhiều người đấy là khi chúng ta đau ở đâu chúng ta hãy bóp vào đấy nhưng mà trong trường | để có một câu chuyện rất là nhiều người khi chúng ta đâu đâu chúng ta hãy móc ở đây |
| Bỏ sót | `hết` | chẩn đoán muộn ở trung bình là năm năm đấy có nghĩa là gì năm năm đầu là cứ chạy hết | mọi người được chẳng đoán muộn ở tung bình là năm năm đấy có nghĩa là gì năm năm đầu là |
| Tự thêm | `chẳng` | là phải gọi là bứt phá về mặt thời gian để chúng ta có một cái chẩn đoán chính xác cuối cùng sau đó thì chúng ta sẽ có | anh phải cố gắng là bức phá về mặt thời gian để có chẳng đoạn chính xác cuối cùng sau đó thì chúng ta sẽ |
| Tự thêm | `chẳng` | chẩn đoán muộn ở trung bình là năm năm đấy có nghĩa là gì năm năm đầu là cứ chạy hết | mọi người được chẳng đoán muộn ở tung bình là năm năm đấy có nghĩa là gì năm năm đầu là |
| Tự thêm | `hết` | của cơ thể của chúng ta nghĩa là từ hệ tim mạch hệ huyết áp rồi là đến hệ hô | khắc của cô thể của chúng ta nghĩa là từ hệ tim mạch hệ huyết áp rồi đến hết |
| Tự thêm | `chẳng` | các cường độ cho nó phù hợp nhất để điều chỉnh cái gia giảm cả lượng thuốc thì làm cái quá trình rất là dài và có thể | cơm đỏ cho nó phù hợp nhất để đi chẳng cái da giảm cái lượng thuốc thì là một cái quá trình rất tài dai |

---

