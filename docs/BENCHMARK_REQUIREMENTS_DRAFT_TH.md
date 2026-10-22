# ข้อกำหนด dataset/evaluation — DRAFT

คัดต่อจาก foundation เดิมเฉพาะกระบวนการและข้อเสนอ ตัด baseline บริษัทออก ต้นฉบับ/วันที่/locator คงอยู่ใน private archive ยังไม่ตรึงทุก REQ/DEC หรือ class list

## 1. Research Objectives & Constraints — USER CONFIRMED หลัง foundation review

ปรับตามคำสั่งผู้ใช้ล่าสุดที่ได้รับ **หลัง commit eafe703** เมื่อ 22 ตุลาคม 2026; ไม่ใช่คำตอบที่มีอยู่ใน foundation review เดิม รอบนี้เตรียมแผน/รายการเสนอเท่านั้น ไม่เปิดภาพหรือเริ่ม annotation ประวัติ OPEN รอบก่อนยังอยู่ใน Git, รายงานเดิมและ decision log

| เป้าหมาย/ข้อจำกัด | สถานะล่าสุด | ส่วนวิธีการที่ยังไม่ตรึง |
| --- | --- | --- |
| End-to-End จากภาพเต็มเป็นผลหลัก | **USER CONFIRMED** | architecture, eligible-person policy, metrics/matching/denominator ยัง PROPOSED |
| Oracle เป็นผลวิเคราะห์แยก | **USER CONFIRMED** | รูปแบบข้อมูลอ้างอิงที่ป้อน เช่น crop/box/mask และการแปลงพิกัดยัง PROPOSED; ไม่รวม Oracle เป็นคะแนน End-to-End |
| ขั้นต่ำ person instance/mask + upper/lower/footwear masks พร้อมเจ้าของถูกต้อง | **USER CONFIRMED** | เป้าหมายความสามารถ ไม่ใช่ numeric class IDs, taxonomy ละเอียด/visible-amodal/อุปกรณ์ หรือวิธีสร้าง mask ที่อนุมัติแล้ว |
| ระบบสุดท้ายรองรับสีบน–ล่างเมื่อภาพเอื้ออำนวย | **USER CONFIRMED** | ต้องสำรวจ readability/uncertainty; palette, multi-color/unknown policy และเกณฑ์ภาพเอื้ออำนวยยัง PROPOSED |
| structured output และคำบรรยาย | **USER CONFIRMED** | schema/หน่วย/ข้อความและวิธีประเมินยัง PROPOSED; ไม่แต่งสีหรือรายละเอียดที่มองไม่ได้ |
| attributes เพิ่ม เช่นความยาว/ลวดลาย | **ไม่ mandatory** | สำรวจเป็นข้อสังเกตเสริมได้ แต่ไม่ขยายงานบังคับโดยปริยาย |
| จำนวนภาพสุดท้าย กำหนดส่ง กำลังคน เวลาที่มี | **OPEN** | ข้อเสนอเริ่ม 24+8 ไม่ตอบคำถามทรัพยากรหรือผูกมัด final quota |
| taxonomy, annotation method, metrics, QA thresholds | **PROPOSED** | ต้องมีหลักฐาน exploration/pilot และการตัดสินภายหลัง ไม่ถือเป้าหมายผลลัพธ์เป็นการอนุมัติวิธีทั้งหมด |

บทบาทข้อมูลในรอบนี้คือ discovery/development เพื่อออกแบบ protocol ไม่มี Final Test membership หรือข้อบังคับ train/validation/test ใหม่ ดู [แผนและ proposed manifest](AUDIT_PROTOCOL_DRAFT_TH.md)

## 3. ประชากรเป้าหมายและขอบเขตข้อสรุป

REQ-01 (PROPOSED): แยกสามประชากรให้ชัด

1. ภาพ CCTV ทั้งหมดในระบบบริษัท — ยังไม่มีกรอบสุ่มให้เข้าถึงครบ
2. ภาพเหตุการณ์ที่ถูกส่งเข้าสู่ระบบและดาวน์โหลดได้ — ตัวเลือกประชากรเป้าหมายที่ใกล้ข้อมูลปัจจุบัน
3. ภาพที่ผ่านเกณฑ์คัดเลือก — ประชากรที่แคบกว่าและมีเงื่อนไขความชัด

ข้อเสนอเริ่มต้น: ประเมิน “ภาพเหตุการณ์ CCTV ที่อยู่ในกรอบข้อมูลที่เข้าถึงได้” โดยระบุช่วงเวลา ไซต์ กล้อง และเงื่อนไขคัดเลือกจริง หากใช้เฉพาะ selected ให้จำกัดข้อสรุปถึงภาพที่ผ่านเกณฑ์นั้น ห้ามขยายเป็นความสามารถบนทุกเฟรมของทุกกล้อง

หากต้องการทั้งภาพตามการใช้งานปกติและเคสยาก ให้รายงานสองมุมมอง:

- ชุดสำหรับประมาณผลในประชากรที่ระบุ โดยมีวิธีสุ่มและน้ำหนักที่อธิบายได้
- ชุดท้าทายแบบเจาะจง เพื่อวิเคราะห์ข้อผิดพลาด
ยังไม่กำหนดสัดส่วน และไม่เฉลี่ยสองชุดเข้าด้วยกันโดยไม่มีเหตุผลทางสถิติ

## 4. งานและหน่วยประเมินที่เสนอ

| ID | งาน | หน่วยและคำตอบอ้างอิงที่ต้องมี | สถานะ |
| --- | --- | --- | --- |
| REQ-02 | person instance/mask และ ownership ของแต่ละ region | คนภายในภาพและการผูก region กลับเจ้าของ | USER CONFIRMED เป้าหมายขั้นต่ำ; geometry/อุปกรณ์/eligible scope ยัง PROPOSED |
| REQ-03 | upper/lower/footwear masks | region masks ที่ผูก person owner ถูกต้อง | USER CONFIRMED เป้าหมายขั้นต่ำ; taxonomy/ชิ้นเดียว/ชั้นเสื้อผ้ายัง PROPOSED |
| REQ-04 | สีบน–ล่างเมื่อภาพเอื้ออำนวย | สีและความไม่แน่ใจของ region ที่เกี่ยวข้อง | USER CONFIRMED สำหรับระบบสุดท้าย; palette/validity ยัง PROPOSED; ความยาว/ลายไม่ mandatory |
| REQ-05 | อธิบายความยากของภาพ | ขนาดคน การบดบัง การหลุดขอบ แสง/ชนิดภาพ | PROPOSED ข้อมูลวิเคราะห์ ไม่ใช่ output โมเดลบังคับ |
| REQ-06 | End-to-End จากภาพเต็ม | คนและ regions ตามขอบเขตที่ยังต้องกำหนด | USER CONFIRMED เป็นผลหลัก; metrics/eligible denominator ยัง PROPOSED |
| REQ-07 | Oracle analysis | ป้อนข้อมูลอ้างอิงเพื่อแยกผลของ parser ตาม protocol ที่จะออกแบบ | USER CONFIRMED แยกจากผลหลัก; crop/box/mask/input policy ยัง PROPOSED |
| REQ-21 | structured output และคำบรรยาย | สื่อ person/regions/สีและข้อจำกัดที่มีหลักฐาน | USER CONFIRMED ความสามารถระบบสุดท้าย; schema/description policy/ตัวชี้วัดยัง PROPOSED |

ไม่ผูก annotation กับการตรวจพบของโมเดลใด คนที่โมเดลพลาดยังต้องอยู่ใน denominator ของงานที่เข้าเกณฑ์ การทดสอบ attribute ใช้เฉพาะโมเดลที่รองรับ output นั้น และไม่รวมเป็นคะแนน Human Parsing เดียวโดยอัตโนมัติ

## 5. โครงสร้าง annotation เชิงความหมาย

REQ-08 (PROPOSED): แยกข้อมูลเป็นห้าระดับก่อนเลือก numeric ID

- ภาพ: image_id, source record, camera/site/time ถ้ามี, ขนาดจริง, hash, modality, curation status
- คน: image-local person_instance_id, geometry, visibility/truncation
- ส่วน: region_id, person_instance_id, semantic class, geometry, validity
- คุณลักษณะ: attribute_name, value, applicability, observability, reason
- ประวัติ: ผู้ทำ/ผู้ตรวจ, รุ่นคู่มือ/เครื่องมือ, วิธีสร้าง, revision, ผล QA

person_instance_id ภายในภาพไม่ใช่การยืนยันตัวตนข้ามกล้องหรือ cross-image identity

REQ-09 (PROPOSED): ใช้พื้นที่ที่มองเห็นเป็นฐานแรก ไม่วาดเติมส่วนที่ถูกบัง เว้นแต่ภายหลังสร้างงาน amodal แยกพร้อมหลักฐานและกติกาเฉพาะ พื้นที่เสาที่บังคนไม่กลายเป็นพิกเซลคน

REQ-10 (PROPOSED): แยก “ไม่มี”, “ใช้คุณลักษณะนี้ไม่ได้”, “มองไม่พอที่จะตัดสิน” และ “ยังไม่ได้ annotate” การ implement อาจใช้หลาย field ไม่จำเป็นต้องสร้างทั้งหมดเป็น semantic class ห้ามตีความ unknown เป็น background โดยอัตโนมัติ

REQ-11 (OPEN): นิยามคนรวมกระเป๋าถือ ร่ม หมวก อุปกรณ์ หรือสิ่งที่สัมผัสร่างกายเพียงใด ต้องเลือกให้เหมาะกับโจทย์ และเก็บ region แยกหากต้องรองรับหลาย evaluation view

## 6. หลักการเลือกคลาสและสี

REQ-12 (PROPOSED): ทุก candidate ต้องผ่านคำถามหกข้อ:

1. ช่วยตอบคำถามประเมินอะไร?
2. มีแหล่งอ้างอิงใด และหลักฐานสนับสนุนตรงเรื่องใด?
3. ขอบเขตไม่ทับซ้อน/ไม่ตกหล่นภายใต้ระบบที่เลือกอย่างไร?
4. ผู้ annotate สังเกตและแยกได้จากภาพจริงเพียงใด?
5. มีตัวอย่างเพียงพอต่อการประเมิน พร้อมรายงานความไม่แน่นอนหรือไม่?
6. เทียบกับ output ของโมเดลด้วย mapping แบบใดและสูญเสียอะไร?

ความหายากไม่ใช่เหตุผลอัตโนมัติให้ตัดคลาสสำคัญทิ้ง อาจเก็บเป็น exploratory class พร้อมข้อจำกัด

REQ-13 (PROPOSED): แยกสีแสดง mask, semantic color label และระบบพิกัดสีออกจากกัน เลื่อนการกำหนด palette/numeric ID จนความหมายคงที่
REQ-14 (OPEN): จะวัดสีที่ปรากฏในภาพหรือสีวัตถุจริง? ข้อเสนอเริ่มต้นคือสีที่สังเกตจากภาพเดียว พร้อมเงื่อนไข observability; ต้องทดลองในแสงต่าง ๆ และไม่อนุมานสีเสื้อจริงจากภาพ IR

ใช้ทะเบียนหลักฐานและสมมติฐานในเอกสาร 2; ตรวจเคสในเอกสาร 3 ก่อนยอมรับ candidate

## 7. การคัดภาพและความเป็นอิสระของชุดทดสอบ

REQ-15 (PROPOSED):

- เก็บ source → download → curation → annotation → QA → release เป็นสถานะแยก
- รักษา selected/rejected/flagged และ notes เดิม; เพิ่มผลทบทวนโดยไม่ลบประวัติ
- ตรวจ exact duplicates และกลุ่มภาพใกล้ซ้ำ/เหตุการณ์ต่อเนื่องก่อนแบ่ง pilot กับ final
- camera+time ใช้เสนอ candidate group ไม่ใช้ยืนยันบุคคลเดิมเพียงอย่างเดียว
- บันทึกว่าผลระบบเดิมมีส่วนในการคัดภาพหรือไม่; ไม่เปลี่ยนเป็นภาพคัดด้วยคนล้วนย้อนหลัง
- เก็บเหตุผลการยกเว้นรายงาน/รายคน/รายคุณลักษณะ เพื่อรายงาน coverage

REQ-16 (PROPOSED): ใช้ชุดพัฒนาคู่มือสำหรับแก้ ontology และ QA; แยก final test ตามกลุ่มเหตุการณ์ที่ตรวจแล้ว ตรึงโมเดล/adapter/protocol ก่อนประเมิน final ห้ามใช้คะแนน final ย้อนกลับมาเลือกคลาสเพื่อเอื้อโมเดล

การตรวจภาพโดย annotator เพื่อสร้าง GT ไม่ใช่การใช้คะแนน final เลือกโมเดล แต่ต้องแยกสิทธิ์/ประวัติการเห็นผล prediction เมื่อทำได้

## 8. การตรวจคุณภาพและกติกาคะแนน

REQ-17 (PROPOSED): ตรวจรูปแบบไฟล์และความสัมพันธ์ ID ทุกไฟล์ ตรวจ geometry อยู่ในภาพ ขนาดตรงต้นฉบับ และการ export/import ไม่เปลี่ยน class/owner/validity

REQ-18 (PROPOSED): เก็บ annotation อิสระก่อน adjudication สำหรับชุดตรวจความสอดคล้อง รายงาน agreement ตามคลาสและสภาพภาพ พร้อม confusion, unknown rate, coverage และภาระเวลา เลือกตัววัดให้ตรงชนิดข้อมูล ไม่ใช้คะแนนเดียวกลบปัญหาทั้งหมด หากมีผู้ทำคนเดียวให้เรียกการตรวจซ้ำว่า intra-annotator consistency

REQ-19 (PROPOSED): กำหนด metrics, matching, ignore policy, background inclusion, macro/micro averaging และ empty-image handling ก่อน final scoring

- semantic parsing: พิจารณา IoU รายคลาสและ mIoU พร้อมระบุวิธีรวม
- instance parsing: พิจารณา matching ระดับคนและคุณภาพ parts
- attributes: ประเมินบนหน่วยและ valid domain เดียวกัน พร้อม coverage
- pipeline: รายงานคนที่พลาด/ตรวจเกินแยกจากคุณภาพ parsing เมื่อพบคนแล้ว
นี่เป็นตัวเลือก ยังไม่ประกาศ protocol ที่อนุมัติแล้ว

REQ-20 (PROPOSED): annotation หลักสะท้อนงานและสิ่งที่เห็น ส่วน evaluation mapping เป็นอีกชั้นหนึ่ง ไม่แปลง coarse output ให้กลายเป็น finer label โดยไม่มีข้อมูล และไม่ตั้ง ignore domain ต่างกันรายโมเดลเพื่อให้คะแนนเทียบกันดูดีขึ้น

## 9. Decision status และสิ่งที่ยังต้องรู้

สถานะเปลี่ยนตามคำตอบใหม่หลัง eafe703 เท่านั้น ไม่ถามซ้ำว่า End-to-End/Oracle หรือสีอยู่ในขอบเขตหรือไม่

| ID | สถานะล่าสุด | สิ่งยืนยันแล้ว / สิ่งที่ยังต้องรู้ | ผลต่อขั้นถัดไป |
| --- | --- | --- | --- |
| DEC-01 | OPEN | source population/snapshot/curation linkage/สิทธิ์ยังขาดหลักฐาน | เตรียม sampling proposal ภายใน export ที่เข้าถึงได้พร้อมข้อจำกัด ไม่ประกาศประชากรทั้งระบบ |
| DEC-02 | USER CONFIRMED เป้าหมาย | parsing masks ขั้นต่ำ + สีบน–ล่างแบบมีเงื่อนไข + structured output/คำบรรยาย; attributes อื่นไม่ mandatory | ออกแบบ exploration ให้ตอบ requirement นี้ ไม่ถามขอบเขตซ้ำ |
| DEC-03 | PROPOSED วิธี/นิยาม | ต้องผูก owner ถูกต้อง; ขอบเขต person mask/อุปกรณ์/ชิ้นเดียว/เสื้อคลุมยังต้องดูภาพ | บันทึก ambiguity ก่อน taxonomy/guideline pilot |
| DEC-04 | PROPOSED นโยบายสี | ความสามารถสีบน–ล่างยืนยันแล้ว; observed/physical target, palette, unknown/multi-color ยังไม่ตรึง | สำรวจ readability/reason แยกจากการเดาค่าสี |
| DEC-05 | OPEN | ไม่มีคน/ยากมาก/ผลคัดเดิมและ notes ต้องมี linkage/ภาพรองรับ | ไม่ตัดภาพจาก pending/rejected เอง |
| DEC-06 | OPEN | จำนวนภาพสุดท้าย กำหนดส่ง ผู้สำรวจ/ผู้ทบทวน กำลังคนและเวลา | 32 เป็นงบทดลองที่เสนอ ไม่ใช่โควตาหรือประมาณแรงงานทำ masks |
| DEC-07 | PROPOSED | taxonomy/coarse-fine/side, annotation method, metrics/QA | exploration ช่วยตั้งสมมติฐาน ไม่ให้ agreement/เกณฑ์คุณภาพโดยอัตโนมัติ |
| DEC-08 | USER CONFIRMED บทบาทผล | End-to-End หลัก; Oracle วิเคราะห์แยก | exact Oracle input/crop transform/metrics ยัง PROPOSED |
| DEC-09 | PROPOSED | แยก discovery/protocol exposure จาก final และเก็บ duplicate/group uncertainty | รอบนี้ไม่กำหนด Final Test หรือ splits |

### ช่องว่างที่ยังหาไม่ได้จากไฟล์

- หากมี original curation export/notes/source dictionary ให้ระบุ path ภายหลัง; ขณะยังไม่พบให้คง missing ไม่หยุดเตรียม manifest และไม่เอา pending ทับผลเดิม
- ผู้รับผิดชอบสำรวจและทบทวน กำหนดส่ง กำลังคน เวลา และจำนวนภาพสุดท้ายยัง OPEN ต้องทราบก่อนจัดคิวทำภาพจริง ไม่ต้องตัดสิน taxonomy/QA ขั้นสุดท้ายตอนนี้

## 10. เกณฑ์จบช่วง foundation

สามารถเริ่ม pilot ได้เมื่อมีภาพที่เชื่อม source ได้ มีร่างนิยาม candidate ครบขอบเขต มีรายการกรณีที่ต้องทดสอบ มีผู้ทำ/ผู้ตรวจที่ระบุจริง และมีแผนบันทึกผลก่อนแก้คู่มือ

ยังไม่ต้องเลือกเครื่องมือถาวรหรือมีจำนวนคลาสสุดท้ายในขั้นนี้ การตัดสินใจใหม่บันทึกวัน เหตุผล หลักฐาน ผู้ตัดสิน และผลกระทบต่อไฟล์/คะแนน
