# ทะเบียนหลักฐานและสมมติฐาน — inherited DRAFT

คงเนื้อหาหลักจาก foundation เดิม P1 หมายถึงเอกสารโครงการเดิมที่เก็บภายนอก Git; รายการที่ตรวจซ้ำรอบนี้ระบุเฉพาะในตารางทบทวนห้าแหล่งด้านล่าง แหล่งอื่นยังเป็นประวัติเดิม ไม่มี visual observations หรือผล pilot ใหม่ในรอบนี้

### ขอบเขตการตรวจต้นฉบับสำหรับหน้าโครงการ — 22 ตุลาคม 2026

ตรวจบทคัดย่อจากแหล่งผู้เขียนบน arXiv ของสองงานต่อไปนี้เพื่อรองรับคำอธิบายใน README รอบนี้ ข้อเสนอด้าน ontology/QA ของโครงการยังต้องมีหลักฐานท้องถิ่น และการตรวจบทคัดย่อนี้ไม่อัปเกรดข้ออ้างส่วนอื่นทั้งเอกสารเป็นการตรวจซ้ำแล้ว

| Source | ต้นฉบับและ locator | สิ่งที่ใช้ในหน้าโครงการ / ขอบเขต |
| --- | --- | --- |
| S03 | [Datasheets for Datasets](https://arxiv.org/abs/1803.09010), abstract | เสนอเอกสารบอก motivation, composition, collection process, recommended uses; ใช้จัดเหตุผลของ provenance/docs ไม่ใช่รับรอง annotation หรือกำหนด QA threshold |
| S04 | [Instance-level Human Parsing via Part Grouping Network](https://arxiv.org/abs/1808.00157), abstract | แยก semantic part segmentation กับการจัด parts เข้า person instances; ใช้อธิบายหน่วยงาน ไม่ยืนยันความเหมาะสมของ taxonomy/pipeline กับ CCTV ชุดนี้ |

### ทบทวนแบบเจาะจงเพื่อแผนสำรวจ — 22 ตุลาคม 2026

อ่าน PDF ต้นฉบับห้าแหล่งต่อไปนี้ เลขหน้าเริ่มหน้าแรกของไฟล์เป็น 1 ลิงก์ตรึงรุ่นเพื่อให้ตรวจ locator ได้ สิ่งในคอลัมน์ปรับใช้เป็น **ข้อเสนอของโครงการ** ไม่ใช่ข้อกำหนดจาก paper ไม่มีงานใดรับรอง taxonomy, palette, QA หรือ ISO conformance ของ CCTV นี้

| แหล่ง / locator | งานต้นฉบับระบุหรือทำจริง | ข้อเสนอปรับใช้กับ CCTV | สิ่งที่ยังต้องพิสูจน์/ข้อจำกัด |
| --- | --- | --- | --- |
| S04 [CIHP / PGN v1](https://arxiv.org/pdf/1808.00157v1), §3.1–3.2, PDF pp.6–7 | ให้ผู้ทำมืออาชีพ annotate และตรวจรอบสองแต่ละภาพ; เปลี่ยน Jumpsuit ที่พบน้อยเป็น Torso-skin; มีเกณฑ์คัดภาพและ random split ของงานนั้น | แยกการสร้างกับ review และบันทึกเหตุผล class candidates | ต้องดูความละเอียดที่ CCTV สังเกตได้/ผู้ทำจริง; ไม่ยกการคัดภาพคนเดียว/ไม่มีคน หรือ split ของ CIHP มาเป็นกฎท้องถิ่น |
| S05 [MHP v2 / NAN v3](https://arxiv.org/pdf/1804.03287v3), §3.1–3.2, PDF pp.4–5 | นับคนและสร้าง indexed parsing mask รายคน; คนอื่นเป็น background ใน mask ของคนนั้น; ตรวจ annotations ทุกภาพและแก้ข้อผิดพลาด | แยก image/person/region identity และเก็บ ownership/review trail | ต้องตรวจ overlap/อุปกรณ์/ส่วนที่แยกได้; ไม่แปล per-person background เป็น scene background หรือบังคับคลาส/จำนวนผู้ตรวจตาม paper |
| S11 [Cityscapes v2](https://arxiv.org/pdf/1604.01685v2), §2.1–2.2, PDF pp.2–3; §2.3 p.3 | ให้บริบทจาก video snippet; แยก fine/coarse annotations และ void; split ตามเมืองแทน random image split | เก็บบริบทภาพต่อเนื่องเท่าที่มีและทดสอบ grouping/leakage; รายงานสิ่งที่ ignore กับ coverage | เป็น street-scene dataset ไม่ใช่ human-part taxonomy; CCTV ต้องพิสูจน์ event/group เอง ยังไม่เลือก city/camera split หรือถือว่า void คือ background |
| S03 [Datasheets for Datasets v8](https://arxiv.org/pdf/1803.09010v8), §3–3.1 p.4; §3.2 pp.5–6 | เสนอคำถาม motivation/composition เช่นหน่วยข้อมูล sampling frame ความสัมพันธ์/สิ่งที่ขาด; ยอมให้ไม่ทราบและบางคำถามไม่เกี่ยวข้อง | บันทึก source/curation versions, intended uses, unknown และเหตุผลการเลือกข้อมูลใน provenance/release plan | ต้องมีเอกสารต้นทางและผู้รับผิดชอบตอบ ไม่สร้างคำตอบจาก template หรือเรียกเอกสารครบว่า QA ผ่าน |
| S07 [CCIHP v1](https://arxiv.org/pdf/2201.09594v1), §2, PDF p.2; ICIP 2021 | ปรับ semantic classes/instance masks จาก CIHP แยก size/color/pattern characteristics; มี Undetermined สำหรับ size ที่ถูกบัง/ตัดขอบ; human masks รวมอุปกรณ์บางอย่างที่ไม่มี semantic label | พิจารณา type แยก length/characteristics และ applicability/observability แยก owner scope | ต้องยืนยันว่า attributes จำเป็นและมองได้ใน CCTV; validity ราย attribute เป็นข้อเสนอ ไม่ใช่คำสั่งของ paper; ไม่คัดลอกสี/IDs หรืออนุมานสีวัตถุจริงจากภาพเดียว |

เข้าถึง PDF ทั้งห้าแหล่งได้; Cityscapes official PDF มีการเรียกซ้ำที่ timeout จึงใช้ author preprint v2 ที่อ่านได้ ยังไม่ตรวจ supplements/release label order ของแหล่งเหล่านี้ สถิติ/คะแนนจาก benchmark ไม่ได้เป็นหลักฐาน local reliability และไม่ได้นำมาใช้กำหนดจำนวนภาพหรือ threshold รอบนี้

## 1. วิธีอ่านและขอบเขตการทบทวน

เอกสารนี้เป็นการทบทวนแบบเจาะจงเพื่อตั้งข้อกำหนด ไม่ใช่ systematic review ที่อ้างว่าครอบคลุมงานทั่วโลก ใช้เอกสารจากผู้เขียนและองค์กรเจ้าของมาตรฐานเป็นฐาน ค้นและตรวจเพิ่มเติมเมื่อ 19 ต.ค. 2026

แยกหลักฐานสามชั้น:

- ข้อความต้นทาง: สิ่งที่ source ระบุจริง พร้อม section/page
- เหตุผลประยุกต์: การตีความว่าข้อความนั้นเกี่ยวกับโจทย์เราอย่างไร
- หลักฐานท้องถิ่น: ผลสำรวจ/pilot ของบริษัท ซึ่งยังไม่มีในรุ่นนี้

การปรากฏใน paper ไม่เท่ากับการพิสูจน์ว่าเหมาะกับ CCTV บริษัท และมาตรฐานกระบวนการไม่ใช่การรับรอง taxonomy เฉพาะของโครงการ

## 2. ทะเบียนแหล่งอ้างอิง

เลขหน้า PDF เริ่มนับหน้าแรกของไฟล์เป็น 1; หากอ้างหน้า journal จะระบุแยก

| ID | แหล่งต้นฉบับและตำแหน่ง | สิ่งที่ตรวจได้และข้อจำกัดการเข้าถึง |
| --- | --- | --- |
| S01 | ISO/IEC 5259-4:2024; หน้าเว็บ What is / FAQ | ตรวจ public scope ด้าน data quality process, labelling, evaluation และ lifecycle; ยังไม่ได้ตรวจข้อกำหนดฉบับเต็ม |
| S02 | ISO/IEC 5259-2:2024; หน้าเว็บ What is / FAQ | กรอบคุณลักษณะและ measures ของ data quality; ยังไม่ได้ทำ clause-level conformance |
| S03 | Gebru et al., Datasheets for Datasets; abstract, CACM 2021 | หลักการบันทึกแรงจูงใจ องค์ประกอบ กระบวนการรวบรวม และ intended use; ไม่ใช่ certification |
| S04 | Gong et al., Instance-level Human Parsing via Part Grouping Network, ECCV 2018; §3.1–3.2, PDF pp.6–7 | ตรวจ CIHP annotation และเหตุผลเปลี่ยน Jumpsuit เป็น Torso-skin; ไม่ได้ตรวจ archive label IDs |
| S05 | Zhao et al., Understanding Humans in Crowded Scenes: Deep Nested Adversarial Learning and A New Benchmark for Multi-Human Parsing, 2018; §3.1–3.2, PDF pp.4–5 | ตรวจ MHP v2 การ annotate รายคน คลาส และการตรวจงาน; ไม่ได้ตรวจ release assets |
| S06 | Gong et al., Look into Person: Self-supervised Structure-sensitive Learning and A New Benchmark for Human Parsing, CVPR 2017; §2, PDF v2 | ตรวจจาก PDF ที่ดาวน์โหลดไว้และหน้า arXiv; ไม่ใช่หลักฐานว่า image domain เท่ากับ CCTV |
| S07 | Loesch & Audigier, Describe Me If You Can! Characterized Instance-Level Human Parsing, ICIP 2021; §2, PDF p.2 | ตรวจโครงสร้าง CCIHP และการปรับคลาส; ไม่ใช้ปี arXiv 2022 แทนปีประชุม |
| S08 | Li et al., A Richly Annotated Pedestrian Dataset for Person Retrieval in Real Surveillance Scenarios, IEEE TIP 2019; §III-A/B, PDF pp.4–5 | ตรวจ annotation รายภาพ การบัง และ coarse body regions; งาน attribute/retrieval ไม่ใช่ dense parsing GT |
| S09 | Specker et al., UPAR: Unified Pedestrian Attribute Recognition and Person Retrieval, WACV 2023; arXiv v1 §3.2–3.3, PDF pp.4–5 | ตรวจการ harmonize attributes และกติกาสี; ยังไม่ได้ตรวจ supplement/release label order |
| S10 | ISO/CIE 11664-4:2019; CIE public scope | มาตรฐานพิกัด CIELAB และ color difference; ไม่ใช่ชื่อสีเสื้อผ้าสำหรับ CCTV |
| S11 | Cordts et al., The Cityscapes Dataset for Semantic Urban Scene Understanding, CVPR 2016; v2 §2.1–2.3, PDF pp.2–3 | ตรวจบริบท/annotation/grouped split รอบ foundation review; ไม่ใช่ human-part taxonomy |

ลิงก์ต้นฉบับ:

- S01: https://www.iso.org/standard/81093.html
- S02: https://www.iso.org/standard/81860.html
- S03: https://arxiv.org/abs/1803.09010
- S04: https://arxiv.org/pdf/1808.00157v1
- S05: https://arxiv.org/pdf/1804.03287
- S06: https://arxiv.org/abs/1703.05446 และ https://arxiv.org/pdf/1703.05446v2
- S07: https://arxiv.org/pdf/2201.09594 ; DOI 10.1109/ICIP42928.2021.9506509
- S08: https://zhangzhang80.github.io/RAP.pdf ; DOI 10.1109/TIP.2018.2878349
- S09: https://arxiv.org/pdf/2209.02522
- S10: https://cie.co.at/publications/colorimetry-part-4-cie-1976-lab-colour-space-1
- S11: https://arxiv.org/pdf/1604.01685v2

## 3. หลักฐานที่นำมาใช้ได้และสิ่งที่ยังสรุปไม่ได้

| Evidence ID | ข้อค้นพบในต้นทาง | ผลต่อโจทย์เรา (ข้อเสนอ) | ขอบเขตข้ออ้าง |
| --- | --- | --- | --- |
| E01 | S01 จัดกรอบกระบวนการคุณภาพ; S02 จัดกรอบการวัด | บันทึกกระบวนการและหลักฐาน QA ตั้งแต่ต้น | ยังอ้าง ISO compliance/certification ไม่ได้ |
| E02 | S03 เสนอ datasheet อธิบายที่มาและการใช้งาน | แยก provenance, composition, intended use และข้อจำกัด | เอกสารครบไม่พิสูจน์ label ถูก |
| E03 | S04 §3.1 มีการตรวจ annotation รอบสองทุกภาพ | แยกผู้สร้างคำตอบกับการทบทวน และเก็บการแก้ไข | ไม่ได้กำหนด universal agreement threshold |
| E04 | S04 §3.2 แทน Jumpsuit ที่พบไม่บ่อยด้วย Torso-skin | ความถี่และเป้าหมายมีผลต่อ taxonomy | ความถี่ใน CIHP ใช้แทนความถี่บริษัทไม่ได้ |
| E05 | S05 แยก parsing map รายคน ใช้ 58 foreground categories และตรวจแก้ annotation | ความเป็นเจ้าของและความละเอียดเป็นการออกแบบคนละเรื่อง | ไม่มีข้อบังคับให้ CCTV ใช้ 58 คลาส |
| E06 | S06 มี 50,462 person images และ 19 semantic parts พร้อม background | แยกโจทย์ person crop ออกจากภาพเต็ม | ไม่ใช้ผลบน crop แทนผลทั้ง pipeline |
| E07 | S07 แยกส่วนจากสี/ขนาด/ลาย; เปลี่ยนความหมายบางคลาสและเพิ่ม facial mask | พิจารณา factorized annotation และบันทึกนิยามละเอียด | จำนวน/ID ของ release ต้องตรวจแยกจาก paper |
| E08 | S08 annotate แต่ละภาพแยกกัน และใช้ coarse body regions เพราะคน surveillance เล็ก/เบลอ | กำหนดความละเอียดตาม observability | coarse regions ของ RAP ไม่ใช่ parsing mask สำเร็จรูป |
| E09 | S09 harmonize 40 binary attributes ใน 12 หมวด; ใช้ข้อมูลที่เห็นรายภาพ; ภาพที่ตัดสินสีไม่ได้บางประเภทถูกคัดออก | ต้องระบุความหมายร่วมและนโยบาย unknown | เราไม่จำเป็นต้องคัดทั้งภาพตาม UPAR; การเก็บ validity ราย attribute เป็นข้อเสนอใหม่ |
| E10 | S10 กำหนดวิธีคำนวณ CIELAB | ใช้อ้างอิงการแทนสีเชิงตัวเลขหากจำเป็น | ไม่ให้จำนวนสีหรือ boundary ของชื่อสี และไม่แก้ color cast ของกล้องเอง |

จำนวนคลาสในตารางนับตามนิยามของแต่ละ paper; ห้ามเปรียบเทียบตัวเลขโดยไม่ตรวจว่ารวม background หรือไม่

## 4. แผนผังเหตุผลของ candidate

รายการนี้เป็น “องค์ประกอบที่ควรพิจารณา” ไม่ใช่ class list ที่อนุมัติแล้ว ทุกแถวต้องเติมภาพจริงและผล pilot ก่อนตรึง

| Candidate | เหตุผลต่อการประเมิน | หลักฐานตั้งต้น | ทางเลือกและข้อเสี่ยง | การตรวจท้องถิ่น |
| --- | --- | --- | --- | --- |
| C01 Person owner | ตรวจว่าชิ้นส่วนถูกคน ไม่ใช่เพียง label ถูก | E03/E05/E07 | owner ไม่ชัดเมื่อคนซ้อน | ตรวจเคส K01/K02 |
| C02 ส่วนร่างกาย/ผิวที่เห็น กับเสื้อผ้า | แยกความผิดพลาดตามเนื้อหาที่โจทย์สนใจ | E04/E06/E07 | anatomical torso ไม่เท่ากับ torso-skin; ห้ามใช้ชื่อแทนกัน | H-01; K08 |
| C03 แขน/ขา/มือ/เท้าระดับละเอียด | วิเคราะห์รายละเอียดได้มากขึ้น | E05/E06 | ความละเอียดอาจเกินพิกเซลที่มี | H-01; K03 |
| C04 ซ้าย/ขวา | วัดความถูกต้องเชิงด้านของร่างกายเมื่อจำเป็น | E05/E06 | ต้องระบุด้านของคน ไม่ใช่ด้านภาพ; ถ้าตัดสินไม่ได้ห้ามเดา | H-02; K08 |
| C05 ชนิดเสื้อผ้าแยกจากความยาว | ไม่สูญเสียชนิดเมื่อความยาวมองไม่ครบ | E07 | นิยามชนิดและ endpoint ยังต้องชัด | H-03; K02/K08 |
| C06 สีเสื้อผ้า | รองรับการประเมินคำบรรยายสีหากอยู่ในขอบเขต | E07/E09/E10 | perceived color กับ physical color เป็นคนละ target | H-04; K04/K05 |
| C07 ลวดลาย | ใช้วัดรายละเอียดเมื่อโจทย์ต้องการ | E07 | compression อาจดูเหมือนลาย; รวมหลายลายอย่างไร | H-05; K03/K08 |
| C08 เครื่องสวมศีรษะ/หน้ากาก/แว่น/กระเป๋า | ใช้เมื่อเกี่ยวกับ output หรือคำถามวิจัย | E05/E07/E09 | หนึ่งคลาสไม่ครอบคลุมทุกวัตถุที่มีหน้าที่ต่างกัน; owner อาจกำกวม | H-01; K01/K08 |
| C09 Observability / applicability | แยกการไม่มีหลักฐานจากคำตอบเชิงลบ | E07/E08/E09 | ต้องไม่เป็นช่องให้ละเว้นภาพยากทั้งหมด | H-06; K02–K05 |
| C10 Occlusion / truncation / scale | แบ่งวิเคราะห์ความยาก | E08 และ P1 | เป็น metadata ไม่จำเป็นต้องเป็น output class | K02/K03; วัด scale ซ้ำด้วยสูตรเดียว |
| C11 Background / ignore / unannotated | กำหนดโดเมนคะแนนอย่างตรวจสอบได้ | ข้อกำหนดทางวิศวกรรมของโครงการ | ความหมายไม่เหมือนกัน; ยังไม่เลือก numeric code | ตรวจ round-trip และ denominator |

ไม่มี candidate บทบาทคนเป็น parsing label ที่อนุมัติแล้ว: P1 เดิมกล่าวถึง Category_EN ในบริบทเหตุการณ์ แต่ field ที่ตรวจได้ใน export ปัจจุบันคือ category ระดับ record ยังขาด source dictionary/event-person binding จึงยืนยัน granularity ของระบบต้นทางไม่ได้ และไม่ถ่ายทอดให้ทุกคนหรือทุกพิกเซลเสื้อผ้า

## 5. สมมติฐานที่จะทดสอบใน pilot

สมมติฐานด้านล่างเสนอโดยโครงการ แหล่งอ้างอิงให้เหตุผลตั้งต้น ไม่ใช่หลักฐานยืนยันผลลัพธ์ของบริษัท เกณฑ์ผ่านเชิงตัวเลขต้องกำหนดก่อน pilot scoring ตามงาน/ทรัพยากรจริง ไม่สร้าง threshold แล้วอ้างว่าเป็นค่ามาตรฐานสากล

### H-01 ความละเอียดของคลาส

คาดว่า ontology แบบ coarse จะมีความสม่ำเสมอสูงกว่า fine-grained ในคนขนาดเล็ก แต่ fine-grained อาจเพิ่มข้อมูลที่โจทย์ต้องใช้

- เปรียบเทียบ: coarse/fine candidates บนคนและภาพชุดเดียวกัน ครอบคลุม scale/occlusion
- วัด: confusion รายคลาส, agreement ของ label/geometry, unknown rate, เวลา และข้อมูลที่สูญเสียเมื่อรวม
- ควบคุม: คู่มือ/การฝึกผู้ทำและวิธีดูภาพ; หากทำซ้ำให้สลับลำดับหรือเว้นช่วงและบันทึก carry-over
- ผลต่อการตัดสิน: แก้นิยามก่อนพิจารณารวม; เก็บ fine class เฉพาะเมื่อความจำเป็นและ reliability รองรับ ไม่อาศัยคะแนนโมเดล final

### H-02 ซ้ายและขวา

คาดว่ากติกาด้านของบุคคลพร้อมตัวอย่าง front/back จะลด side swaps เมื่อเทียบกับคำอธิบายสั้นที่ไม่มีตัวอย่าง

- วัด: side confusion แยก front/back/profile/occluded และสัดส่วนตัดสินด้านไม่ได้
- ถ้ายังไม่น่าเชื่อถือ: พิจารณา parent class ที่ไม่แยกข้าง หรือเก็บ side validity แยก โดยระบุข้อมูลที่เสีย
- ไม่ใช้ตำแหน่งซ้าย/ขวาของภาพเป็นเฉลยด้านกายวิภาค

### H-03 ชนิดและความยาวแยกกัน

คาดว่าการแยกสอง field จะเก็บชนิดที่เห็นได้ในกรณีปลายเสื้อผ้าถูกบัง โดยไม่บังคับเดาความยาว

- เปรียบเทียบ: compound label กับ type + length + validity
- วัด: จำนวนคำตอบชนิดที่ใช้ได้, agreement, invalid combinations และเวลา
- ผลต่อการตัดสิน: หากนิยามกำกวมหรือเกิด combinations ที่ไม่มีความหมาย ให้แก้ applicability matrix ก่อนใช้

### H-04 ชุดสีและคู่มือ

คาดว่าชุดสีที่มีตัวอย่าง boundary จากกล้องจริงและกติกา unknown จะลดความสับสน โดยยังรักษา coverage ที่มีประโยชน์

- เปรียบเทียบ: ชุดสี candidate และคู่มือที่มี/ไม่มี boundary examples
- วัด: confusion คู่สี, agreement, coverage, unknown แยก RGB/low-light/grayscale
- เก็บ: target คือ observed color หรือ physical color; เงื่อนไขจอและการปรับภาพ
- ผลต่อการตัดสิน: แก้ boundary/รวมสีเฉพาะเมื่อข้อมูลและเป้าหมายรองรับ; ไม่อ้างว่า CIELAB รับรองชื่อสี
- หาก target เป็นสีวัตถุจริง ต้องมี reference acquisition/calibration เพิ่ม ไม่ใช้การเดาจาก JPEG เป็น gold standard

### H-05 ลวดลาย

คาดว่าความน่าเชื่อถือของ pattern ลดลงตามขนาด region และ compression

- วัด: agreement ตามขนาด region, ความสับสน solid/pattern และ unknown
- ทดลองกับภาพจริงที่ขนาดต่างกัน; การย่อภาพจำลองต้องรายงานแยกจากภาพกล้องจริง
- ผลต่อการตัดสิน: เก็บเป็นส่วนขยายหรือกำหนด applicability ตามหลักฐาน แทนการบังคับให้ทุก region มีลาย

### H-06 การเก็บ validity รายคุณลักษณะ

คาดว่าจะรักษาข้อมูลที่ยังใช้ได้มากกว่าการคัดทั้งภาพ เมื่อบางคุณลักษณะมองไม่ชัด

- เปรียบเทียบ: whole-image rejection กับ per-task/per-attribute validity
- วัด: coverage ของแต่ละงาน, disagreement เรื่อง validity และการกระจายภาพที่ถูกยกเว้น
- ผลต่อการตัดสิน: ใช้ validity ได้เมื่อกติกาชัดและไม่เอื้อโมเดลรายตัว; รายงาน denominator เสมอ
- unknown ที่มากขึ้นอาจเพิ่ม agreement ลวง จึงต้องดู coverage ควบคู่

## 6. รูปแบบบันทึกการตัดสินรายคลาส

ใช้ฟอร์มต่อไปนี้กับทุกคลาสที่เสนอจริง ไม่ต้องแต่งสมมติฐานใหม่ให้ทุก label หากใช้สมมติฐานร่วมกันได้

| Field | เนื้อหาที่ต้องบันทึก |
| --- | --- |
| decision_id / version / date | ตัวระบุและประวัติ |
| candidate / parent / unit | ชื่อ ความสัมพันธ์ และหน่วย annotation |
| intended_measurement | คำถามประเมินที่จะตอบ |
| source_id + locator | หลักฐานตรงและตำแหน่ง |
| source_claim | ข้อความสรุปจากต้นทางโดยไม่เติมเหตุผล |
| adaptation_rationale | เหตุผลที่นำมาใช้/ปรับให้ตรง CCTV |
| inclusion / exclusion | นิยามและกรณีขอบเขต |
| alternatives | ทางเลือกที่พิจารณาและข้อแลกเปลี่ยน |
| case_ids / pilot_ids | ภาพจริงและผลทดลอง |
| hypothesis / decision_rule | สมมติฐานร่วมและเกณฑ์ตัดสินที่กำหนดก่อนวัด |
| mapping_consequence | เทียบโมเดลได้อย่างไรและสูญเสียอะไร |
| status / decision_owner | proposed / pilot / accepted / revised / deferred พร้อมผู้ตัดสินจริง |

ตัวอย่าง trace ที่ครบเมื่อมีข้อมูล: REQ-14 → E09/E10 → C06 → H-04 → K04/K05 → ผล pilot → DEC-04
ตอนนี้ยังไม่มีผล pilot จึงจบที่ข้อเสนอ ไม่เติม accepted หรือค่าความสอดคล้องสมมติ

## 7. ช่องว่างหลักฐานที่ต้องปิด

1. ตรวจคู่มือ/release จริงก่อนคัดลอกชื่อ class, numeric ID หรือ color palette; paper กับ release อาจต่างรุ่น
2. ตรวจภาพบริษัทและ mapping ไป metadata ก่อนอ้าง coverage/observability
3. ตรวจข้อกำหนดมาตรฐานฉบับเต็มหากต้องการกล่าวอ้าง conformance; ร่างนี้ใช้เพียง public scope
4. กำหนดผู้ทำจริงและการวัด agreement; การ review หลังพูดคุยกันไม่ใช่ independent agreement
5. ตรวจ application requirements ก่อนเพิ่มสี/ลาย/ความยาวเป็นผลประเมินบังคับ
6. ตรวจ label definitions ของโมเดลที่ผ่านการคัดเลือกในขั้น mapping ภายหลัง โดยไม่ใช้ model score กำหนด ontology

## 8. เกณฑ์เลือกแหล่งเพิ่มเติม

เพิ่มงานเมื่อช่วยปิดคำถามที่ยังค้าง เช่น กติกา amodal, ภาพ thermal/IR, benchmark clothing color หรือ annotation reliability โดยบันทึก query วันค้น source ที่ตรวจ และเหตุผลรับ/ไม่รับ
ไม่นำ metric SOTA, citation count หรือจำนวนคลาสมาเป็นหลักฐานเพียงอย่างเดียวว่า taxonomy ดีที่สุด

เอกสารที่เชื่อมกัน:

- BENCHMARK_REQUIREMENTS_DRAFT_TH.md — REQ/DEC
- CASE_REGISTER_DRAFT_TH.md — K cases และข้อจำกัดข้อมูล
