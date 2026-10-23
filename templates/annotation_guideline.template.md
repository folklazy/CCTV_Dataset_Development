# คู่มือ annotation ทดลอง v0.1 — PROPOSED

ปรับใช้ annotation guideline template เดิมหลัง visual exploration commit c5139f4 ทุกกฎด้านล่างเป็นข้อเสนอรอมนุษย์ทบทวน การเขียนเอกสารไม่ใช่การอนุมัติ ontology/วิธีทำ mask/เกณฑ์คุณภาพ และรอบนี้ยังไม่ทำ annotation จริง

เป้าหมายที่ผู้ใช้ยืนยันคือ End-to-End หลัก, Oracle แยก, person/upper/lower/footwear masks พร้อม owner, สีบน–ล่างเมื่อภาพเอื้อ และ structured output/คำบรรยาย Attributes อื่นไม่ mandatory ดู [requirements](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md)

หลักฐานรายภาพ/Exploration IDs/locator/crop coordinates อยู่ในชุดทบทวนภายใน คู่มือ public ใช้ rule IDs เดียวกันเพื่อเชื่อมหลักฐานโดยไม่เผยแพร่ข้อมูลบริษัท ข้อค้นพบจากภาพเป็น observations ของ assistant/Codex ไม่ใช่ GT หรือ independent human review

## วิธีใช้ก่อน pilot

1. เปิด review packet ภายใน อ่าน full frame ก่อน crop แล้วเทียบ observation กับ inference และคำถาม ไม่ถือข้อเสนอ Codex เป็นคำตอบที่อนุมัติแล้ว
2. ผู้ทบทวนบันทึก choice/reason/revision ใน decision sheet; ทุกแถวเริ่ม PENDING_HUMAN_REVIEW เก็บความเห็นต่างก่อนข้อยุติ
3. เปลี่ยนกฎเป็น accepted เฉพาะเมื่อผู้ตัดสินระบุจริง พร้อมรุ่น/ผลกระทบและหลักฐาน เก็บ v0.1 เดิมไว้ หากยังไม่ชัดให้ defer ไม่เติมคำตอบสมมติ

## กฎร่างและทางเลือก

ตัวเลือก A/B/C ด้านล่างเสนอรูปแบบข้อมูลหรือ workflow ที่อยู่ภายใต้ข้อกำหนดเดียวกัน ผลกระทบของแต่ละทางเลือกเขียนกำกับไว้ ผู้ทบทวนยังแก้หรือเลื่อนคำตัดสินได้ ไม่เสนอการเติมส่วนที่ซ่อน การเดา owner หรือการรวม unknown เป็น background เป็นทางเลือก pilot

### R01 — person instance และ person mask

**คำถาม:** อะไรเป็นคนหนึ่ง instance และ person mask ครอบคลุมเท่าใด?

**หลักฐาน:** private review binding ของ R01 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: visible body + เสื้อผ้าที่สวมและ footwear เป็นฐาน; อุปกรณ์แยก มี scope เรียบง่ายแต่ต้องเก็บ refs สำหรับ view อื่น
- B: visible silhouette รวมอุปกรณ์ที่สวม/สะพาย แต่แยกสิ่งถือกับ material regions; ต้องตกลง bag/headwear inclusion และมีงานแยกชิ้นเพิ่ม
- C: เก็บ primitive body/garment/accessory layers แล้ว derive person views ภายหลัง; ยืดหยุ่นกว่าแต่ใช้เวลาและต้องตรวจ mapping เพิ่ม

**ข้อเสนอ Codex / เหตุผล:** เสนอ A เป็น working view เพื่อเชื่อม masks ขั้นต่ำกับเจ้าของ เก็บ accessory แยกเพื่อสร้าง evaluation view อื่นได้ ไม่ใช้ detector box หรือความครบทุก region เป็นตัวกำหนดว่ามี person; ตัวเลขเกณฑ์ขนาด/คุณภาพยังไม่กำหนด

**ผลต่อ annotation/evaluation:** ต้องตกลง mask scope ก่อนเปรียบเทียบพื้นที่/owner; คนขอบภาพหรือคนไกลยังมี record ได้พร้อมสถานะ ไม่ยืนยันจำนวนคนจากหัวเพียงอย่างเดียว

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

**แหล่งตั้งต้น / ขอบเขต:** MHP v2 §3.1 PDF p.4; CCIHP §2 PDF p.2: person/part scopes ต่างตาม dataset

### R02 — body / worn clothing / bag / held object

**คำถาม:** จะเก็บกระเป๋า สิ่งถือ หมวก และเสื้อผ้าซ้อนอย่างไร?

**หลักฐาน:** private review binding ของ R02 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: body/worn garments กับ associated accessories เป็นชั้นข้อมูลแยก; เชื่อม owner เมื่อมีหลักฐานและเลือก evaluation view ได้
- B: เก็บเฉพาะขอบ person/garments ที่ยืนยันได้ พร้อม accessory-overlap refs/uncertainty ก่อนทำ accessory geometry; ลดงานเสริมแต่ยัง derive silhouette รวมไม่ได้ครบ
- C: ทดลอง accessory geometry/type เพิ่มเฉพาะเคส pilot ที่กระทบขอบ person; วัดภาระก่อนตัดสิน ไม่เพิ่ม accessories เป็น mandatory ทั้งชุด

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: ผูกวัตถุกับ person เมื่อหลักฐานรองรับ และเก็บความไม่แน่ใจแยก เสื้อที่สวมกับผ้าที่ถือไม่สรุปจากสี/ความใกล้ เป้าหมาย bag/headwear inclusion ใน person view ยังรอทบทวน

**ผลต่อ annotation/evaluation:** mask ศูนย์นอก region support ไม่แปลว่าเป็น known background; pixels ของวัตถุที่แยกออกยังต้องมี validity/นโยบาย evaluation ไม่ถ่ายทอดสีกระเป๋าเป็นสี upper

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

**แหล่งตั้งต้น / ขอบเขต:** CCIHP §2 PDF p.2 รวม accessories บางอย่างใน human mask; เป็นทางเลือกของงานนั้น

### R03 — visible / occluded / truncated / partial person

**คำถาม:** ส่วนที่ไม่เห็นและคนที่เห็นไม่ครบต้องบันทึกอย่างไร?

**หลักฐาน:** private review binding ของ R03 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: visible support พร้อม occlusion/truncation/unknown แยก; คง partial person และ valid regions ทุกคนที่มีหลักฐาน
- B: เก็บ confirmed visible core กับ boundary-uncertainty support แยก; ไม่เติมส่วนซ่อน แต่เพิ่มภาระอธิบาย valid domain
- C: เก็บ partial-person record และ regions ที่ชัดทันที พร้อมคิว review เฉพาะส่วนที่ยังแยกไม่ได้; คงข้อมูลไว้แต่ความพร้อมแต่ละ task ต่างกัน

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: ไม่เติมด้านหลังสิ่งบังหรือ black region; คง partial person และ valid regions ที่สังเกตได้ ไม่ตัดทั้งคนเพราะ lower/footwear ไม่มีข้อมูล บริเวณที่ถูกปิดไม่กลายเป็น background อัตโนมัติ

**ผลต่อ annotation/evaluation:** รายงาน denominator/coverage ต่อคนและต่อ task แยกกัน; absence ต้องมีหลักฐานเชิงบวก ไม่ใช่ mask ว่างหรือไม่มี region

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

### R04 — ownership เมื่อซ้อนกัน

**คำถาม:** region หรือชิ้นผ้าที่คั่นคนสองคนเป็นของใคร?

**หลักฐาน:** private review binding ของ R04 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: image-local person ref เมื่อยืนยันได้ และ owner candidates/unknown เมื่อยังไม่ชัด; ต้องตรวจ references กับ validity แยก
- B: เก็บ unresolved visible region แยกจาก person geometries ที่ยืนยันแล้วจน adjudication; รักษาหลักฐานแต่เพิ่ม region ที่ยังผูกคนไม่ได้
- C: แยกรอบ geometry กับรอบ ownership review พร้อมเก็บผลก่อนแก้; ทำงานเป็นลำดับได้แต่เพิ่ม handoff/revision cost ไม่ถือว่ามี independent review แล้ว

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: ใช้ visible continuity/บริบทที่อธิบายได้ เก็บ owner candidates/unknown เมื่อยังแยกไม่ได้ ไม่เดาจาก category และไม่ merge เพื่อให้ export ง่าย

**ผลต่อ annotation/evaluation:** unknown owner ไม่เท่ากับ no person/background; semantic support ที่เห็นกับ owner validity เป็นคนละเรื่อง ต้องกำหนด matching/scoring domain ภายหลัง

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

**แหล่งตั้งต้น / ขอบเขต:** MHP v2 §3.1 PDF p.4: parsing plane รายคน ไม่ใช่ข้อบังคับ owner heuristic ของ CCTV

### R05 — upper/lower หลายชั้นและชิ้นเดียว

**คำถาม:** เสื้อคลุม ผ้าพาด หรือ one-piece แบ่ง upper/lower ตรงไหน?

**หลักฐาน:** private review binding ของ R05 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: visible garment surface พร้อม relation และ upper/lower mapping ที่ยัง unresolved ได้; เก็บหลักฐานก่อนแต่ยังใช้ scoring บางส่วนไม่ได้
- B: เก็บ outermost visible surfaces กับ layer relations แล้วทบทวน upper/lower projection แยก; รองรับหลายชั้นแต่ mapping/งานตรวจมากขึ้น ไม่เติม inner layer ที่ซ่อน
- C: คง one-piece/ambiguous garment extent เป็น geometry แยกและ task validity ที่รอ mapping; รักษาคน/regions อื่นได้ แต่ต้องมีหลักฐานเพิ่มก่อนประเมิน upper/lower บริเวณนั้น

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: garment ที่ชัดคง visible region ของตัวมัน เสื้อชิ้นเดียวหรือรอยต่อไม่ชัดเก็บ unresolved extent ไม่ลากเส้นแบ่งสมมติและไม่ทำ geometry ซ้ำทั้งสอง region เพื่อเลี่ยงการตัดสิน ต้องหาหลักฐาน one-piece ชัดเพิ่มก่อนกติกานี้ผ่าน pilot

**ผลต่อ annotation/evaluation:** ต้องตัดสินวิธี derive upper/lower จาก garment extent ก่อน scoring; ตอนนี้มีเพียงเคสกำกวม ไม่ได้ยืนยัน dress/coat ทุกตัว

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

**แหล่งตั้งต้น / ขอบเขต:** CCIHP §2 PDF p.2 แยก Dress เป็น UpperClothes/Skirt แต่ไม่ให้กฎขอบที่บังคับใช้กับเรา

### R06 — footwear / sandals / bare skin

**คำถาม:** เท้าเปล่า รองเท้าแตะ และเท้าที่มองไม่เห็นต่างกันอย่างไร?

**หลักฐาน:** private review binding ของ R06 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: footwear material ที่เห็นแยกจาก skin พร้อม presence/observability; แยกความหมายได้แต่ขอบ sandal อาจใช้เวลาตรวจ
- B: เมื่อแยกวัสดุไม่ได้ให้บันทึก visible foot context/locator และ pending footwear geometry; คง person/regions อื่นไว้ แต่ยังให้คะแนน footwear ส่วนนั้นไม่ได้
- C: เก็บ confirmed footwear core พร้อม boundary uncertainty และคิวทบทวน; คงหลักฐานบางส่วนแต่ต้องกำหนด validity ก่อน scoring ไม่เรียกส่วนที่ไม่เห็นว่า absent

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: รองเท้าแตะเก็บเฉพาะวัสดุที่เห็นและแยก skin ตามขอบที่ยืนยันได้ เมื่อขอบสายไม่ชัดให้บันทึก uncertainty; visible bare foot อาจรองรับ footwear absent เมื่อมนุษย์ตรวจแล้ว ไม่ใช้เท้าที่หลุดขอบเป็น absence

**ผลต่อ annotation/evaluation:** valid footwear domain ต่างจาก person domain; ไม่ตัด partial person หรือให้คะแนนถูกจากการตอบ absent เมื่อยังไม่เห็นเท้า

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

### R07 — absent / unknown / unobservable / not annotated

**คำถาม:** คำว่าไม่มี ไม่แน่ใจ มองไม่ได้ และยังไม่ทำจะเก็บแยกอย่างไร?

**หลักฐาน:** private review binding ของ R07 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: presence, observability, annotation workflow และ value state แยก fields; ความหมายชัดแต่ต้องตรวจ combinations
- B: เก็บเหตุการณ์งานและ reason records แล้ว derive state ด้วย mapping version ที่ตรวจย้อนกลับได้; ลดการแก้หลาย field แต่ระบบ derived view ซับซ้อนขึ้น
- C: ใช้ state objects แยกตาม person/region/attribute และบันทึกความหมายเต็มตอน export; โครงสร้างละเอียดขึ้นแต่ไม่ flatten unknown/unobservable/not_annotated/absent เป็นค่าเดียว

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: absent คือมีหลักฐานว่า target ไม่มี; unknown คือข้อสรุปยังไม่แน่; unobservable คือภาพไม่รองรับการอ่าน; not_annotated เป็นสถานะงาน ไม่ใช่ความจริงของภาพ applicability อีกแกนหนึ่ง ไม่บังคับค่า inferred ให้เต็ม

**ผลต่อ annotation/evaluation:** ignore เป็นนโยบาย evaluation ที่ต้องมี policy ref แยกจาก annotation state; JSON/validity export ต้องรักษาความต่าง ไม่เติม absent/background เป็น default

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

**แหล่งตั้งต้น / ขอบเขต:** Cityscapes §2.2 PDF p.3: unclear ใช้ void ในงานนั้น; โครงการเสนอ state แยก ไม่ยก void code มาใช้

### R08 — สีที่ปรากฏ หลายสี หลายชั้น

**คำถาม:** จะตอบสีบน–ล่างอย่างไรเมื่อมี cast/หลายชั้น/อ่านไม่ชัด?

**หลักฐาน:** private review binding ของ R08 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: apparent color ต่อ visible region/ชั้น พร้อม value state/reason; รองรับเป้าหมายสีโดยไม่เดาสีจริงและต้องมีหลักฐาน
- B: เก็บคำบรรยายสีที่เห็นกับ support refs ก่อน mapping สู่ vocabulary รุ่นทดลอง; เลื่อนการตรึงชื่อสีได้แต่ยังเทียบ categorical score โดยตรงไม่ได้
- C: เก็บชุด apparent colors แบบไม่บังคับ dominant color ต่อ visible layer พร้อมเหตุผล unknown; รองรับหลายสีแต่ต้องทดสอบวิธี matching และยังไม่ตรึงจำนวนสี

**ข้อเสนอ Codex / เหตุผล:** เสนอ A ตามเป้าหมายระบบ: เมื่อเห็นให้บันทึก apparent color/หลายบริเวณที่มีหลักฐาน ถ้าเห็นแค่ความสว่างให้ระบุข้อจำกัด ไม่ตีเป็น hue ที่ไม่ทราบ เก็บหลายสี/ชั้นแบบ relation โดยไม่กำหนดจำนวนสี palette หรือ boundary; unknown พร้อมเหตุผลเมื่อมองไม่ได้

**ผลต่อ annotation/evaluation:** สี display ของ mask เป็น UI metadata ไม่ใช่สีเสื้อ; การไม่มีคำตอบสีไม่ลบ geometric support และคำบรรยายต้องคง uncertainty

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

**แหล่งตั้งต้น / ขอบเขต:** CCIHP §2 PDF p.2 แยก semantics กับ color characteristics; จำนวนสีของ paper ไม่ใช่ requirement ของ CCTV

### R09 — source black region และ embedded overlay

**คำถาม:** จะจัดการพื้นที่ดำ/ตัวอักษร/กรอบที่ฝังมาแล้วอย่างไร?

**หลักฐาน:** private review binding ของ R09 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: คง source/provenance พร้อม validity และ artifact refs แยก; ไม่ใช้ black/overlay เป็น GT หรือเติมข้อมูลที่ถูกปิด
- B: เสนอ geometry ของบริเวณข้อมูลเสียที่ระบุได้ใน pilot พร้อม task-specific validity; รายละเอียดมากขึ้นแต่เพิ่มงานและต้องตรวจเครื่องมือก่อน
- C: เริ่มจาก flags/reason ต่อ person/region และ source-artifact refs แล้วค่อยทบทวน pixel-domain policy; ลดงานเริ่มต้นแต่ยัง scoring บริเวณกำกวมไม่ได้ ไม่ตัดทั้งคนโดยอัตโนมัติ

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: ส่วนที่ถูกปิดไม่มีหลักฐานให้เติมเป็นคนหรือ background ไม่ใช้ detection box/text เป็น person/part annotation และยัง annotate ส่วนที่เห็นจริงของคนได้ตามกติกาที่มนุษย์ทบทวน

**ผลต่อ annotation/evaluation:** evaluation domain ต้องระบุส่วนเสียข้อมูลและรายงาน coverage; overlay อาจทับคนบางส่วน ไม่ควรใช้แค่ image-wide reject โดยไม่พิจารณา task

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

### R10 — blur และ ghosting

**คำถาม:** ขอบนุ่มหรือมีรอยซ้ำหลายชั้นควรเลือกขอบไหน?

**หลักฐาน:** private review binding ของ R10 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: confirmed visible support พร้อม uncertain boundary และ human adjudication; ยังต้องทดสอบวิธีทำขอบ ไม่ใช้ threshold สากล
- B: ทดลอง inner-confirmed/outer-possible boundary bracket เฉพาะ pilot; แสดงความไม่แน่ใจได้แต่เพิ่ม geometry สองชุดซึ่งยังไม่ใช่ final mask
- C: single visible-support draft พร้อม boundary-uncertainty notes/review queue; format ง่ายกว่าแต่ต้องทดสอบ repeated review ก่อนกำหนด scoring domain ไม่มี generative enhancement

**ข้อเสนอ Codex / เหตุผล:** เสนอ A เป็นกฎร่าง ยังไม่เลือก numeric blur threshold หรือวิธีตัดขอบสากล รอยซ้ำไม่ใช่หลาย person instances โดยอัตโนมัติ ไม่ใช้ enhancement เติมรายละเอียด

**ผลต่อ annotation/evaluation:** decode pass ไม่รับรอง boundary accuracy; pilot ต้องทดสอบความเข้าใจ/เวลาและบันทึกการแก้กฎก่อนวัด agreement

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

### R11 — Person ID / locator / provenance

**คำถาม:** ID คนภายในภาพและ locator สำรวจเชื่อมอย่างไร?

**หลักฐาน:** private review binding ของ R11 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: annotation person ID ใหม่ภายในภาพพร้อม temporary locator_ref และ provenance แยก; ตรวจ remap refs ทุก revision
- B: opaque UUID ภายในภาพกับ display order แยก; ลดการชน ID แต่ชื่อยาวและต้องมี mapping ที่มนุษย์อ่านได้
- C: local keys จาก reviewed candidate inventory พร้อม explicit remap เมื่อ split/merge; ทำซ้ำได้แต่ต้องเก็บ revision log ไม่ใช้ detector/category เป็น identity

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: person ID ไม่ยืนยันบุคคลข้ามภาพ เก็บ locator_ref/source/hash/guideline/annotation revision แยก ไม่เขียนทับ observation เดิม owner unresolved ไม่สร้าง person ปลอมมาเติมช่อง

**ผลต่อ annotation/evaluation:** การย้ายชื่อ ID ต้อง remap refs ครบ; exact duplicate records ยังมี provenance/exposure ของแต่ละ record ไม่มี Final Test assignment ในขั้นนี้

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

### R12 — geometry และการคืนพิกัด

**คำถาม:** crop/resize/padding และ orientation คืนพิกัดอย่างไร?

**หลักฐาน:** private review binding ของ R12 เชื่อม Exploration IDs/locator และข้อจำกัดที่ตรวจแล้ว; ไม่ใช้ metadata/category แทนการดูภาพ

**ทางเลือก:**

- A: geometry master ใน original encoded-pixel frame พร้อม explicit transform chain; คืนพิกัดตรวจง่ายแต่ต้องรองรับในเครื่องมือ
- B: เก็บ native crop coordinates กับ transform chain แล้ว export canonical geometry สู่ภาพต้นฉบับ; ใช้ crop workflow ได้แต่ต้องผ่าน inverse/roundtrip checks และคง native evidence
- C: ทำบน original canvas โดย zoom เพื่อแสดงผลเท่านั้นและตรวจ export dimensions/IDs; ลด resize transforms แต่ขึ้นกับ GUI และยังต้องตรวจ format จริง

**ข้อเสนอ Codex / เหตุผล:** เสนอ A: เก็บ original width/height/orientation และ crop rectangle, scale_x/y, padding หรือ affine matrix; display crop ไม่ใช่ GT bbox ตรวจ inverse จุดอ้างอิงและใช้ nearest-neighbor เฉพาะ label raster ไม่อ้างว่าการย่อแล้วขยายคืนรายละเอียดเดิมได้

**ผลต่อ annotation/evaluation:** dimensions/pixel IDs/owner refs ต้องผ่าน structural check ก่อน pilot; transform correctness ทางคณิตศาสตร์ไม่พิสูจน์ boundary correctness ของ annotation

**สถานะ:** PROPOSED_PENDING_HUMAN_REVIEW

## ความหมาย state ฉบับเสนอ

| แกน | ค่าตัวอย่างในร่าง | ข้อจำกัด |
| --- | --- | --- |
| presence | present / absent / unknown | absent ต้องมีหลักฐาน ไม่ใช่ region หายหรือ mask ว่าง |
| observability | observable / partial / unobservable / unknown | ไม่บังคับข้อมูลครบทุก region เพื่อคง person record |
| annotation workflow | not_annotated / draft / reviewed / needs_revision | reviewed ต้องมี reviewer จริง ไม่ได้เกิดจาก checksum/synthetic test |
| applicability/value | applicable / not_applicable / unknown และ known / unknown / unobservable | แยกไม่เกี่ยวข้องกับตัดสินไม่ได้ |
| evaluation disposition | UNDECIDED; include/ignore/exclude เมื่อมี policy | ไม่ใช้ unknown เป็น background/absent/ignore โดยเงียบ ๆ |

## แหล่งต้นฉบับที่ตรวจเฉพาะประเด็น

- [MHP v2 paper v3](https://arxiv.org/pdf/1804.03287v3), §3.1 PDF p.4: parsing masks รายคน; background ใน plane นั้นไม่ได้กำหนด global scene unknown policy ของเรา
- [CCIHP v1](https://arxiv.org/pdf/2201.09594v1), §2 PDF p.2: person/accessory scope และ semantic/characteristic เปลี่ยนจาก CIHP ได้; ไม่คัดลอกจำนวนสีหรือกฎ Dress split มาใช้ตรง ๆ
- [Cityscapes v2](https://arxiv.org/pdf/1604.01685v2), §2.2 PDF p.3: unclear/void และ coverage ของงานนั้น; ร่างนี้เสนอ state แยกและยังไม่เลือก ignore code/threshold

ไม่ทบทวน literature ทั้งชุดซ้ำ ไม่อ้าง ISO conformance หรือว่าข้อเสนอข้างบนเป็นมาตรฐานจากแหล่งเหล่านี้ แหล่งอ้างอิงไม่แทนการทดสอบกับผู้ทำและข้อมูลจริง

## Schema / pilot / สิ่งที่ยังขาด

อ่าน [schema ร่าง](../docs/DATA_DICTIONARY_TH.md) และ [แผน pilot](quality_review.template.md) คู่มือยังไม่มี numeric class IDs, palette หรือ threshold ที่อนุมัติ เคส one-piece ชัดเจน footwear หลายมุม และ known modality ยังเป็นช่องว่าง ต้องเสนอรอบสำรวจเฉพาะจุดภายหลัง ไม่เปิดภาพใหม่ในรอบจัดคู่มือนี้
