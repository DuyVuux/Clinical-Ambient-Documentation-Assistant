# ASR Medical Error Analysis — nguyenvulebinh/ViStreamASR

## Summary

- Samples: 200
- Samples with critical/high missing error: 14

## Group summary

| Group | Severity | Ref samples | Missing samples | Missing total | Inserted samples | Inserted total |
|---|---|---:|---:|---:|---:|---:|
| negation | critical | 52 | 13 | 15 | 4 | 4 |
| symptom | moderate | 61 | 10 | 10 | 7 | 7 |
| medication | high | 0 | 0 | 0 | 0 | 0 |
| allergy | critical | 0 | 0 | 0 | 0 | 0 |
| dose_unit | high | 6 | 1 | 1 | 3 | 3 |
| number | moderate | 0 | 0 | 0 | 0 | 0 |
| red_flag | high | 0 | 0 | 0 | 0 | 0 |

## Top missing terms

### negation
- `không`: 10
- `không có`: 3
- `chưa`: 2

### symptom
- `ho`: 10

### medication
- None

### allergy
- None

### dose_unit
- `ngày`: 1

### number
- None

### red_flag
- None

## Critical/high examples

### public_vietmed_0776

**Reference:** của mình nó có đảm bảo được cái việc như những tài liệu người ta nói không

**Prediction:** nơi điều trị của mình nó có đảm bảo được cái việc mà như như như những tài liệu ta

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0495

**Reference:** xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bây giờ nó không

**Prediction:** bài hát ngay xưa cái đôi tay của mình và cái vai của mình nó đau đớn thế nào thì bên

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0062

**Reference:** thông dụng thôi nhưng mà mọi người nên để ý để tránh cái tình trạng là các cái tác động nó cứ tích lũy ngày một ngày

**Prediction:** rất là thông dụng thôi nhưng mà mọi mình nên để ý để tránh cái tình trạng là các cái tác động

**Flags:**
- dose_unit (high): missing ['ngày']

### public_vietmed_0192

**Reference:** dạ vâng và cái việc mà bác nói khó như này nó đã có lâu chưa ạ

**Prediction:** vâng dạ vâng ờ và cái việc mà bác nói khó như này nó có

**Flags:**
- negation (critical): missing ['chưa']

### public_vietmed_0628

**Reference:** là bác bị đau lưng cũng đã lâu rồi và đau cả hai đầu gối nữa đúng không ạ vâng dạ vâng vậy thì với những cái triệu

**Prediction:** vâng là bác đau lưng cũng đã lâu rồi và đau cả hai đầu gối nữa đúng ạ vâng dạ vâng

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0273

**Reference:** trình và chúc bác thật là nhiều sức khỏe vâng vừa rồi thì chúng ta thấy là rất là nhiều người bệnh cao tuổi đúng không ạ

**Prediction:** hỏi cái chương trình và chúc bác lấy nhiều sức khỏe vâng vừa rồi chúng ta thấy là rất là nhiều người

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0424

**Reference:** hiệu quả nhưng lại tác dụng phụ không có nhiều như vậy không ảnh hưởng đến nội tạng nhiều như vậy và bản thân

**Prediction:** có hiệu quả nhưng lại tắt dụng phụ không nhiều như vậy không ảnh hưởng đến nội tạng nhiều như vậy và

**Flags:**
- negation (critical): missing ['không có']

### public_vietmed_0410

**Reference:** như bác sĩ nói thì rất là nhiều đối tượng chúng ta đều có thể mắc cái bệnh cơ xương khớp đúng không ạ vậy thì nhiều

**Prediction:** nữa ờ như bác nói thì rất là nhiều đối tượng chúng ta đều có thể mắc cái bệnh cơ xương khớp

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0287

**Reference:** chúng ta bị trục trặc mà chẳng qua là cái hệ thần kinh ở trung ương tức là ở sọ não đấy nó không điều khiển được một

**Prediction:** của chúng ta bị trục trặc mà chẳng qua là cái hệ thần kinh ở trung ương tức là ở sọ não đấy

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0354

**Reference:** chẳng may bác ngã mà nó lại gãy xương thì tất cả những cái câu chuyện đó nó lại trở nên là không có ý nghĩa cho nên cái

**Prediction:** nếu chẳng may bác ngã mà nó lại chưa thì tất cả những cái câu chuyện đó nó lại trở nên là

**Flags:**
- negation (critical): missing ['không', 'không có']

### public_vietmed_0431

**Reference:** này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại tổng đài của chương trình không hai

**Prediction:** cái mã này chúng ta sẽ có thể có thông tin về sản phẩm vâng và tôi cũng xin được nhắc lại

**Flags:**
- negation (critical): missing ['không']

### public_vietmed_0919

**Reference:** giai đoạn sau mười năm cái việc mà phẫu thuật kích thích não sâu nó trở nên kém hiệu quả hơn tuy nhiên điều đó không có

**Prediction:** giai đoạn sau mười năm cái việc mà thuật ờ kích thích não sau cái nó trở nên kém hiệu quả hơn

**Flags:**
- negation (critical): missing ['không', 'không có']

### public_vietmed_0318

**Reference:** chứng này tôi đã bác đã bị lâu chưa ạ

**Prediction:** với những triệu chứng này thì bác

**Flags:**
- negation (critical): missing ['chưa']

### public_vietmed_0325

**Reference:** của chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh của chúng ta chứ không

**Prediction:** của chúng ta thì khi đó rõ ràng chúng ta biết rằng là chúng ta cần phải điều chỉnh cái bệnh

**Flags:**
- negation (critical): missing ['không']
