# Synthetic Encounter Specs — Vietnamese Outpatient Clinical Ambient Documentation MVP

**File:** `synthetic_data/synthetic_encounter_specs.md`  
**Scope:** Local-first Clinical Ambient Documentation Assistant for Vietnamese outpatient care  
**Stage:** Day 5–7  
**Version:** v0.1.0  
**Status:** Draft for MVP synthetic data design  
**Data type:** Synthetic only — no real patient data  

---

## 1. Purpose

Tài liệu này định nghĩa **20 synthetic outpatient encounter case outlines** cho MVP.  
Tuần này **chỉ thiết kế case outline**, chưa cần viết toàn bộ hội thoại.

Mục tiêu là tạo seed data có kiểm soát để kiểm thử các module:

- ASR transcript structure
- Diarization / speaker role attribution
- Clinical fact extraction
- Negation and assertion detection
- Medication, dosage, route, frequency extraction
- Allergy extraction
- Clinical subject attribution
- SOAP-lite / outpatient note generation
- Doctor review / confirmation workflow
- Evaluation hold-out design

---

## 2. Design Principles

1. **Synthetic-first:** Không dùng real patient data trong giai đoạn này.
2. **Outpatient-first:** Ưu tiên khám ngoại trú tiếng Việt.
3. **Source attribution-ready:** Mọi clinical fact sau này phải map được về transcript segment/audio span.
4. **Doctor-review-ready:** Mọi output lâm sàng chỉ là draft cho đến khi bác sĩ xác nhận.
5. **FHIR-ready:** Fact type nên có khả năng map về Observation, Condition, MedicationStatement/MedicationRequest, AllergyIntolerance, Procedure, Composition/DocumentReference.
6. **Difficulty progression:** Case đi từ dễ đến khó để test pipeline theo từng lớp.
7. **Safety-first:** Không thiết kế case khiến AI tự chẩn đoán hoặc tự quyết định điều trị mà không cần bác sĩ.

---

## 3. Common Label Taxonomy

Các label kỳ vọng có thể dùng trong synthetic annotation:

- `symptom`
- `negation`
- `duration`
- `severity`
- `vital_sign`
- `diagnosis`
- `differential_diagnosis`
- `medication`
- `dosage`
- `route`
- `frequency`
- `allergy`
- `procedure`
- `lab_test`
- `imaging`
- `past_history`
- `family_history`
- `social_history`
- `pregnancy_status`
- `clinical_subject`
- `speaker_role`
- `caregiver_reported`
- `doctor_instruction`
- `follow_up`
- `red_flag`
- `plan`

---

## 4. Case Outlines

---

# SYN_OUT_001

## Setting
Outpatient clinic

## Specialty
Internal medicine

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân ho 3 ngày, sốt nhẹ, không đau ngực, không khó thở, không dị ứng thuốc.

## Must include
- Present symptom: ho 3 ngày
- Present symptom: sốt nhẹ
- Negated symptom: không đau ngực
- Negated symptom: không khó thở
- Medication: paracetamol 500mg
- Allergy: không dị ứng thuốc
- Follow-up: tái khám nếu sốt cao hoặc khó thở

## Difficulty
Easy

## Expected labels
symptom, duration, negation, medication, dosage, allergy, plan, follow_up, red_flag

---

# SYN_OUT_002

## Setting
Outpatient clinic

## Specialty
Pediatrics

## Roles
Doctor, Caregiver, Patient

## Clinical scenario
Mẹ đưa trẻ 6 tuổi đi khám vì sốt 2 ngày và ho. Trẻ vẫn ăn uống được, không co giật, không phát ban. Mẹ là người cung cấp phần lớn thông tin.

## Must include
- Clinical subject: patient là trẻ em
- Speaker role: caregiver nói thay bệnh nhân
- Present symptom: sốt 2 ngày
- Present symptom: ho
- Negated symptom: không co giật
- Negated symptom: không phát ban
- Medication: paracetamol siro theo cân nặng
- Follow-up: quay lại nếu sốt cao liên tục, li bì, khó thở

## Difficulty
Medium

## Expected labels
symptom, duration, negation, medication, dosage, clinical_subject, caregiver_reported, speaker_role, plan, follow_up, red_flag

---

# SYN_OUT_003

## Setting
Outpatient clinic

## Specialty
Cardiology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân đau ngực từng cơn khi gắng sức trong 1 tuần, không đau khi nghỉ, không ngất, có tiền sử tăng huyết áp và đang dùng amlodipine 5mg mỗi ngày.

## Must include
- Present symptom: đau ngực khi gắng sức
- Duration: 1 tuần
- Negated symptom: không ngất
- Past history: tăng huyết áp
- Medication: amlodipine 5mg mỗi ngày
- Plan: đo điện tim, kiểm tra huyết áp, cân nhắc xét nghiệm theo chỉ định bác sĩ
- Red flag: đau ngực kéo dài, khó thở, vã mồ hôi cần đi cấp cứu

## Difficulty
Medium

## Expected labels
symptom, duration, negation, past_history, medication, dosage, frequency, procedure, plan, red_flag

---

# SYN_OUT_004

## Setting
Outpatient clinic

## Specialty
Endocrinology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân đái tháo đường type 2 tái khám. Đường huyết gần đây dao động, có khát nước nhiều, không hạ đường huyết, đang dùng metformin 500mg ngày 2 lần.

## Must include
- Diagnosis/history: đái tháo đường type 2
- Present symptom: khát nước nhiều
- Negated symptom: không hạ đường huyết
- Medication: metformin 500mg
- Frequency: ngày 2 lần
- Lab test: HbA1c
- Plan: tiếp tục theo dõi đường huyết, tái khám theo hẹn

## Difficulty
Medium

## Expected labels
diagnosis, symptom, negation, medication, dosage, frequency, lab_test, plan, follow_up

---

# SYN_OUT_005

## Setting
Outpatient clinic

## Specialty
Gastroenterology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân đau thượng vị sau ăn 2 tuần, ợ chua, không nôn ra máu, không đi ngoài phân đen, có dùng ibuprofen vài ngày trước.

## Must include
- Present symptom: đau thượng vị sau ăn
- Present symptom: ợ chua
- Duration: 2 tuần
- Negated symptom: không nôn ra máu
- Negated symptom: không đi ngoài phân đen
- Medication history: ibuprofen
- Plan: tránh NSAID, cân nhắc thuốc giảm tiết acid theo bác sĩ
- Follow-up: quay lại nếu đau tăng, nôn máu, phân đen

## Difficulty
Medium

## Expected labels
symptom, duration, negation, medication, past_history, doctor_instruction, plan, follow_up, red_flag

---

# SYN_OUT_006

## Setting
Outpatient clinic

## Specialty
Pulmonology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân khó thở khi gắng sức, khò khè về đêm, có tiền sử hen, không sốt, không đau ngực. Bệnh nhân dùng salbutamol inhaler khi cần.

## Must include
- Present symptom: khó thở khi gắng sức
- Present symptom: khò khè về đêm
- Past history: hen
- Negated symptom: không sốt
- Negated symptom: không đau ngực
- Medication: salbutamol inhaler
- Route: đường hít
- Frequency: khi cần
- Plan: kiểm tra kỹ thuật dùng inhaler, tái khám nếu triệu chứng tăng

## Difficulty
Medium

## Expected labels
symptom, negation, past_history, medication, route, frequency, procedure, plan, follow_up

---

# SYN_OUT_007

## Setting
Outpatient clinic

## Specialty
Dermatology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân nổi mẩn ngứa sau khi ăn hải sản, không khó thở, không sưng môi, từng dị ứng tôm. Bác sĩ dặn tránh tác nhân nghi ngờ và theo dõi dấu hiệu nặng.

## Must include
- Present symptom: nổi mẩn ngứa
- Trigger: sau ăn hải sản
- Allergy: dị ứng tôm
- Negated symptom: không khó thở
- Negated symptom: không sưng môi
- Medication: thuốc kháng histamine theo chỉ định
- Red flag: khó thở, phù môi/mặt, choáng
- Plan: tránh hải sản nghi ngờ

## Difficulty
Easy

## Expected labels
symptom, allergy, negation, medication, doctor_instruction, plan, red_flag

---

# SYN_OUT_008

## Setting
Outpatient clinic

## Specialty
Obstetrics and Gynecology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân nữ trễ kinh 6 tuần, buồn nôn nhẹ, không đau bụng nhiều, không ra máu âm đạo. Bác sĩ đề nghị test thai và siêu âm theo chỉ định.

## Must include
- Present symptom: trễ kinh 6 tuần
- Present symptom: buồn nôn nhẹ
- Pregnancy status: nghi ngờ có thai
- Negated symptom: không đau bụng nhiều
- Negated symptom: không ra máu âm đạo
- Lab/procedure: test thai
- Imaging/procedure: siêu âm
- Follow-up: quay lại nếu đau bụng tăng hoặc ra máu

## Difficulty
Medium

## Expected labels
symptom, duration, pregnancy_status, negation, lab_test, imaging, procedure, plan, follow_up, red_flag

---

# SYN_OUT_009

## Setting
Outpatient clinic

## Specialty
Otolaryngology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân đau họng 4 ngày, nghẹt mũi, không khó thở, không nuốt nghẹn, tự dùng kháng sinh còn thừa 2 viên trước khi đi khám.

## Must include
- Present symptom: đau họng 4 ngày
- Present symptom: nghẹt mũi
- Negated symptom: không khó thở
- Negated symptom: không nuốt nghẹn
- Medication history: tự dùng kháng sinh còn thừa
- Doctor instruction: không tự ý dùng kháng sinh
- Plan: điều trị triệu chứng và theo dõi

## Difficulty
Medium

## Expected labels
symptom, duration, negation, medication, doctor_instruction, plan, follow_up

---

# SYN_OUT_010

## Setting
Outpatient clinic

## Specialty
Neurology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân đau đầu âm ỉ 1 tháng, tăng khi căng thẳng, không yếu liệt tay chân, không nói khó, không co giật. Bác sĩ hỏi dấu hiệu cảnh báo thần kinh.

## Must include
- Present symptom: đau đầu âm ỉ
- Duration: 1 tháng
- Trigger: căng thẳng
- Negated symptom: không yếu liệt tay chân
- Negated symptom: không nói khó
- Negated symptom: không co giật
- Red flag: đau đầu đột ngột dữ dội, yếu liệt, nói khó
- Plan: theo dõi, tái khám nếu có dấu hiệu cảnh báo

## Difficulty
Medium

## Expected labels
symptom, duration, severity, negation, red_flag, plan, follow_up

---

# SYN_OUT_011

## Setting
Outpatient clinic

## Specialty
Orthopedics

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân đau gối phải sau khi chạy bộ, không sưng nóng đỏ, không sốt, đi lại được nhưng đau khi lên xuống cầu thang.

## Must include
- Present symptom: đau gối phải
- Trigger: sau chạy bộ
- Negated symptom: không sưng nóng đỏ
- Negated symptom: không sốt
- Functional impact: đau khi lên xuống cầu thang
- Procedure/imaging: cân nhắc chụp X-quang nếu đau kéo dài hoặc chấn thương rõ
- Plan: nghỉ ngơi, chườm lạnh, tái khám nếu đau tăng

## Difficulty
Easy

## Expected labels
symptom, negation, procedure, imaging, plan, follow_up

---

# SYN_OUT_012

## Setting
Outpatient clinic

## Specialty
Urology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân tiểu buốt 2 ngày, tiểu nhiều lần, không sốt cao, không đau hông lưng. Bác sĩ chỉ định xét nghiệm nước tiểu.

## Must include
- Present symptom: tiểu buốt 2 ngày
- Present symptom: tiểu nhiều lần
- Negated symptom: không sốt cao
- Negated symptom: không đau hông lưng
- Lab test: tổng phân tích nước tiểu
- Plan: uống đủ nước, dùng thuốc theo đơn nếu bác sĩ kê
- Follow-up: quay lại nếu sốt, đau hông lưng, tiểu máu

## Difficulty
Easy

## Expected labels
symptom, duration, negation, lab_test, plan, follow_up, red_flag

---

# SYN_OUT_013

## Setting
Outpatient clinic

## Specialty
Mental health / Psychiatry

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân mất ngủ 3 tuần, lo âu nhiều do áp lực công việc, không có ý định tự hại, không dùng rượu thường xuyên. Bác sĩ tư vấn vệ sinh giấc ngủ và hẹn tái khám.

## Must include
- Present symptom: mất ngủ 3 tuần
- Present symptom: lo âu
- Social context: áp lực công việc
- Negated risk: không có ý định tự hại
- Negated social history: không dùng rượu thường xuyên
- Plan: vệ sinh giấc ngủ, theo dõi triệu chứng
- Follow-up: tái khám theo hẹn hoặc sớm hơn nếu có ý nghĩ tự hại

## Difficulty
Hard

## Expected labels
symptom, duration, social_history, negation, red_flag, plan, follow_up

---

# SYN_OUT_014

## Setting
Outpatient clinic

## Specialty
Geriatrics

## Roles
Doctor, Caregiver, Patient

## Clinical scenario
Con gái đưa bố 78 tuổi đi khám vì hay quên tăng dần 6 tháng. Bệnh nhân tự nói vẫn sinh hoạt được, người nhà nói có quên uống thuốc huyết áp. Không té ngã gần đây.

## Must include
- Clinical subject: patient là người cao tuổi
- Speaker role: caregiver cung cấp thông tin phụ
- Present symptom: hay quên tăng dần 6 tháng
- Functional status: vẫn sinh hoạt được
- Medication adherence issue: quên uống thuốc huyết áp
- Negated event: không té ngã gần đây
- Plan: đánh giá nhận thức, rà soát thuốc, hẹn tái khám

## Difficulty
Hard

## Expected labels
symptom, duration, clinical_subject, caregiver_reported, speaker_role, medication, negation, procedure, plan, follow_up

---

# SYN_OUT_015

## Setting
Outpatient clinic

## Specialty
Internal medicine

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân mệt mỏi 1 tháng, chóng mặt nhẹ, ăn kém. Không sốt, không sụt cân rõ. Bác sĩ chỉ định công thức máu và xét nghiệm cơ bản.

## Must include
- Present symptom: mệt mỏi 1 tháng
- Present symptom: chóng mặt nhẹ
- Present symptom: ăn kém
- Negated symptom: không sốt
- Negated symptom: không sụt cân rõ
- Lab test: công thức máu
- Lab test: xét nghiệm cơ bản
- Plan: đánh giá nguyên nhân thiếu máu hoặc rối loạn chuyển hóa nếu có kết quả bất thường

## Difficulty
Medium

## Expected labels
symptom, duration, severity, negation, lab_test, plan, follow_up

---

# SYN_OUT_016

## Setting
Outpatient clinic

## Specialty
Infectious disease / Internal medicine

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân tiêu chảy cấp 1 ngày sau ăn ngoài, đi ngoài phân lỏng 5 lần, không máu trong phân, không nôn nhiều, không dấu mất nước nặng.

## Must include
- Present symptom: tiêu chảy 1 ngày
- Frequency: đi ngoài 5 lần
- Trigger: sau ăn ngoài
- Negated symptom: không máu trong phân
- Negated symptom: không nôn nhiều
- Negated sign: không mất nước nặng
- Plan: bù nước, theo dõi, tái khám nếu sốt cao, phân máu, khát nhiều/li bì

## Difficulty
Medium

## Expected labels
symptom, duration, frequency, negation, plan, follow_up, red_flag

---

# SYN_OUT_017

## Setting
Outpatient clinic

## Specialty
Allergy / Immunology

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân khai từng nổi mề đay sau khi uống amoxicillin. Hiện đến khám vì viêm họng nhẹ, không sốt cao, không khó thở. Bác sĩ ghi nhận dị ứng thuốc.

## Must include
- Allergy: amoxicillin
- Allergy reaction: nổi mề đay
- Current symptom: viêm họng nhẹ
- Negated symptom: không sốt cao
- Negated symptom: không khó thở
- Doctor instruction: tránh tự dùng amoxicillin/penicillin nếu chưa được bác sĩ đánh giá
- Plan: ghi nhận dị ứng thuốc trong hồ sơ

## Difficulty
Medium

## Expected labels
allergy, medication, symptom, negation, doctor_instruction, plan, red_flag

---

# SYN_OUT_018

## Setting
Outpatient clinic

## Specialty
Family medicine

## Roles
Doctor, Patient

## Clinical scenario
Bệnh nhân tái khám sau điều trị viêm phế quản. Ho đã giảm, không sốt, còn mệt nhẹ. Bác sĩ đánh giá đáp ứng điều trị và dặn hoàn thành thuốc theo đơn trước đó nếu không có tác dụng phụ.

## Must include
- Follow-up encounter context: tái khám
- Improved symptom: ho đã giảm
- Negated symptom: không sốt
- Present symptom: còn mệt nhẹ
- Medication adherence: hoàn thành thuốc theo đơn trước đó
- Negated adverse effect: không có tác dụng phụ đáng kể
- Plan: theo dõi thêm, quay lại nếu ho tăng hoặc sốt lại

## Difficulty
Medium

## Expected labels
follow_up, symptom, negation, medication, doctor_instruction, plan, red_flag

---

# SYN_OUT_019

## Setting
Outpatient clinic

## Specialty
Internal medicine / Hypertension clinic

## Roles
Doctor, Patient, Nurse

## Clinical scenario
Điều dưỡng đo huyết áp 150/95 mmHg. Bệnh nhân nói quên uống thuốc 2 ngày, không đau đầu dữ dội, không đau ngực, không khó thở. Bác sĩ điều chỉnh kế hoạch theo dõi.

## Must include
- Role: nurse cung cấp vital sign
- Vital sign: huyết áp 150/95 mmHg
- Medication adherence issue: quên uống thuốc 2 ngày
- Negated symptom: không đau đầu dữ dội
- Negated symptom: không đau ngực
- Negated symptom: không khó thở
- Plan: theo dõi huyết áp tại nhà, dùng thuốc đúng hướng dẫn, tái khám

## Difficulty
Hard

## Expected labels
vital_sign, speaker_role, symptom, negation, medication, dosage, plan, follow_up, clinical_subject

---

# SYN_OUT_020

## Setting
Outpatient clinic

## Specialty
Pediatrics

## Roles
Doctor, Caregiver, Patient

## Clinical scenario
Bố đưa bé 4 tuổi đi khám vì nổi ban và sốt. Bố nói bé đã uống paracetamol 250mg, hết sốt tạm thời. Bé không khó thở, không nôn ói, chưa ghi nhận dị ứng thuốc.

## Must include
- Clinical subject: patient là trẻ 4 tuổi
- Speaker role: caregiver nói thay bệnh nhân
- Present symptom: nổi ban
- Present symptom: sốt
- Medication: paracetamol 250mg
- Dosage: 250mg
- Response: hết sốt tạm thời
- Negated symptom: không khó thở
- Negated symptom: không nôn ói
- Allergy: chưa ghi nhận dị ứng thuốc
- Follow-up: quay lại nếu ban lan nhanh, sốt cao, khó thở, li bì

## Difficulty
Hard

## Expected labels
symptom, medication, dosage, allergy, negation, clinical_subject, caregiver_reported, speaker_role, plan, follow_up, red_flag

---

## 5. Coverage Summary

| Coverage area | Covered by cases |
|---|---|
| Basic symptom extraction | SYN_OUT_001, 005, 010, 011, 012, 015 |
| Negation detection | SYN_OUT_001, 003, 005, 006, 010, 012, 016 |
| Medication extraction | SYN_OUT_001, 003, 004, 006, 017, 020 |
| Dosage extraction | SYN_OUT_001, 003, 004, 020 |
| Route/frequency | SYN_OUT_004, 006 |
| Allergy | SYN_OUT_001, 007, 017, 020 |
| Vital signs | SYN_OUT_019 |
| Lab tests | SYN_OUT_004, 012, 015 |
| Imaging/procedure | SYN_OUT_008, 011 |
| Caregiver attribution | SYN_OUT_002, 014, 020 |
| Nurse role | SYN_OUT_019 |
| Follow-up / red flag | Most cases |
| Mental health safety language | SYN_OUT_013 |
| Pediatric outpatient | SYN_OUT_002, 020 |
| Geriatric outpatient | SYN_OUT_014 |

---

## 6. Annotation Notes for Later Weeks

Khi chuyển từ outline sang full synthetic dialogue, mỗi case nên sinh thêm:

```text
1. full_dialogue.md
2. transcript_segments.jsonl
3. clinical_facts.jsonl
4. soap_lite_draft.json
5. doctor_review_gold.json
6. audit_review_events.jsonl
```

Mỗi clinical fact bắt buộc có:

```json
{
  "fact_id": "...",
  "encounter_id": "...",
  "fact_type": "...",
  "original_text": "...",
  "normalized_text": "...",
  "assertion": "...",
  "speaker_role": "...",
  "clinical_subject": {
    "subject_type": "patient"
  },
  "source_segment_ids": ["..."],
  "doctor_confirmation_status": "pending"
}
```

---

## 7. Safety and Governance Notes

- Các case trong file này là synthetic outline, không đại diện cho chỉ định điều trị thật.
- Không dùng tên, số điện thoại, địa chỉ, mã bệnh án hoặc thông tin định danh thật.
- Không dùng audio bệnh nhân thật trong giai đoạn này.
- Không đưa case hold-out vào training nếu sau này đánh dấu `allowed_use = ["holdout_only"]`.
- Không cho phép clinical fact không có `source_segment_ids`.
- Không đánh dấu bất kỳ note/fact nào là Gold nếu chưa có doctor review/confirmation.
- Không để AI tự kết luận chẩn đoán cuối cùng mà không có bác sĩ xác nhận.
