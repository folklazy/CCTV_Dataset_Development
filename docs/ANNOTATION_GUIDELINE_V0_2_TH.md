# ทำ annotation CCTV: คู่มือสั้นสำหรับผู้ทำ

อัปเดต 5 พฤศจิกายน 2026 — **ข้อเสนอปฏิบัติสำหรับ pilot24 ยังไม่ freeze GT** ใช้ภาพที่คัดไว้2,200ภาพ ขั้นที่ทำเสร็จคือรับไฟล์และวัดสถิติภาพ; ยังไม่ได้วัดระยะ/ขนาดคนครบชุดหรือสร้าง annotationจริง

## ทำตามนี้ 6 ข้อ

1. **ดูภาพเต็มก่อน:** ตรวจทุกคนที่ยืนยันได้ รวมคนเล็ก คนนอน คนคลาน และคนที่โมเดลไม่พบ ไม่คัดคนตามกรอบYOLO
2. **ให้โมเดลร่าง แล้วตรวจแก้:** ใช้SAM3ที่เตรียมไว้ช่วยสร้างmask; คุณแก้ขอบ/คลาส/เจ้าของก่อนรับ ไม่ใช้คะแนนโมเดลเป็นการรับรองGT
3. **ทำ4ส่วนที่เห็น:** Hair=ผมศีรษะ, Face=ใบหน้าไม่รวมคอ, Upper=เสื้อผ้าบน, Lower=เสื้อผ้าล่าง ไม่เติมส่วนที่ถูกบัง หมวก/ของถือไม่ใช่เสื้อผ้าสี่ส่วน ชุดชิ้นเดียวคร่อมบนล่างเก็บเป็น cross-zone ไม่ตัดเอวเดา
4. **ไม่ชัดให้บอกไม่ชัด:** แยกถูกบัง/หลุดขอบ/ไม่แน่ใจ/ยังไม่ได้ตรวจ ไม่เปลี่ยนเป็นไม่มีคนหรือไม่มีส่วนร่างกาย และไม่ลบคนทั้งคนเพราะประเมินได้บางส่วน
5. **สีดูจากภาพจริง:** ใช้สีที่เห็นบนเสื้อผ้า ไม่อ่านจากoverlay; มองไม่พอให้unknownพร้อมเหตุผล ไม่ใช้ดำแทนunknown
6. **รับหลังตรวจและเปิดกลับได้:** maskทุกชิ้น/รู/ownerต้องอยู่ครบ เก็บรุ่นก่อนแก้และผู้ตรวจ สคริปต์ตรวจขนาดกับไฟล์ให้เอง คุณไม่ต้องกรอกตัวเลขพิกเซล

ขอบหู หนวดเครา แว่น และขอบคลุมเครือยังต้องปิดเป็นworking ruleจากตัวอย่างก่อนpilot ไม่เปลี่ยนคำจำกัดความเพื่อให้ตรงโมเดลใด รายละเอียดเดิมอยู่ภาคผนวกด้านล่าง

## “ระยะ” และความครอบคลุม

ใช้ **ขนาดที่คนปรากฏในภาพ** เป็นข้อมูลหลัก ระยะเป็นเมตรยังไม่ทราบหากไม่มีcamera calibration/ข้อมูลตำแหน่งอ้างอิง ภาพคนเล็กอาจมาจากการย่อภาพ คนย่อตัว หรือถูกบัง จึงไม่ตั้งว่าเล็ก=ไกลโดยอัตโนมัติ

| ตรวจเรื่องอะไร | สิ่งที่เก็บและนำไปใช้ |
| --- | --- |
| คนเล็ก–ใหญ่ | หลังตรวจmask คำนวณกว้าง/สูงของvisible bbox, พื้นที่mask และสัดส่วนต่อภาพ เก็บทั้งสองแกนเพื่อไม่ทำให้คนนอนดูเล็กเพราะใช้ความสูงอย่างเดียว |
| รายละเอียด4ส่วน | วัดพื้นที่Hair/Face/Upper/Lowerแยกรายคน คนตัวใหญ่อาจมีFaceเล็กหรือถูกบังได้ |
| คนซ้อน/สิ่งบัง/หลุดขอบ | ระบุสภาพที่เห็นและส่วนที่ได้รับผล ไม่ประมาณเปอร์เซ็นต์ตัวเต็มที่ซ่อน |
| เบลอ/แสง | เก็บความเบลอ แสงมืด ย้อนแสง glare และขาวดำ จากภาพจริง; timestampไม่ยืนยันสภาพแสงหรือIR |
| มุมและท่าทาง | ครอบคลุมหน้า/หลัง/ข้าง มุมสูง และยืน/นั่ง/ก้ม/นอน/คลานตามที่พบจริง ไม่บังคับให้ข้อมูลมีทุกเคส |
| สิ่งปน/เสื้อผ้ายาก | ตรวจกรอบหรือข้อความฝัง พื้นที่ดำ เงาสะท้อน เสื้อซ้อนและชุดคร่อมบนล่าง |

ตารางนี้เป็นรายการค้นหาช่องว่าง ไม่ใช่คำอ้างว่าชุด2,200มีครบทุกกรณี ใช้ภาพตัวอย่างเดิมที่identityตรงช่วยเลือกpilot เก็บเหตุผลต่อภาพและรายงานกรณีที่ยังไม่พบ ไม่เพิ่ม/ตัดสมาชิกเงียบๆ

ไม่ตั้งระยะ3/5/10เมตรหรือเกณฑ์ตัดคนเล็กขึ้นเอง เก็บค่าขนาดต่อเนื่องก่อน หากจะรายงานกลุ่มขนาดให้ประกาศcutoffsจากข้อมูลGTก่อนดูผลโมเดล และแสดงจำนวนGT/valid pixelsทุกกลุ่ม [COCO](https://cocodataset.org/dataset/detection-eval.htm) มีการรายงานตามพื้นที่mask แต่เกณฑ์ขนาดของCOCOไม่ใช่ระยะเป็นเมตรหรือกฎคัดภาพของโครงการเรา

## ใช้โมเดลอะไรช่วยร่าง

**แนะนำSAM3เป็นตัวช่วยร่างหลักที่มีอยู่แล้ว** ใช้text/box promptsตามที่adapterรองรับ [sourceทางการ](https://github.com/facebookresearch/sam3) อธิบายpromptable segmentation; SAM3ไม่ใช่parserที่รับรองคำตอบHair/Face/Upper/Lowerของเราโดยอัตโนมัติ จึงต้องตรวจsemantic classและownerเอง

เลือกเครื่องมือคนละตัวกับระบบที่จะbenchmarkเพื่อแยกบทบาทการร่างจากผู้เข้าสอบ แต่คำว่า“คนละarchitecture”ไม่รับรองความเป็นอิสระ: SAM3และparserบางตัวอาจมีส่วนประกอบแบบTransformerหรือข้อมูลฝึกเกี่ยวข้องกัน เรายังไม่ได้พิสูจน์training-data independence ไม่จำเป็นต้องเพิ่มอีกหลายโมเดลก่อนทราบfailureจริง

ใช้full-frameค้นหาคนก่อน และเมื่อคนเล็กให้ใช้cropจากพิกเซลต้นฉบับที่มีcontextพร้อมtransformกลับภาพเดิม หากโมเดลพลาดให้คนเพิ่มbox/promptหรือวาดแก้ ไม่ใช้YOLOเป็นgateของGT ไม่ใช้super-resolutionสร้างรายละเอียดมารับเป็นคำตอบ เก็บprompt/crop/config/จำนวนcallsและraw masks; zoom/cropไม่ได้กู้ข้อมูลที่ไม่มีในภาพ

ป้องกันการตามร่างโมเดลโดยคง6ภาพที่ผู้ใช้ทำก่อนเห็นAI draftไว้ตามแผนเดิม ตรวจmissed personsและพื้นที่ที่โมเดลไม่เสนอด้วย ทุกภาพต้องผู้ใช้ตรวจรับ ไม่เรียกAIตรวจซ้ำว่าindependent human agreement

**ความพร้อมจริง:** local X-AnyLabeling-Server revision `8330c45f4d47f62588122e462ac3eb7e0a2e6f46` มีweights SAM3 แต่adapterยังใช้external contour+largest component; ต้องเก็บraw masksก่อนแปลง ตรวจholes/disconnected components และdesktoproundtripก่อนpilot พบglobal BF16 autocast/CPU fallbackในloader จึงยังต้องปิดeffective precision/device readinessบนT4 ไม่รับรองว่ารันพร้อมจากไฟล์weightsอย่างเดียว รอบนี้ไม่ได้รันโมเดลเพิ่มหรือดาวน์โหลด

## Pilot เป็นงานจริงที่นำไปใช้ต่อได้

Pilot24คือ **ลองannotateจริง** เพื่อวัดความถูกต้องของเครื่องมือ กติกา และเวลาที่ใช้ ไม่ใช่แค่plotกราฟ ภาพที่แก้จนผ่านใช้ต่อใน2,200และreleaseแรก300ได้โดยรักษาIDs/source hashes/annotation revisions ไม่ทำซ้ำเพราะเปลี่ยนbatch

ผลที่ต้องได้คือ original references, masksสี่ส่วนและperson support/owner, validity, สีพร้อมสถานะ, ร่างก่อนแก้/ผลหลังแก้ และreview receipt เก็บเวลาสร้างร่าง/เวลาแก้จริงเพื่อประมาณงานที่เหลือ ถ้ากฎเปลี่ยนให้reopenเฉพาะส่วนที่ได้รับผล เก็บpilotเป็นdevelopment exposure ไม่เรียก24ภาพนี้ว่าunseen test และไม่ใช้มันสรุปคุณภาพทั้งdataset

**เครื่องมือที่เพิ่มแล้ว:** [annotation_scale.py](../scripts/annotation_scale.py) อ่านbinary maskที่มีอยู่และคืนJSONขนาด/พื้นที่โดยไม่แก้ไฟล์ ใช้ได้ทั้งpersonและแต่ละtarget แยกstage `draft` / `human_reviewed`; stageเป็นprovenanceที่ผู้เรียกระบุ ไม่ใช่การรับรองโดยโปรแกรม

```bash
python scripts/annotation_scale.py --mask person.png --width 1920 --height 1080 --stage human_reviewed
```

ใช้Pythonที่มีPillowเดิม; width/heightต้องมาจากภาพต้นฉบับ maskว่างให้extent=nullและarea0 ไม่สรุปว่าperson/targetไม่มี ระยะเมตรยังnull; ต้องส่งเฉพาะmaskbinaryไม่ใช่overlayหรือmulticlass PNG ผลทดสอบสังเคราะห์4กรณีผ่าน ไม่ใช่ผลวัดขนาดของคนจริงทั้งชุด

**งานถัดไป:** ปิดworking rulesที่ค้างและlossless bridge → เลือกpilot24ตามcoverageที่สังเกตจริง → ร่าง/ตรวจ/แก้ → reuseผลที่ผ่านและทำต่อเป็นbatches ไม่เพิ่มงานเว็บ

<details>
<summary>ภาคผนวก: กติกาและรายละเอียดร่างเดิม สำหรับผู้พัฒนาและเคสกำกวม</summary>

# คู่มือ annotation CCTV ฉบับร่างสำหรับทดสอบ

> ขอบเขตที่ผู้ใช้ยืนยัน: Hair / Face / Upper / Lower และสีเสื้อผ้าบน–ล่าง ใช้ pilot24 ข้อเสนอ six core/pilot60 เป็นประวัติ ไม่ใช่รายการ target บังคับของงานนี้

เวอร์ชัน `0.2-PROPOSED` วันที่ 5 พฤศจิกายน 2026 กำหนด working rules สำหรับทดลองหลังผ่าน intake, coverage และเครื่องมือ ชื่อ targets และขนาด pilot ได้รับการยืนยันแล้ว แต่ขอบเขตละเอียดของแต่ละ target, IDs และการจัดกรณีกำกวมยังต้องทดลองและบันทึก decision ก่อน freeze ontology ไม่มีข้อความใดรับรองว่าได้สร้าง masks จริงแล้ว

## ข้อมูลหลักและตัวตน

เก็บ lossless binary masks ต่อ person/region ใน original encoded-pixel coordinates พร้อม JSON สำหรับ IDs, owner, states, attributes, relations, evidence และ revisions ภาพ/annotations จริงอยู่นอก repository ไม่บันทึก RGB ของสีแสดง mask เป็น semantic IDs หรือสีเสื้อผ้า

image-local person ID แยกจาก detector order, temporary locator และ metadata category คนหนึ่งอาจมี visible support หลายชิ้นจากสิ่งบังซึ่งยังเป็น person เดียวได้เมื่อมีหลักฐาน Owner ที่ยังไม่ชัดใช้ null พร้อม candidates/reason ไม่แจก owner จากความใกล้ที่สุดหรือสร้าง person ปลอม

## ข้อเสนอคลาสและขอบเขต

| Target key | ชื่อ | รวมตามกฎร่าง | ไม่รวมและวิธีจัดกรณีกำกวม |
| --- | --- | --- | --- |
| Hair | Hair | เส้นผมบนศีรษะที่มองเห็นและแยกจากสิ่งบังได้ | หมวก ผ้าคลุม เงา ฉากหลัง และผมที่ซ่อน; facial hair เป็นประเด็นต้องตัดสินใน pilot |
| Face | Face | บริเวณใบหน้าที่มองเห็นและมีขอบรองรับ | ผม คอ หมวก หน้ากากหรือสิ่งบัง; ขอบหู/ช่องตา/แว่นต้องมี decision ใน pilot ก่อน freeze |
| Upper | Upper | เสื้อผ้าสวมช่วงบนที่เห็น รวมหลายชั้นตาม visible support | ผิวกาย กระเป๋า ของถือ และส่วนที่ถูกบัง; ชุดต่อเนื่องข้ามตัวใช้ A04 |
| Lower | Lower | กางเกง กางเกงขาสั้น กระโปรง หรือเสื้อผ้าช่วงล่างที่เห็น | ผิวขา ถุงเท้า รองเท้า และวัตถุอื่น; ไม่เดาขอบใต้สิ่งบัง |

ใช้ target keys เป็น semantic identifiers ชั่วคราว ไม่ใช้เลขเดิมของ six core แทนโดยอัตโนมัติ Person IDs และ visible person support เป็นโครงสร้างเจ้าของ ไม่ใช่ target ที่ห้า รองเท้า ผิวกาย cross-zone garments และ associated objects เก็บเป็นบริบท/uncertainty ได้ ไม่เพิ่มเป็นคลาสประเมินบังคับ การเปลี่ยนความหมายต้องขึ้น ontology revision และทบทวนรายการที่ได้รับผล

## กฎที่ใช้ต่อหนึ่ง person

| Rule | นิยามและวิธีทำ | เมื่อไม่แน่ใจ | ตัวอย่างสมมติและผลต่อการแก้ |
| --- | --- | --- | --- |
| A01 visible person | รวม visible body และสิ่งสวมบนร่างกาย/headwear/footwear; แยก bag/held equipment | เก็บ confirmed support และ uncertainty refs ไม่เติมส่วนที่ถูกบัง | DEMO_A ถูกเสาบังมี mask สองชิ้น; ห้ามทิ้งชิ้นเล็กเพื่อให้ polygon เดียว |
| A02 partial person | คนขอบภาพหรือเห็นบางส่วนยังมี record; annotate targets ที่รองรับ | แยก truncated กับ occluded และ presence unknown | DEMO_B เห็นครึ่งตัว ไม่ตั้ง lower absent จากการหลุดขอบ |
| A03 visible layers | แต่ละ valid pixel ให้ topmost material ที่เห็น; เก็บ relation ของชั้นที่มีหลักฐาน | ไม่วาด inner layer ใต้ outer; garment identity อาจ unknown | DEMO_C jacket เปิดเห็น shirt บางส่วนมี visible regions แยก |
| A04 cross-zone | เก็บ extent ของ garment ต่อเนื่องเมื่อยืนยันได้ | upper/lower projection unresolved หากไม่มีขอบรองรับ | DEMO_D เสื้อคลุมยาว ห้ามแบ่งตามสัดส่วนเอวคงที่หรือคัดทั้ง mask ซ้ำให้สอง class |
| A05 outside vocabulary | ของสวมที่รู้ว่าเป็น socks/gloves ยังเป็น person support ได้ | semantic_assignment=outside_core_vocabulary พร้อมชนิด/เหตุผล ต่างจาก unknown | DEMO_E sock ไม่ย้ายไป footwear/skin และไม่ทิ้งเป็น scene background |
| A06 associated object | geometry auxiliary เฉพาะที่มีผลต่อ person boundary/owner/color | เก็บ owner unknown ถ้าบอกไม่ได้ว่าสัมพันธ์กับคนใด | DEMO_F ผ้าถือสีเดียวกับเสื้อ ยังต้องแยกจาก worn garment |
| A07 uncertain boundary | เก็บขอบที่ภาพรองรับและ uncertainty support/reason ตาม format ที่ทดสอบแล้ว | ส่งกลับ native review; ห้าม enhancement สร้างรายละเอียด | DEMO_G motion trail ไม่สร้าง person instance เพิ่มเอง |
| A08 source loss | กรอบ text blackout เป็น source-artifact refs และ validity | ไม่เติมคนใต้พื้นที่ดำหรือถือกรอบเดิมเป็น GT | DEMO_H overlay ทับแขน เก็บส่วนที่ยังเห็นและเหตุผลข้อมูลหาย |

Person support กับ union ของ Hair/Face/Upper/Lower ไม่จำเป็นต้องเท่ากัน เพราะมีผิวกาย รองเท้า หมวก และส่วนอื่นนอก targets เก็บความหมายเหล่านี้แยกจาก known scene background ไม่ลบ person pixels เพื่อบังคับให้เท่ากัน

## ความหมายของ states

- `absent` ต้องมีหลักฐานว่า target ไม่มี เช่นเห็นลำตัวเปลือยชัดสำหรับ Upper; mask ว่างหรือเห็นหัวเล็กอย่างเดียวไม่พอ
- `occluded` คือมีสิ่งบัง; `out_of_frame` คือภาพตัดส่วนออก; อาจเกิดพร้อมกันและต้องบอกส่วนที่ได้รับผล
- `unknown` คือยังตัดสินความหมายไม่ได้; `unobservable` คือภาพไม่รองรับคำตอบนั้นหลังดู evidence ที่เหมาะสม
- `not_reviewed` และ `not_annotated` เป็น workflow states ไม่มีความหมายว่าไม่มี target
- storage0 ของ binary region หมายถึงนอก region support เท่านั้น ไม่รับรอง known scene background ของทุก task

## สีบนและล่าง

ใช้ apparent visible color จาก original RGB ภายใน garment support และบันทึก region/layer refs เก็บ value_state/reason แยกจากสีแสดง masks ไม่อ่านสีจาก bag, detector overlay หรือ skin ที่ปะปน ห้ามตั้ง missing เป็นดำหรือเทา

หลายสีเก็บ components ที่มองเห็นและหลักฐาน ไม่บังคับเปอร์เซ็นต์ dominant จากที่ยังไม่วัด ภาพ grayscale หรือ cast รุนแรงอาจบันทึกความสว่าง/ความไม่แน่ใจโดยไม่เดา hue ของวัสดุ ชื่อ palette และเกณฑ์ multi-color ต้องผ่าน pilot ก่อน freeze ห้ามนำ palette ของโมเดลมาใช้เป็น GT โดยไม่พิจารณานิยาม

## ขั้นทำร่างและตรวจรับ

1. อ่าน full frame และสร้าง person opportunity inventory จากภาพจริงก่อนใช้ pseudo-labels ไม่จำกัดคนตาม detector ที่ประเมิน
2. บันทึก SAM3/model/prompt parameters และ source hashes; ผลทุกชิ้นเริ่ม draft
3. ตรวจ missed persons, duplicate persons, owner, class, boundary, holes, disconnected components และ validity แยกกัน
4. Codex checked ต้องมี receipt สำหรับ revision ที่เปิดดูจริง แล้วส่งผู้ใช้พร้อม overlay ที่สลับ original ได้
5. ผู้ใช้รับหรือแก้ทุกภาพ; เปลี่ยน revision เมื่อแก้ pixels/relations/attributes และตรวจซ้ำส่วนที่ได้รับผล
6. ส่งออก canonical masks+JSON และตรวจ roundtrip อีกครั้งก่อน accepted/release

## ตัวอย่างจริงและการเปลี่ยนกฎ

สมุดตัวอย่างจริงเก็บภายนอก Git แต่ละ rule ผูก source-version record ID, full-frame/crop evidence, observed facts, candidates, chosen decision, reviewer และ rule revision ตัวอย่าง DEMO ในคู่มือนี้ไม่มีน้ำหนักเป็น evidence ของข้อมูลจริง

การแก้กฎบันทึก before/after, reason, private evidence refs, affected classes/tasks, impact query และผล reopen รายการเก่า หากยังตกลงไม่ได้ให้คง proposed/unresolved ไม่ freeze ด้วยคะแนนโมเดลหรือเสียงส่วนใหญ่ของ agents

การแยก person กับ parts และการตรวจทวนมีแนวคิดประกอบจาก [MHP v2 §3.1](https://arxiv.org/pdf/1804.03287) และ [CIHP §3.1](https://arxiv.org/pdf/1808.00157) ส่วน 4 targets, visible scope, cross-zone และ uncertainty policy ข้างต้นเป็น working design ของโครงการนี้

ประวัติ 5 พฤศจิกายน 2026: ปรับจากข้อเสนอ six core เป็น Hair/Face/Upper/Lower ตามคำตอบผู้ใช้ ใช้ pilot24 และคงประเด็นขอบเขตที่ยังต้องทดลองไว้อย่างชัดเจน ไม่มีการแปลง annotation เก่าเพราะยังไม่เริ่มสร้าง GT ของรอบนี้

</details>
