# Manual Audit 30 Samples - 3 Models

Quy tắc audit nhanh:
1. Có mất từ "không/chưa" không?
2. Có đổi đau ngực/khó thở không?
3. Có sai thuốc không?
4. Có sai số/liều/đơn vị không?
5. Có thêm bệnh/thuốc không có trong audio không?
6. Có bỏ sót red flag không?
Không cần sửa mọi lỗi nhỏ. Chỉ cần đánh dấu lỗi ảnh hưởng lâm sàng.

## Sample 1: `public_vietmed_0122`

**Reference:** ta không nên sờ nắn bóp vào đấy đấy có một cái câu chuyện rất là nhiều người đấy là khi chúng ta đau ở đâu chúng ta hãy bóp vào đấy nhưng mà trong trường

**ChunkFormer:** ta nên sờ nắn bóp vào đấy có một cái câu chuyện rất là nhiều người đấy là khi chúng ta đau ở đâu chúng ta hay bóp vào đấy

**PhoWhisper-medium:** chúng ta không nên sờ nắn bóp vào đấy đấy có một cái câu chuyện rất là nhiều người đấy là khi chúng ta đau ở đâu chúng ta hay bóp vào đấy.

**PhoWhisper-base:** ta không nên sờ nắn bóp vào đấy đấy có một cái câu chuyện rất là nhiều người đấy là khi chúng ta đau ở đâu chúng ta hay bóp vào đấy.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: mất “không nên”, đảo nghĩa khuyến cáo.
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 2: `public_vietmed_0325`

**Reference:** của chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh của chúng ta chứ không

**ChunkFormer:** chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh của chúng ta

**PhoWhisper-medium:** của chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh của chúng ta.

**PhoWhisper-base:** của chúng ta thì khi đó rõ ràng chúng ta biết rằng chúng ta cần phải điều chỉnh cái bệnh của chúng ta.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: mất cụm phủ định “chứ không”.
- **PhoWhisper-medium:** [ ] Pass | [x] Error: mất cụm phủ định “chứ không”.
- **PhoWhisper-base:** [ ] Pass | [x] Error: mất cụm phủ định “chứ không”.
---

## Sample 3: `public_vietmed_0495`

**Reference:** xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không

**ChunkFormer:** xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó

**PhoWhisper-medium:** hẳn ngày xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó.

**PhoWhisper-base:** giải hắc ngày xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: mất “không”.
- **PhoWhisper-medium:** [ ] Pass | [x] Error: mất “không”.
- **PhoWhisper-base:** [ ] Pass | [x] Error: mất “không”.
---

## Sample 4: `public_vietmed_0424`

**Reference:** hiệu quả nhưng lại tác dụng phụ không có nhiều như vậy không ảnh hưởng đến nội tạng nhiều như vậy và bản thân

**ChunkFormer:** hiệu quả nhưng lại tác dụng phụ không có nhiều như vậy không ảnh hưởng đến nội tạng nhiều như vậy và bản thân

**PhoWhisper-medium:** có cái hiệu quả nhưng lại tác dụng phụ không nó nhiều như vậy không ảnh hưởng đến nội tạng nhiều như vậy và bản thân.

**PhoWhisper-base:** nó hiệu quả nhưng lại tác dụng phụ không có nhiều như vậy không ảnh hưởng đến nội tạng nhiều như vậy và bản thân.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 5: `public_vietmed_0062`

**Reference:** thông dụng thôi nhưng mà mọi người nên để ý để tránh cái tình trạng là các cái tác động nó cứ tích lũy ngày một ngày

**ChunkFormer:** là thông dụng thôi nhưng mà mọi người nên để ý để tránh cái tình trạng là các cái tác động nó cứ tích tụ

**PhoWhisper-medium:** nó rất là thông dụng thôi nhưng mà mọi người nên để ý để tránh cái tình trạng là các cái tác động nó cứ tích.

**PhoWhisper-base:** của nó rất là thông dụng thôi nhưng mà mọi người nên để ý để tránh cái tình trạng là các cái tác động nó cứ tích.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 6: `public_vietmed_0273`

**Reference:** trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bệnh cao tuổi đúng không ạ

**ChunkFormer:** chương trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bị bệnh

**PhoWhisper-medium:** hỏi đến chương trình và chúc bác thật là nhiều sức khoẻ vâng vừa rồi chúng ta thấy là rất là nhiều người bệnh.

**PhoWhisper-base:** hỏi đến chương trình và chúc bác thử nhiều sức khoẻ vâng vừa rồi chúng ta thấy là rất là nhiều người bệnh.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: mất “cao tuổi”, đổi nhóm bệnh nhân.
- **PhoWhisper-medium:** [ ] Pass | [x] Error: mất “cao tuổi”.
- **PhoWhisper-base:** [ ] Pass | [x] Error: mất “cao tuổi”.
---

## Sample 7: `public_vietmed_0431`

**Reference:** này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình không hai

**ChunkFormer:** mã này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình

**PhoWhisper-medium:** cái mã này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình.

**PhoWhisper-base:** cái mã này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin nhắc lại tầm đàn của chương trình.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 8: `public_vietmed_0919`

**Reference:** giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó không có

**ChunkFormer:** giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó

**PhoWhisper-medium:** giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều.

**PhoWhisper-base:** giai đoạn sau mười năm cái việc mà phẫu thuật thích thích nấu sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: mất “không có”.
- **PhoWhisper-medium:** [ ] Pass | [x] Error: mất “không có”.
- **PhoWhisper-base:** [ ] Pass | [x] Error: mất “không có”, sai thuật ngữ “kích thích não sâu”.
---

## Sample 9: `public_vietmed_0884`

**Reference:** nó sẽ giúp cải thiện được rất là nhiều các triệu chứng của người bệnh parkinson đặc biệt là các cái triệu chứng về vận

**ChunkFormer:** thích não sâu nó sẽ giúp cải thiện được rất là nhiều các triệu chứng của người bệnh parkinson đặc biệt là các cái triệu chứng

**PhoWhisper-medium:** nội sau nó sẽ giúp cải thiện được rất là nhiều các triệu chứng của người bệnh bạc kinh doanh đặc biệt là các cái triệu chứng.

**PhoWhisper-base:** thích nói sau nó sẽ giúp cải thiện được rất là nhiều các cái triệu chứng của người bệnh bắc kinh doanh đặc biệt là các cái triệu chứng.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [ ] Pass | [x] Error: sai “Parkinson”.
- **PhoWhisper-base:** [ ] Pass | [x] Error: sai “Parkinson”.
---

## Sample 10: `public_vietmed_0174`

**Reference:** đấy thì cái câu chuyện là gì ạ đạp xe ở trong nhà nó rất là an toàn nhưng mà đạp xe ra ngoài thì nó lại rất nhiều chuyện

**ChunkFormer:** ngoài đấy thì cái câu chuyện là gì ạ đạp xe ở trong nhà nó rất là an toàn nhưng mà đạp xe ra ngoài thì nó lại rất nhiều cái

**PhoWhisper-medium:** ngoài đấy thì cái câu chuyện là gì ạ đạp xe ở trong nhà nó rất là an toàn nhưng mà đạp xe ra ngoài thì nó lại rất nhiều.

**PhoWhisper-base:** ngoài đấy thì cái câu chuyện là địa đạp xe ở trong nhà nó rất là an toàn nhưng mà đạp xe ra ngoài thì nó lại rất nhiều chi.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 11: `public_vietmed_0148`

**Reference:** với tất cả những cái biểu hiện như vậy thì chúng tôi thấy khá là rõ ràng là nó có khả năng là cái biểu hiện của một cái

**ChunkFormer:** với tất cả những cái biểu hiện như vậy thì chúng tôi thấy khá là rõ ràng là nó có khả năng là cái biểu hiện của nó

**PhoWhisper-medium:** nên thì với tất cả những cái biểu hiện như vậy thì chúng tôi thấy khá là rõ rằng là nó có khả năng là phê biểu hiện của.

**PhoWhisper-base:** thì với tất cả những biểu hiện như vậy thì chúng tôi thấy khá là rõ rằng là nó có khả năng là biểu hiện của.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 12: `public_vietmed_0420`

**Reference:** tổng đài này thì sẽ có cơ hội nhận được ưu đãi của chương trình vâng và sẽ quay trở lại với chương trình của chúng ta

**ChunkFormer:** số tổng đài này thì sẽ có cơ hội nhận được ưu đãi của chương trình vâng và sẽ quay trở lại

**PhoWhisper-medium:** bị gọi về hai số đồng đài này thì sẽ có cơ hội nhận được ưu đãi của chương trình vâng và sẽ quay trở lại.

**PhoWhisper-base:** chị gọi về hai số tổng thái này thì sẽ có cơ hội nhận được ưu đãi của chương trình vân và sẽ quay trở lại.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 13: `public_vietmed_0962`

**Reference:** bình luận bên dưới các bác sĩ của chương trình sẽ giải đáp câu hỏi của quý vị trong phần cuối của chương trình quý vị nha thưa tất cả quý vị khi nói đến

**ChunkFormer:** ngay phần bình luận bên dưới các bác sĩ của chương trình sẽ giải đáp câu hỏi của quý vị trong phần cuối của chương trình quý vị nha thưa tất cả quý vị khi nói đến

**PhoWhisper-medium:** ngay phần bình luận bên dưới các bác sĩ của chương trình sẽ giải đáp câu hỏi của quý vị trong phần cuối của chương trình quý vị nha thưa thiên tất cả quý vị khi nói đến bệnh.

**PhoWhisper-base:** ngay phần bình luận bên dưới các bác sĩ của chương trình sẽ giải đáp câu hỏi của quý vị cho phần cuối của chương trình quý vị nhé thưa tất cả quý vị khi nói đến biển.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 14: `public_vietmed_0149`

**Reference:** biểu hiện tê bì dọc theo tay hoặc là cái vùng cổ vai gáy này cái thứ ba nữa là nó lại còn liên quan đến cái câu chuyện là

**ChunkFormer:** biểu hiện tê bì dọc theo tay hoặc là cái vùng cổ vai gáy này cái thứ ba nữa là nó lại còn liên quan

**PhoWhisper-medium:** unk động rồi các biểu hiện tê bì dọc theo tay hoặc là vùng cổ vai gáy này cái thứ ba nữa là nó lại còn liên quan.

**PhoWhisper-base:** động là các biểu hiện tê bì dọc theo tay hoặc là vùng cổ gai gáy ngày thứ ba nữa là nó lại còn liên quan.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [ ] Pass | [x] Error: sai vùng “cổ vai gáy”.
---

## Sample 15: `public_vietmed_0976`

**Reference:** thôi do đó thì những cái triệu chứng mà nó sẽ giúp cho người bệnh

**ChunkFormer:** bệnh do đó thì những cái triệu chứng mà nó sẽ giúp cho người bệnh

**PhoWhisper-medium:** do đó thì những cái triệu chứng mà nó sẽ giúp cho người bệnh.

**PhoWhisper-base:** do đó thì những chiều chứng mà nó sẽ giúp cho người bệnh.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [ ] Pass | [x] Error: sai “triệu chứng”.
---

## Sample 16: `public_vietmed_0080`

**Reference:** rất là nặng và càng về sau mà mình càng muộn phát hiện thì cái việc điều trị nó lại càng khó khăn hơn chính vì thế cho

**ChunkFormer:** sẽ rất là nặng và càng về sau mà mình càng muộn phát hiện thì cái việc điều trị nó lại càng khó khăn hơn thì chính cái

**PhoWhisper-medium:** những lần sau nó sẽ rất là nặng và càng về sau mà mình càng muộn phát hiện thì cái việc điều trị nó lại càng khó khăn hơn.

**PhoWhisper-base:** những lần sau nó sẽ rất là nặng và càng về sau mà mình càng muộn phát hiện thì cái việc điều trị nó lại càng khó khăn hơn chính mình.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 17: `public_vietmed_0776`

**Reference:** của mình nó có đảm bảo được cái việc như những tài liệu người ta nói không

**ChunkFormer:** nơi điều trị của mình nó có đảm bảo được cái việc mà như những tài liệu người ta nói hay không tất

**PhoWhisper-medium:** nơi điều trị của mình nó có đảm bảo được cái việc mà như như như những tài liệu người ta nói hay không tức là.

**PhoWhisper-base:** nơi điều trị của mình nó có đảm bảo được cái việc mà như như những tài liệu người ta nói hay không tức là.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 18: `public_vietmed_0303`

**Reference:** như thế này và chúng tôi khuyên là bác cũng nên đi thăm khám với các cái bác sĩ

**ChunkFormer:** cái việc như thế này và chúng tôi khuyên là bác cũng nên đi thăm khám với các cái sĩ

**PhoWhisper-medium:** phải nhận định hai cái việc như thế này và chúng tôi khuyên là bác cũng nên đi thăm khám với các cái.

**PhoWhisper-base:** cảnh nhận định hai cái việc như thế này và chúng tôi khuyên là bác cũng nên đi thăm khám với các cái.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: mất “bác sĩ” trong khuyến cáo đi thăm khám.
- **PhoWhisper-medium:** [ ] Pass | [x] Error: mất “bác sĩ”.
- **PhoWhisper-base:** [ ] Pass | [x] Error: mất “bác sĩ”.
---

## Sample 19: `public_vietmed_0996`

**Reference:** tiếp tục uống các cái thuốc với cái lượng gần như gần bằng so với trước trước khi mà phẫu thuật và sau một tháng

**ChunkFormer:** tiếp tục uống các cái thuốc với cái lượng gần như gần bằng so với trước trước khi mà phẫu thuật và sau một

**PhoWhisper-medium:** phải tiếp tục uống các cái thuốc với cái lượng gần như gần bằng so với trước trước khi mà phẫu thuật và sau một tháng.

**PhoWhisper-base:** phải tiếp tục uống chắc kết thúc với lượng gần như gần bằng so với trước trước khi mà phẫu thuật và sau một tháng.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: mất “tháng”, sai thông tin thời gian.
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [ ] Pass | [x] Error: sai cụm “uống thuốc”.
---

## Sample 20: `public_vietmed_0526`

**Reference:** người bệnh của chúng ta cũng đang có một cái tha thiết là mình tìm được một cái giải pháp gì đó mà chúng ta điều trị có

**ChunkFormer:** cái người bệnh của chúng ta cũng đang có một cái tha thiết là mình tìm được một cái giải pháp gì đó mà chúng ta điều trị cái

**PhoWhisper-medium:** bản thân những cái người bệnh của chúng ta cũng đang có một cái tha thiết là mình tìm được một cái giải pháp gì đó mà chúng ta điều trị.

**PhoWhisper-base:** bản thân những cái người bệnh của chúng ta cũng đang có một cái tha thiết là mình tìm được một cái giải pháp gì đó mà chúng ta điều trị.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 21: `public_vietmed_0775`

**Reference:** vào và mình tính toán các tọa độ để mình đi vào sau đó là bệnh nhân sẽ được tiến hành phẫu thuật thì bệnh nhân

**ChunkFormer:** vị trí mình đi vào và mình tính toán các tọa độ để mình đi vào sau đó là bệnh nhân sẽ được tiến hành phẫu thuật thì bệnh

**PhoWhisper-medium:** vị trí mình đi vào và mình tính toán cách tọa độ để mình đi vào và sau đó là bệnh nhân sẽ đượctiến hành phẫu thuật thì bệnh.

**PhoWhisper-base:** quý vị trí mình đi vào và mình tính toán các tội độ để mình đi vào vậy sau đó là bệnh nhân sẽ được tiến hành phẫu thuật thị bình.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [ ] Pass | [x] Error: sai “tọa độ” trong ngữ cảnh phẫu thuật.
---

## Sample 22: `public_vietmed_0232`

**Reference:** ta có thể hiểu một cách nôm na là mạch máu nó đến ở đây nhưng mà xương nó ở đây khớp nó ở đây nghĩa là nó từ chỗ này đến

**ChunkFormer:** chúng ta có thể hiểu một cách nôm na là mạch máu nó đến ở đây nhưng mà xương nó ở đây khớp nó ở đây thì là nghĩa là

**PhoWhisper-medium:** ra chúng ta có thể hiểu một cách nôm na là mạch máu nó đến ở đây nhưng mà xương nó ở đây khớp nó ở đây nghĩa.

**PhoWhisper-base:** chúng ta có thể hiểu một cách nôm na là mạch máu nó đến ở đây nhưng mà xương nó ở đây khớp nó ở đây.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 23: `public_vietmed_0626`

**Reference:** luận cuối cùng chính vì vậy cho nên trong trường hợp này của anh thì chúng tôi nghĩ là của anh cũng gần được năm năm rồi đấy thế cho nên là anh phải cố gắng

**ChunkFormer:** luận cuối cùng chính vì vậy cho nên trong trường hợp này của anh thì chúng tôi nghĩ là của anh cũng gần được năm rồi đấy thế cho nên là

**PhoWhisper-medium:** kết luận cuối cùng chính vì vậy cho nên trong trường hợp này của anh thì chúng tôi nghĩ là của anh cũng gần được năm năm rồi đấy thế cho nên là.

**PhoWhisper-base:** kết luận cuối cùng chính vì vậy cho nên trong trường hợp này của anh thì chúng tôi nghĩ là của anh cũng gần được năm năm rồi đấy thế cho nên là.

### Clinical Review Note
- **ChunkFormer:** [ ] Pass | [x] Error: “năm năm” thành “năm”, sai thời lượng.
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 24: `public_vietmed_0801`

**Reference:** cái hiệu quả điều trị cao nhất hạn chế tác dụng phụ của điện cực cũng như là kéo dài cái thời gian lâu nhất của cục

**ChunkFormer:** điều trị cao nhất hạn chế tác dụng phụ của điện cực cũng như là kéo dài cái thời gian lâu nhất

**PhoWhisper-medium:** cao nhất hạn chế tác dụng phụ của điện cực cũng như là kéo dài cái thời gian lâu nhất.

**PhoWhisper-base:** quá điều trị cao nhất hạn chế tác dụng của điện cực cũng như là kéo dài cái thời gian lâu nhất.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [ ] Pass | [x] Error: mất “tác dụng phụ”, đổi nghĩa.
---

## Sample 25: `public_vietmed_0562`

**Reference:** phải vịn mình sẽ phải luôn luôn phòng tránh luôn luôn nghĩ rằng là nó sắp ngã rồi thì mình phải cẩn thận nếu mà ngã

**ChunkFormer:** sẽ phải vịn mình sẽ phải luôn phòng tránh luôn nghĩ rằng là nó sắp ngã rồi thì mình phải cẩn thận nếu mà mình

**PhoWhisper-medium:** mình sẽ phải vịn mình sẽ phải luôn luôn phòng tránh luôn luôn nghĩ rằng là nó sắp ngã rồi thì mình phải cẩn thận nếu mà.

**PhoWhisper-base:** mình sẽ bẻ vị mình sẽ bẻ luôn luôn phòng tránh luôn luôn nghĩ rằng là nó sắp ngã rồi thì mình phải cẩn thận nếu mà ngã.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 26: `public_vietmed_0510`

**Reference:** mừng là bác đã có đi thăm khám ở bệnh viện cũng đã có những cái chụp chiếu để có cái khẳng định và cái triệu chứng của

**ChunkFormer:** là mừng là bác đã có đi thăm khám ở bệnh viện cũng đã có những cái chụp chiếu để có cái khẳng định cái

**PhoWhisper-medium:** cũng rất mừng là bác đã có đi thăm khám ở bệnh viện cũng đã có những cái chụp chiếu để có cái khẳng định.

**PhoWhisper-base:** cũng rất mừng là bác đã có đi thăm khám ở bệnh viện cũng đã có những cái chục chiếu để có cái khẳng định.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 27: `public_vietmed_0841`

**Reference:** triệu chứng nhưng có một số triệu chứng thì phẫu thuật kích thích não sâu nó không có giúp ích được ví dụ những cái

**ChunkFormer:** triệu chứng nhưng có một số triệu chứng thì phẫu thuật kích thích não sâu nó không có giúp ích được ví dụ những cái triệu chứng

**PhoWhisper-medium:** triệu chứng nhưng có một số triệu chứng thì phẫu thuật kích thích não sau nó không có giúp ích được ví dụ những cái triệu chứng.

**PhoWhisper-base:** triệu chứng nhưng có một số triệu chứng thì phẫu thuật kích thích não sau nó không có giúp ích được ví dụ những chiều.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 28: `public_vietmed_0120`

**Reference:** mà chúng ta lưu ý cũng như là duy trì các cái biện pháp điều trị duy trì của chúng ta là hết sức là quan trọng bởi

**ChunkFormer:** việc mà chúng ta lưu ý cũng như là duy trì các cái biện pháp điều trị duy trì của chúng ta là hết sức

**PhoWhisper-medium:** nữa là cái việc mà chúng ta lưu ý cũng như là duy trì các cái biện pháp điều trị duy trì của chúng ta là hết sức.

**PhoWhisper-base:** nhất là cái việc mà chúng ta lưu ý cũng như duy trì các biện pháp điều trị duy trì của chúng ta là hết sức.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 29: `public_vietmed_0478`

**Reference:** cũng không có nhiều cho nên xin phép là chúng tôi cũng sẽ tư vấn ngắn gọn như này đi vào các vấn đề chính vấn đề số một

**ChunkFormer:** cũng không có nhiều cho nên xin phép là chúng tôi cũng sẽ tư vấn ngắn gọn như này đi vào các cái vấn đề chính vấn đề là

**PhoWhisper-medium:** thời gian cũng không có nhiều cho nên xin phép là chúng tôi cũng sẽ tư vấn ngắn gọn như này đi vào các vấn đề chính vấn đề số.

**PhoWhisper-base:** thời gian cũng không có nhiều cho nên xin phép là chúng tôi cũng sẽ tư vấn ngắn gọn như này đi vào các cái vấn đề chính vấn đề xuống.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

## Sample 30: `public_vietmed_0145`

**Reference:** thấy rằng là có một cái hoạt chất nó có cái tác dụng mà chống viêm giảm đau chính là để để phát huy cái tác dụng này

**ChunkFormer:** thấy rằng là có một cái hoạt chất nó có cái tác dụng mà chống viêm giảm đau chính là để phát huy hóa

**PhoWhisper-medium:** nhận thấy rằng là có một cái hoạt chất nó có cái tác dụng mà chống viêm giảm đau chính là để để phát huy.

**PhoWhisper-base:** nhận thấy rằng là có một cái hoạt chất nó có cái tác dụng chống viêm giảm đau chính là để để phát huy.

### Clinical Review Note
- **ChunkFormer:** [x] Pass | [ ] Error:
- **PhoWhisper-medium:** [x] Pass | [ ] Error:
- **PhoWhisper-base:** [x] Pass | [ ] Error:
---

