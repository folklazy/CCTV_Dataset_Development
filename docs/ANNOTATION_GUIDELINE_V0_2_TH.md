# ทำ annotation CCTV: คู่มือสั้นสำหรับผู้ทำ

อัปเดต 6 พฤศจิกายน 2026 — **ข้อเสนอปฏิบัติสำหรับ pilot24 ยังไม่ freeze GT** ใช้ภาพที่คัดไว้2,200ภาพ ขั้นที่ทำเสร็จคือรับไฟล์และวัดสถิติภาพ; ยังไม่ได้วัดระยะ/ขนาดคนครบชุดหรือสร้าง annotationจริง

<a id="accepted-gt-scope"></a>
## ขอบเขต GT ที่ผู้ใช้รับรองแล้ว — 6 พฤศจิกายน 2026

**GT-SCOPE-20261106-USER-ACCEPTED:** ทำ **bbox คน + person ID ภายในภาพ + masks Hair/Face/Upper/Lower พร้อม validity** ไม่บังคับวาดหรือตรวจรับ **GT mask คนทั้งตัว** การรับรองนี้ยืนยันชนิดข้อมูลและหลักการประเมิน ไม่ใช่การ freeze ขอบคลาส/mapping/matching thresholds หรือรับรองว่า annotation/pilot ผ่านแล้ว

| ขั้น | ข้อมูลและหน้าที่ | สิ่งที่ต้องตรวจรับ |
| --- | --- | --- |
| เตรียม GT | bbox ของคนที่เห็น, person ID และ masks 4 ส่วนของคนนั้น; ส่วนที่ประเมินไม่ได้มีสถานะ/เหตุผล | ผู้ใช้ตรวจความครบและขอบเขตจริง ไม่จำกัดตามคนที่โมเดลเสนอ |
| สร้างร่าง/รันระบบ | SAM3 person mask เป็น helper draft; ตอนทดสอบ YOLO สร้าง predicted bbox/mask ของตัวเอง และ parser ใช้ RGB crop | helper/predicted mask ไม่ใช่ GT และไม่เพิ่มภาระว่าต้องตรวจรับ person mask ทั้งตัว |
| จัดเจ้าของหลัง parser | baseline pipeline ปัจจุบันใช้ predicted YOLO mask จำกัดผลรายคน เป็นส่วนหนึ่งของผลระบบ | ไม่ใช้ GT mask/GT class ช่วยเลือกหรือแก้ predictions |
| ประเมินผล | bbox GT สำหรับ detector และการจับคู่รายคนตามกติกาที่จะ freeze; GT masks4ส่วนสำหรับ parsing | domain/mapping/aggregation เดียวกันทุกระบบ นับ missed/duplicate/FP/FN ตามนิยาม |

**Person ID** เป็นเลขภายในภาพเพื่อผูก bbox และ parts ว่าเป็นของใคร ไม่ใช่ตัวตนข้ามภาพหรือ tracking คนที่2ติดมาในcropคนที่1ยังเป็นความเสี่ยงของpipeline; ถ้าผลสุดท้ายเอาเสื้อคนที่2มาผูกคนที่1 การประเมินรายคนต้องนับส่วนเกินได้จาก GT Upper ของแต่ละคน ไม่ใช่ดูเฉพาะ semantic รวมทั้งภาพ

วัด YOLO box AP/Precision/Recall และ parsing per-target IoU/Precision/Recall/F1-Dice/confusion ได้เมื่อ GT/domain ตรวจครบ ส่วน person-mask AP/IoU ทั้งตัวและ full-person-mask matching/Q แบบ CIHP เดิมไม่มีสิทธิ์รายงานจาก GT นี้ ต้องใช้ bbox-based matching ที่นิยามใหม่และผ่าน scorer acceptance; ยังไม่ได้แก้ scorer เก่าหรือเปลี่ยนผล CIHP/CCTV เดิม

สีบน–ล่างยังเป็น requirement เดิมในภาพที่ประเมินได้ เก็บ GT สี/unknown แยกจาก mask validity เพื่อประเมินสีภายหลัง การอนุมัติ scope นี้ไม่ทำให้ unknown/ส่วนไม่เห็นต้องมีคำตอบหรือ mask ไม่ว่าง

**ลำดับงาน:** ยืนยัน coverage/rule-critical examples และ lossless edit roundtrip → calibration/pilot24 (คง6human-first) → ปิดกฎและตรวจ scorer ที่ใช้ bbox → freeze protocol → ขยาย300รวมpilot แล้วทำต่อใน2,200เป็นbatches ไม่เปิด inference/full evaluation จากการบันทึกข้อตกลงนี้

## ผู้ทำตอบ 4 เรื่อง ส่วนตัวเลขให้สคริปต์เก็บ

| ขั้น | สิ่งที่ทำจริง | สิ่งที่บันทึก |
| --- | --- | --- |
| คนครบไหม | ดูภาพเต็มก่อนเห็นร่าง ตรวจทุกคนที่ยืนยันได้ รวมคนเล็ก นอน คลาน และคนที่ detector พลาด | person ID ภายในภาพ; คนที่ยังแยกไม่ได้เก็บรอตรวจ ไม่เดาจำนวนคนในฝูง |
| ส่วนไหนวาดได้ | ให้เครื่องช่วยร่าง แล้วแก้ Hair / Face / Upper / Lower ตามสิ่งที่เห็น | mask กับเจ้าของ; ถ้าทำไม่ได้เลือกเหตุผลสั้น ๆ |
| สีไหนบอกได้ | ดูสีเสื้อผ้าจากภาพต้นฉบับ บนและล่างตอบแยกกัน | สีที่เห็น หรือ “ระบุไม่ได้” พร้อมเหตุผล ไม่ใช้ดำแทน missing |
| ผ่านหรือยัง | สลับภาพจริงกับ mask ตรวจคนตกหล่น เจ้าของ ขอบ คลาส และสี | ผ่าน / ต้องแก้ / รอตัดสิน พร้อมผู้ตรวจและ revision |

**หลักเดียวตลอดงาน:** วาดสิ่งที่เห็น ระบุสิ่งที่ไม่รู้ และอย่าให้โมเดลเป็นผู้ตัดสิน GT คนหนึ่งอาจมี mask เสื้อที่ใช้ได้ แต่สีใช้ไม่ได้ ไม่ต้องทิ้งทั้งคนหรือทั้งภาพ

ขนาด พื้นที่ สัดส่วนภาพ source hash กล้องและเวลาอ้างอิง ให้สคริปต์คำนวณหรือดึงจาก metadata เมื่อมี ไม่ต้องกรอกซ้ำหรือเดาระยะเมตร เหตุผลสั้นที่เลือกได้หลายข้อคือ **ถูกบัง / หลุดขอบ / เล็กหรือเบลอ / แสงหรือภาพขาวดำ / คลาสหรือเจ้าของไม่ชัด / ภาพถูกทับข้อความหรือกรอบ** โดยผูกกับส่วนที่ได้รับผล

แยก **วาดได้ / ยืนยันว่าไม่มี / มองไม่พอตัดสิน / ยังไม่ได้ตรวจ** ออกจากกัน “ถูกบัง” ไม่ได้แปลว่าวาดไม่ได้เสมอไป หากเห็นแขนเสื้อสองชิ้นก็เก็บสองชิ้นโดยไม่เติมใต้สิ่งบัง สถานะสีแยกจากสถานะ mask; Hair/Face ไม่ต้องกรอกสีเสื้อผ้า

### กติกาที่ใช้ตลอด 6 ข้อ

1. **ดูภาพเต็มก่อน:** ตรวจทุกคนที่ยืนยันได้ รวมคนเล็ก คนนอน คนคลาน และคนที่โมเดลไม่พบ ไม่คัดคนตามกรอบYOLO
2. **ให้โมเดลร่าง แล้วตรวจแก้:** ใช้SAM3ที่เตรียมไว้ช่วยสร้างmask; คุณแก้ขอบ/คลาส/เจ้าของก่อนรับ ไม่ใช้คะแนนโมเดลเป็นการรับรองGT
3. **ทำ4ส่วนที่เห็น:** Hair=ผมศีรษะ, Face=ใบหน้าไม่รวมคอ, Upper=เสื้อผ้าบน, Lower=เสื้อผ้าล่าง ไม่เติมส่วนที่ถูกบัง หมวก/ของถือไม่ใช่เสื้อผ้าสี่ส่วน ชุดชิ้นเดียวคร่อมบนล่างเก็บเป็น cross-zone ไม่ตัดเอวเดา
4. **ไม่ชัดให้บอกไม่ชัด:** แยกถูกบัง/หลุดขอบ/ไม่แน่ใจ/ยังไม่ได้ตรวจ ไม่เปลี่ยนเป็นไม่มีคนหรือไม่มีส่วนร่างกาย และไม่ลบคนทั้งคนเพราะประเมินได้บางส่วน
5. **สีดูจากภาพจริง:** ใช้สีที่เห็นบนเสื้อผ้า ไม่อ่านจากoverlay; มองไม่พอให้unknownพร้อมเหตุผล ไม่ใช้ดำแทนunknown
6. **รับหลังตรวจและเปิดกลับได้:** maskทุกชิ้น/รู/ownerต้องอยู่ครบ เก็บรุ่นก่อนแก้และผู้ตรวจ สคริปต์ตรวจขนาดกับไฟล์ให้เอง คุณไม่ต้องกรอกตัวเลขพิกเซล

ขอบหู หนวดเครา แว่น และขอบคลุมเครือมีข้อเสนอเริ่มต้นใน revision `0.2-R1-PROPOSED` ด้านล่าง ต้องทดสอบกับตัวอย่างก่อน freeze ไม่เปลี่ยนคำจำกัดความเพื่อให้ตรงโมเดลใด รายละเอียดร่างเดิมเก็บในภาคผนวก

## นิยามขอบเขตที่แนะนำสำหรับ pilot

นี่คือข้อเสนอของโครงการ ไม่ใช่คำจำกัดความที่ paper รับรอง ต้องผูกภาพตัวอย่างและทดสอบความเข้าใจก่อนรับเป็นกฎที่ freeze แล้ว

| ส่วน | ให้นับ | ไม่ให้นับ / เมื่อกำกวม |
| --- | --- | --- |
| Hair | กลุ่มผมศีรษะและปอยที่มีหลักฐานพิกเซล | หมวก ผ้าคลุม หนวดเครา; ไม่สร้างเส้นผมละเอียดกว่าภาพ |
| Face | บริเวณใบหน้าที่เห็น รวมตา คิ้ว จมูก ปาก และหนวดเคราภายในขอบใบหน้า เป็น face region ไม่ใช่ skin-only | คอ หู ผม หน้ากาก กรอบแว่น; ใต้เลนส์ใสที่เห็นหน้าให้นับได้ แต่ไม่เดาใต้เลนส์ทึบ/สะท้อน ถ้าแยกขอบไม่ได้เก็บ uncertainty |
| Upper | เสื้อผ้าบนที่เห็น เช่น เสื้อ แจ็กเก็ต; ชั้นนอกและชั้นในเฉพาะส่วนที่เปิดให้เห็น | ผิวกาย กระเป๋า ของถือ; ไม่วาดเสื้อข้างใต้ทับชั้นนอก |
| Lower | กางเกง กางเกงขาสั้น กระโปรงที่เห็น | ผิวขา ถุงเท้า รองเท้า; ไม่เติมส่วนที่ถูกบัง |
| ชุดชิ้นเดียวคร่อมบน–ล่าง | เก็บ mask ที่เห็นเป็น `cross-zone` พร้อมเจ้าของ | ไม่ตัดตามเอวเดา ไม่ติด Upper/Lower ซ้ำทั้งชิ้น; ยังไม่อ้างว่าครอบคลุมเสื้อผ้าทุกประเภท |

Face นี้ต่างจาก Sapiens Face_Neck และอาจต่างจาก CIHP บางขอบ ต้องประกาศ mapping ภายหลัง ไม่ขยาย GT ตามโมเดลที่อยากให้ชนะ นิยามหนวดเครา/หู/แว่นเป็นข้อเสนอเริ่มต้นที่เลือกให้แล้ว ไม่ใช่คำถามให้ผู้ใช้คิดกฎทั้งหมดเอง แต่ยังต้องมีตัวอย่างตรวจรับก่อนใช้งานทั้งชุด

## ปัจจัยหลายอย่าง แต่ไม่ต้องเพิ่มแบบฟอร์มยาว

| ปัจจัย | เครื่องช่วยอะไร | คนตัดสินอะไร | ผลต่อการใช้ข้อมูล |
| --- | --- | --- | --- |
| ขนาดคนและแต่ละส่วน | bbox สองแกน พื้นที่ mask และสัดส่วนภาพ | พิกเซลพอให้ลากขอบจริงไหม | วิเคราะห์ตามขนาดได้ ไม่ใช่ระยะเมตร; คนนอนไม่เล็กเพราะวัดแค่ความสูง |
| บัง/คนซ้อน/ติดขอบ | ตรวจ owner และ pixels ที่ซ้อนผิดเงื่อนไข | ของใคร เห็นถึงไหน | เก็บ visible support; semantic ใช้ได้แต่ owner ไม่ทราบต้องแยกสิทธิ์งาน instance |
| มุม/ท่าทาง/ความหนาแน่น | นับคนจากรายการที่ตรวจแล้ว ใช้ tags ที่ยืนยันแล้ว | เติม tag ที่เห็นชัดระหว่างตรวจ | ตรวจช่องว่างด้านหลัง ก้ม นอน มุมสูง; metadata กล้องไม่บอกท่ารายคน |
| เบลอ/ความละเอียด/แสง/บีบอัด | ค่าคม/สว่างใช้จัดคิวตรวจ | boundary กับสีของแต่ละส่วนยังใช้ได้ไหม | ไม่ใช้ threshold ภาพรวมคัดคนทิ้ง; mask กับสีมี valid domain ต่างกันได้ |
| สีเพี้ยน/ขาวดำ/หลายสี | เก็บ RGB เดิมและ region references | สีที่สังเกตได้ ไม่เดาสีวัสดุจริง | ไม่ใช้ enhancement สร้าง GT; หลายสีเก็บรายการก่อน ไม่แต่งเปอร์เซ็นต์ |
| ชั้นเสื้อผ้า/หน้า/คอ | ตรวจคลาสและ combinations | ใช้กฎสั้น ส่งเคสที่ไม่เข้ากฎ | เปลี่ยนกฎต้องมี revision และย้อนตรวจ records ที่เกี่ยวข้อง |
| กรอบ/ข้อความ/พื้นที่ดำ/ภาพสะท้อน | เก็บ source-artifact regions | คนจริงในฉาก หรือภาพสะท้อน/ภาพบนจอ | เสนอไม่นับภาพบนจอ/ภาพสะท้อนเป็นคนจริงเพิ่ม; เก็บ region แยก ไม่เติมใต้ข้อความ |
| ภาพซ้ำ/กล้องเดิม/เวลาใกล้กัน | ตรวจ hashes และกลุ่มกล้อง/เวลา | ยืนยันเหตุการณ์เมื่อมีหลักฐาน | เวลาแตกต่างไม่รับรองความเป็นอิสระ; ยังไม่แบ่ง train/test อัตโนมัติ |
| ร่าง AI ชี้นำ/คนตกหล่น | เก็บ draft → edits → accepted | ดูภาพเต็มก่อน แล้วตรวจทั้งสิ่งที่เสนอและไม่ได้เสนอ | คนละ architecture ไม่รับรองความเป็นกลาง; คง 6 ภาพ human-first |
| ส่งออกเสียรูป | ตรวจ grid, holes, ทุก component และ owner | เปิดกลับแล้วเทียบต้นฉบับ | polygon ดูสวยไม่พอ ถ้ารูหรือชิ้นส่วนหายห้ามรับเป็น canonical GT |

ไม่ต้องกรอกทุก difficulty tag ก่อนวาดทุกภาพ และ “ไม่ได้ติด tag” ไม่เท่ากับ “ไม่มีปัจจัยนั้น” รายงาน coverage แยกตรวจแล้ว/ยังไม่ทราบ หากจะวัดคะแนนกลุ่มคนนอน ต้องตรวจสมาชิกและ negatives ของกลุ่มนั้นครบก่อน ไม่วัดจากเฉพาะคนที่บังเอิญติด tag

<details>
<summary>ข้อกำหนด valid domain, QA และการนำไปใช้ต่อ — สำหรับผู้ดูแลชุดข้อมูล</summary>

**โดเมนคะแนน:** สร้างจาก annotation และกฎเดียวกันข้ามโมเดล ไม่ใช้ prediction เลือกพื้นที่วัด พื้นที่นอก polygon ยังไม่เท่ากับ background จนตรวจครบ; คนที่ยังไม่ได้ annotate คือ unfinished work ไม่ใช่ negative ภาพที่ตรวจแล้วว่าไม่มีคนจึงเป็น verified negative ได้

เก็บ known non-target แยกจาก unknown เช่น รองเท้าไม่ใช่สี่ targets แต่รู้ว่าคืออะไร ส่วน `cross-zone` ที่รู้ว่าเป็นเสื้อผ้าแต่แยก Upper/Lower ไม่ได้ เก็บ label/mask ไว้ ข้อเสนอคือไม่นับพื้นที่นี้ใน strict Upper/Lower domain ของทุกโมเดลและรายงานจำนวนคน/พิกเซลที่ยกเว้น ไม่ยกเว้น Hair/Face ไปด้วยโดยไม่มีเหตุผล นี่เป็นข้อเสนอสำหรับ dataset ใหม่ ไม่แก้ C4-P/native benchmark เก่าย้อนหลัง ต้อง freeze evaluator contract ก่อน scoring

ถ้ารู้คลาสแต่ไม่รู้เจ้าของ semantic อาจใช้ได้ แต่ instance eligibility ต้อง pending/excluded พร้อมเหตุผล ขอบที่ตัดสินไม่ได้ให้เก็บ uncertainty region จากภาพ ไม่ทำ erosion หรือขยาย ignore band ทั้งชุดเพื่อเพิ่มคะแนน หากระบุขอบ uncertainty ไม่ได้ต้องส่ง review ไม่เดาแล้วเรียก valid

**แยกชุดตามคำอ้าง:** unseen-camera ต้องแยกกล้อง; future same-camera ต้องแยกเหตุการณ์/ช่วงเวลาโดยมีหลักฐาน ทั้งสองตอบคนละคำถาม Pilot ที่ใช้ปรับกฎเป็น development-exposed ไม่ใช่ unseen confirmatory test รอบนี้ไม่สร้าง split

**QA ที่ใช้แรงตรงจุด:** scripts ตรวจไฟล์ทุกภาพ ผู้ใช้ตรวจรับทุกภาพ Codex ช่วยเคสผิดเงื่อนไข กำกวม และเปลี่ยนกฎ พร้อมตัวอย่างปกติที่เลือกด้วยวิธีคงที่เพื่อไม่ตรวจเฉพาะ warnings ห้าม accepted เพราะไม่มี warning ตัวเลข IoU/Dice ระหว่าง draft กับหลังแก้บอกขนาดการแก้ ไม่ใช่ accuracy ของ GT

คง 6 ภาพ human-first ก่อนเห็น AI เพื่อดูคนตกหล่น ขอบ และคลาส การเทียบคนกับ AI ไม่ใช่ inter-annotator agreement; ถ้าจะอ้าง agreement ระหว่างมนุษย์ต้องมีคนที่สองทำอย่างอิสระตามกฎเดียวกัน ตรวจซ้ำคนเดิมเป็น repeatability ที่อาจมีความจำ ไม่ตั้ง IoU 0.9 หรืออัตราผ่านสากลขึ้นเอง

**Pilot24:** เลือกจาก coverage ที่ตรวจแล้วพร้อม source hashes ถ้ามี membership ล็อกแล้วให้ตรวจช่องว่าง ไม่เปลี่ยนเงียบ ๆ ไม่พยายามให้ 24 ภาพครอบคลุมทุก combination เลือกเคสทั่วไปและเคสขัดกฎที่มีจริง ไม่เลือกจากคะแนนโมเดล benchmark

เกณฑ์จบที่เสนอ: ทุกภาพมี human receipt; masks/owner/validity/สีอ่านกลับตรง; เคสขัดกฎมีคำตัดสินหรือ explicit unresolved domain; มี counts/coverage และเวลา draft/edit/review ที่วัดจริง; เก็บ revision และรายการที่ต้องย้อนแก้ ไม่ต้องทำ unknown ให้เป็นศูนย์ แต่ห้ามซ่อนหรืออ้าง valid ครบ

ผลที่ผ่านใช้ต่อใน 2,200 และ release300 ได้ภายใต้ revision เดียวกัน ความคืบหน้าวัด accepted images/persons/regions และ unresolved counts ไม่ใช่จำนวน plots กราฟขนาด/แสง/มุมเป็นผลประกอบเพื่อเห็นช่องว่าง ไม่ใช่การรับรอง GT

</details>

## หลักฐานที่ใช้ตัดสิน

อ่าน [ทะเบียนหลักฐานรอบนี้](EVIDENCE_AND_HYPOTHESES_TH.md#targeted-review-20261105) เพื่อดู source/section และสิ่งที่นำมาปรับใช้ งาน interactive segmentation รองรับแนวทางเครื่องร่าง–คนแก้และกฎรายคลาส แต่ไม่รับรองความเร็ว SAM3 ของเรา RAP สนับสนุนการตรวจมุม/การบังรายคน CrowdHuman แยก visible กับ full extent; เราใช้ visible masks โดยไม่เพิ่ม amodal GT

Cityscapes มี policy เติมรูภายใน foreground จริง จึง **ไม่ยืม topology นั้น** สำหรับเสื้อผ้าเราเก็บรูและชิ้นส่วนที่เห็นเพื่อไม่ปนพื้นหลังในการสกัดสี กติกา Face, cross-zone, 4 คำถามและ valid domains เป็นข้อเสนอของโครงการ ไม่ใช่มาตรฐานสำเร็จรูปจาก paper

## “ระยะ” และความครอบคลุม

ใช้ **ขนาดที่คนปรากฏในภาพ** เป็นข้อมูลหลัก ระยะเป็นเมตรยังไม่ทราบหากไม่มีcamera calibration/ข้อมูลตำแหน่งอ้างอิง ภาพคนเล็กอาจมาจากการย่อภาพ คนย่อตัว หรือถูกบัง จึงไม่ตั้งว่าเล็ก=ไกลโดยอัตโนมัติ

| ตรวจเรื่องอะไร | สิ่งที่เก็บและนำไปใช้ |
| --- | --- |
| คนเล็ก–ใหญ่ | ใช้ bbox GT ที่ตรวจแล้ววัดกว้าง/สูง พื้นที่กรอบ และสัดส่วนภาพทั้งสองแกน; พื้นที่ mask GT วัดเฉพาะ4parts ไม่แต่งพื้นที่ mask คนทั้งตัวจาก bbox |
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

<a id="person-part-pseudolabel"></a>
## ขนาดขั้นต่ำและสคริปต์สร้างร่าง person + 4 parts — 6 พฤศจิกายน 2026

สถานะ **SCRIPT_IMPLEMENTED_CPU_CHECKED / MODEL_QUALITY_NOT_YET_VALIDATED** ผู้ใช้ยืนยันว่าต้องการ script ไม่ใช่หน้าตรวจใหม่ ใช้ SAM3 ช่วยร่าง bbox คน, mask คน และ Hair/Face/Upper/Lower แล้วผู้ใช้ตรวจแก้; ไม่สร้างเว็บและไม่ใช้ outputs ของ YOLO/parser ที่เป็นผู้เข้าสอบมาเป็นเฉลย

### ควรกำหนดขั้นต่ำกี่ pixels

**ข้อเสนอหลัก: ไม่ใช้ตัวเลขเดียวลบคนออกจาก GT ตอนเก็บ annotation** ยืนยันว่าเป็นคนและลาก bbox ได้ให้เก็บ ส่วน mask คน, mask แต่ละ target และสีมี validity แยกกัน หากไม่รู้ว่าเป็นคนจริงให้เก็บ uncertainty region แทนเดา instance ถ้าขอบ mask ไม่พอให้เก็บ bbox ที่ตรวจได้และเหตุผล mask ไม่พร้อม ห้ามสร้าง mask สี่เหลี่ยมเต็ม bbox ทดแทน

| การใช้งาน | เกณฑ์ที่แนะนำตอนนี้ | เหตุผล |
| --- | --- | --- |
| บันทึกว่ามีคน / bbox | คนยืนยันได้และขอบ bbox รองรับจากภาพ; ยังไม่มี hard minimum | คนเล็กยังอาจเป็นโจทย์ที่ YOLO ต้องตรวจ การไม่ label จะทำให้ผู้ตรวจพบจริงกลายเป็น FP |
| person mask | optional/helper เท่านั้น หากเลือกสร้าง GT เพิ่มจึงตรวจ visible boundary/ทุกชิ้น/รู; ไม่เดาตัวเต็มใต้สิ่งบัง | ไม่ใช่ gate ของ GT ชุด bbox+4parts ที่รับรองแล้ว |
| Hair/Face/Upper/Lower | พิจารณาความชัดของแต่ละส่วน ไม่ตัดสินจาก bbox คนรวม | คนใหญ่แต่หันหลังอาจไม่มี Face ที่เห็น; คนเล็กอาจเห็นเสื้อแต่ไม่มีรายละเอียดหน้า |
| สีบน/ล่าง | เห็น apparent color เพียงพอและ region ไม่ปนเปื้อน | mask ถูกแต่ภาพขาวดำยังบอก hue ของเสื้อจริงไม่ได้ |
| จัดคิวตรวจขนาด | ยาวสุดของ visible bbox `<20`, `20–49`, `50–99`, `≥100 px` พร้อม width/height/area จริง | เป็น **review bins ที่เสนอ** ไม่ใช่เกณฑ์คัดคนหรือมาตรฐานสากล; ใช้ทั้งสองแกนเพื่อรองรับคนนอน |

ตัวเลข 20/50 มีตัวอย่างใน pedestrian evaluation แต่มีนิยามต่างกัน: [CityPersons evaluator, Params และ _prepare](https://github.com/cvgroup-njust/CityPersons/blob/master/evaluation/eval_script/eval_MR_multisetup.py) ใช้ **ความสูง** 50 px/visibility0.65 สำหรับ Reasonable และ 20 px/visibility0.2 สำหรับ All ของเขา เราไม่ได้วัด amodal height/visibility แบบนั้นและมีคนนอน จึงไม่อ้างว่าการใช้ longest side20 ของเราเป็น CityPersons protocol ส่วน100เป็นเพียงเส้นแบ่งคิวอ่านง่ายของโครงการ [COCO](https://cocodataset.org/dataset/detection-eval.htm) รายงานกลุ่มจาก mask area อีกนิยามหนึ่ง

ตัวอย่างคำนวณเพื่ออธิบายความไวของ IoU: ถ้า GT เป็นสี่เหลี่ยม10×10 แต่ขอบทำนายหดเข้าทุกด้าน1px เหลือ8×8 จะได้IoU0.64; GT20×20เหลือ18×18ได้0.81 ตัวอย่างสมมตินี้อธิบายว่าความผิด1pxกระทบคนเล็กมาก ไม่ใช่ผลทดลองหรือเหตุผลให้ตั้ง20pxเป็นเส้นตัดสากล

หลัง pilot ให้รายงานจำนวนคนและความพร้อม bbox/mask/target/color ตามขนาดก่อนเลือก evaluation subsets; ถ้าจำเป็นต้องมี minimum สำหรับคะแนนหลัก ต้อง freeze ก่อนดูผลผู้เข้าสอบและมี tiny-person diagnostic/ignore treatment ที่ประกาศเหมือนกันทุกระบบ คนต่ำกว่าเส้นตัดห้ามหายจาก annotation หรือกลายเป็น background เงียบ ๆ ยังไม่มี final benchmark cutoff ในรอบนี้

### โมเดลช่วยร่างและเรื่อง bias

**แนะนำ SAM3 ที่มีอยู่เป็นตัวช่วยหลัก พร้อม human-box crop สำหรับคนที่ตกหล่น** ไม่เพิ่ม Grounding DINO หรือ weights อื่นก่อนเห็นข้อผิดพลาดจริงใน pilot นี่คือการเลือกเครื่องมือที่เหมาะเริ่มงานจากหลักฐานและทรัพยากร ไม่ใช่การรับรองว่าแม่นที่สุดบน CCTV ชุดนี้

| ทางเลือก | หลักฐาน / ความต่าง | ข้อสรุป |
| --- | --- | --- |
| SAM3 | [paper v2 §3](https://arxiv.org/html/2511.16719v2) ระบุ DETR-like detector, PE backbone และ mask head; ใช้ text/visual prompts ได้ | ทำ person boxes/masks และ part proposals ด้วยตัวเดียวที่มีอยู่; เลือกใช้เป็น drafts ต้องตรวจ class/owner/boundary เอง |
| Grounding DINO + SAM3 | [official implementation](https://github.com/IDEA-Research/GroundingDINO) เป็น Transformer-based grounded detector; ยังต้องมี mask model | เป็น fallback candidate หาก person recall ของ SAM3 ไม่พอ ไม่รับรองว่าแม่นกว่าหรือเป็น architecture ที่เป็นอิสระจากทุกผู้เข้าสอบ; รอบนี้ไม่ติดตั้ง/ดาวน์โหลด |
| ผู้เข้าสอบ YOLO/parser เดิมช่วยสร้างเฉลย | checkpoint และข้อผิดพลาดเกี่ยวข้องกับสิ่งที่กำลังจะวัดโดยตรง | ไม่เลือกเป็น draft generator หรือ person gate ของ GT |
| คนวาดเอง / classical interactive segmentation | [Microsoft Research review](https://www.microsoft.com/en-us/research/publication/interactive-foreground-extraction-using-graph-cut/) อธิบาย graph-cut/GrabCut ซึ่งไม่ใช่ pretrained neural parser | ใช้ช่วยเคสกำกวมหรือ first pass ได้ แต่ยังต้องมีคนระบุความหมายและไม่รับรองขอบจาก algorithm โดยอัตโนมัติ; ยังไม่ได้เพิ่ม GrabCut execution |

เก้าผู้เข้าสอบเดิมมีทั้ง CNN และ Transformer/ViT อยู่แล้ว การกำหนดว่า helper ต้องไม่มี architecture component ซ้ำกับทุกตัวจึงยังทำให้เป็นจริงไม่ได้ด้วยตัวเลือกข้างต้น **SAM3 ต่างตระกูลและ checkpoint จากผู้เข้าสอบ แต่ยังเป็น Transformer เช่นบางผู้เข้าสอบ** ไม่อ้างว่าข้อมูลฝึกไม่ทับกันหรือไม่มี annotation bias การควบคุมที่ใช้จริงคือไม่อ่าน predictions/คะแนนของผู้เข้าสอบ, เก็บ human-first6ก่อนเห็นAI, ตรวจ missed persons ทั้งภาพ, เก็บ raw→แก้→รับรอง และให้กฎ GT เป็นอิสระจากชื่อโมเดล

สำหรับ 4 parts SAM3 เป็น promptable segmenter ไม่มี native semantic IDs สี่คลาสของเรา แต่ละชื่อไฟล์จึงเป็นกลุ่มตาม prompt ที่เรียก ไม่ใช่การรับรอง class ID จาก head ของ parser และยังไม่ใช่ parser 4 คลาสที่พิสูจน์แล้ว prompt `face` อาจไม่ตรงขอบ Face ของเรา และ `upper body clothing`/`lower body clothing` อาจตอบคลุมเครือ กรณีนี้ต้องแก้ semantic labels ไม่แปลว่าชื่อ prompt รับรองคลาสถูกทั้งหมด

### Script ทำอะไรจริง

- [person_pseudolabel.py](../scripts/person_pseudolabel.py): จัด candidate queue ตามกล้อง/seed จาก intake ที่ผูก hashes, เก็บ geometry, export native binary PNG ทุก instance/ทุก target, ตรวจ readback และสร้าง preview; มี COCO uncompressed RLE utility ที่รักษารู/ชิ้นส่วน แต่ยังไม่มี GT evaluation/export ที่อนุมัติเอง
- [sam3_person_draft.py](../scripts/sam3_person_draft.py): เรียก local SAM3 โดยตรง ไม่ผ่าน server adapter ที่ทำ largest-contour ใช้ FP32/batch1/resolution1008/noAMP/noTF32 และไฟล์weightsเดิม ไม่มี download/fallback/auto-retry รองรับหนึ่ง image ID ต่อ invocation พร้อม call budget และ immutable attempt claim
- เส้นทางอัตโนมัติ: original RGB → SAM3 `person` → เก็บ native person masks/model boxes/visible mask envelope → cropรายคนพร้อมcontext15% → ร่าง Hair/Face/Upper/Lower และ auxiliary `dress` probe → map-backบนgridเดิม `dress` probe ไม่เท่ากับ Apparel และไม่ถูกแบ่งเป็น Upper/Lower
- เส้นทางคนแก้ bbox: `--person-boxes` ใช้กรอบที่คนวาดก่อนเห็นร่าง พร้อม source SHA/reviewer → cropพิกเซลต้นฉบับพร้อมcontext → SAM3 positive-box prompt → parts routeเดิม ช่วยคนเล็ก/ตกหล่นโดยไม่ให้ text detector เป็นgate ไม่เอากรอบYOLOมาแทน human inventory
- เก็บ raw candidate planes และ raw unions ก่อน intersection แยกจาก `owned_proposal` ที่ตัดด้วย person maskเพื่อช่วยตรวจ พร้อม outside-person pixels และ target-conflict map **intersection นี้เป็น draft ที่แก้ได้** ไม่ใช่ขอบเขต GT; person maskผิดอาจตัด Hair/เสื้อที่ถูกออก จึงต้องดูrawประกอบ
- ยังไม่ compose เป็นเฉลย4classแบบบังคับชนะทับกัน หาก Face/Hairซ้อนหรือ Upper/Lowerชนกันให้เก็บไว้ตรวจ ไม่ใช้คะแนนสูงสุดแปลเป็น GT ไม่มี proposalคือ “โมเดลไม่เสนอ” ไม่ใช่ absent หรือ verified negative
- ทุก mask อยู่ original grid; person support ไม่เท่ากับ union4parts เพราะยังมีผิวกาย รองเท้า/ส่วนอื่น person masks ที่รวมกระเป๋าหรือคนข้างเคียงต้องแก้ตามกฎ

โมเดลมี learned bbox ของตนเอง และ script เก็บ bbox envelope จาก helper mask แยกไว้เป็นร่าง **GT bbox คนต้องให้ผู้ใช้ตรวจ/แก้จากภาพจริงได้โดยตรง ไม่บังคับแก้ person mask ก่อน** ไม่ใช้ union ของ4partsแทน bbox คนเพราะอาจขาดแขนขา และไม่รับ draft model box เป็น GT อัตโนมัติ ประกาศ visible-person bbox policy ให้ชัด ไม่เรียกผลว่า official amodal pedestrian benchmark

### จำนวนภาพและลำดับที่ใช้

คง **pilot24 → release300รวม24 → ทำต่อใน2,200** ไม่สร้างจำนวน seed ใหม่ที่ไม่มีเหตุผล 24ภาพมี6calibration+18workflow โดย6ในworkflowเป็นhuman-firstตามแผนเดิม จำนวน24เพื่อพิสูจน์เครื่องมือ/กฎ/ภาระงาน ไม่ใช่จำนวนที่ให้ statistical precision ของทั้งdatasetและไม่ใช่ชุด train โมเดล SAM3 ในวิธีนี้เป็นpretrainedzero-shot ไม่มี training/fine-tuningจาก24ภาพ

เตรียม queue candidate24 จาก24กลุ่มกล้องแล้วด้วย deterministic camera round-robin; **ยังไม่ใช่ membership ที่รับรอง coverage** ต้องเปิดตรวจคนเล็ก/มืด/บัง/ท่าทางก่อนfreezepilot รายชื่อและภาพอยู่private ไม่เผยแพร่กล้องจริงขึ้นGit การเห็นแต่24กล้องยังไม่รับรอง coverageครบ67กลุ่มหรือทุกเหตุการณ์ เปลี่ยนสมาชิกต้องสร้างqueueใหม่พร้อมเหตุผล ไม่แก้queuehashย้อนหลัง

### วิธีใช้และการตรวจรับ

ใช้ Python environmentเดิมที่มีPillow/PyTorch; system `python3` ของเครื่องนี้ไม่มีPillowจึงใช้ interpreterของ environmentตรง ๆ ตัวอย่างต่อไปนี้เป็น placeholders; คำสั่งpathsจริงและqueueอยู่private work run

```bash
# สร้างคิวอย่างเดียว ไม่เรียกโมเดล
/path/to/existing-env/bin/python scripts/person_pseudolabel.py prepare \
  --binding /private/intake/SCIENTIFIC_INPUT_BINDING.json \
  --output /private/work/runs/new-pilot24

# ตรวจ binding/imports/input เท่านั้น ยังไม่โหลด weights เข้า GPU
/path/to/existing-env/bin/python scripts/sam3_person_draft.py \
  --queue /private/work/runs/new-pilot24 --id CAND_EXAMPLE \
  --source-checkout /path/to/X-AnyLabeling-Server \
  --checkpoint /path/to/existing/sam3.pt --output /private/work/runs/precheck-example

# เมื่อตรวจ readinessและภาพที่อนุญาตแล้ว เพิ่ม --execute และใช้ outputใหม่
# ใช้ --max-calls 64 เป็นเพดานชัดเจน ไม่เพิ่มอัตโนมัติเมื่อคนมาก
```

`--execute` มีสิทธิ์เรียกโมเดลจริง การไม่มีflagนี้เป็นprecheckเท่านั้น คำสั่งหนึ่ง IDไม่เปิดbatch2,200เอง max64นับทั้ง image encodesและprompt forwards; routeอัตโนมัติใช้2+6P callsต่อภาพเมื่อPคือจำนวนpersonproposalsและทำครบทุกขั้น ไม่รวมmodel loading หากคนมากจนเกินbudgetจะหยุดพร้อมpartialartifacts ไม่แอบเพิ่มงบ One attemptต่อID; failure/partialต้องreconcileก่อนสร้างcontinuationเอง ไม่ลบATTEMPTSเพื่อretry

`--person-boxes` JSON มี `image_id`, `source_sha256`, `provenance: human_drawn_before_model_draft`, `reviewer`, `boxes_xyxy_exclusive` เป็นlistของกรอบoriginalpixels ส่วนhuman-first6ต้องมี `--human-first-receipt` ซึ่งผูกsource,reviewer,timeและhashesของไฟล์annotationที่มีอยู่จริงก่อนAI Scriptตรวจreceiptได้แต่ไม่พิสูจน์ว่ามนุษย์ไม่เคยเห็นAIจากช่องทางอื่น

กรณีimageแตก/EXIFrotationไม่ปกติ/geometryผิด/labelsไม่binary/nonfinite/OOM/CUDA/callbudget/diskguard ให้เก็บSTATUS/TRACEBACK/CALLSและpartialหยุด ไม่ลดresolution/precisionหรือเปลี่ยนpromptเพราะอยากให้ผ่าน เพดานdiskfree50GiBคงเป็นoperationalguard ส่วน `--min-free-gib` เป็นreserveที่ผู้เรียกประกาศ ไม่ใช่ค่าคาดการณ์peak ห้ามใช้freeVRAMจุดเดียวรับรองว่าโมเดลรันได้หรือรันร่วมปลอดภัย

**ตรวจแล้วในรอบนี้:** CPU requirement fixtures14กรณีผ่าน ครอบคลุมhole/components, original-grid map-back, class conflicts/raw-versus-owned, empty outputs, tiny/lying geometry, RLE, bindings/changedsource, human-box rescue, budget/failurehistory และhuman-firstguards; ใช้fakebackendที่ระบุชัด ไม่ใช่ผลSAM3จริง Precheckจริงอ่านภาพcalibrationหนึ่งภาพ/hashweights/importsผ่านด้วยenvironmentเดิม ไม่มีmodelโหลดหรือGPUforward

ตรวจฮาร์ดแวร์จริงพบTeslaT4และงานSapiens1Bกำลังใช้GPUอยู่; precheckเห็นfreeประมาณ7.56GiB แต่ยังไม่มีmeasuredpeakของSAM3FP32+partsrouteนี้ จึงยังไม่อ้างว่ารันร่วมพอหรือไม่พอ ไม่เปิดGPUงานใหม่ในรอบสร้างscript/ทบทวนนี้ สถานะGPUreadiness/ความแม่น4partsยังต้องตรวจด้วยcalibrationจริงที่มีbudgetก่อนเปิดpilotdraftsหรือbatch

ตัวสร้าง draft ข้าม largest-contour ของ server เดิมได้แล้ว แต่ **การเปิดแก้และส่งกลับจาก desktop editor แบบไม่ทำ mask เสียรูปยังต้องตรวจ** ก่อน accepted GT สคริปต์นี้ยังไม่มีปุ่ม/คำสั่งรับรอง GT จากโมเดลหรือ exporter สำหรับคะแนน benchmark สี confidence ที่เก็บคือ model proposal score ไม่ใช่ความมั่นใจว่ามนุษย์รับรองแล้ว

**ขั้นถัดไปที่ชัดเจน:** ยืนยันตัวอย่างcoverageและ6human-first → ทดสอบSAM3หนึ่งภาพcalibrationเมื่อจัดresourceได้ โดยเก็บactualpeak/geometry/raw4partsและดูภาพจริง → แก้implementationเฉพาะbugพร้อมhistory → ทำpilot24ตามงบ → คนตรวจแก้/รับรองและfreezeกฎ → ขยาย300/2,200เป็นbatches ไม่เปลี่ยนกฎจากคะแนนYOLO/parser

## Pilot เป็นงานจริงที่นำไปใช้ต่อได้

Pilot24คือ **ลองannotateจริง** เพื่อวัดความถูกต้องของเครื่องมือ กติกา และเวลาที่ใช้ ไม่ใช่แค่plotกราฟ ภาพที่แก้จนผ่านใช้ต่อใน2,200และreleaseแรก300ได้โดยรักษาIDs/source hashes/annotation revisions ไม่ทำซ้ำเพราะเปลี่ยนbatch

ผลที่ต้องได้คือ original references, bbox GT พร้อม person ID, masks สี่ส่วนและ owner/validity, สีพร้อมสถานะ, ร่างก่อนแก้/ผลหลังแก้ และ review receipt; person mask ที่ helper สร้างแยกเป็น draft ไม่ใช่ GT บังคับ เก็บเวลาสร้างร่าง/เวลาแก้จริงเพื่อประมาณงานที่เหลือ ถ้ากฎเปลี่ยนให้reopenเฉพาะส่วนที่ได้รับผล เก็บpilotเป็นdevelopment exposure ไม่เรียก24ภาพนี้ว่าunseen test และไม่ใช้มันสรุปคุณภาพทั้งdataset

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
