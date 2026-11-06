# แผน annotation pilot และ QA ทดลอง v0.1 — PROPOSED

## เพิ่มเติม 6 พฤศจิกายน 2026 — เตรียม scripts แล้ว ยังไม่เปิด pilot

ใช้ [scripts person + 4 parts](../docs/ANNOTATION_GUIDELINE_V0_2_TH.md#person-part-pseudolabel) ตามคำชี้แจงผู้ใช้ ไม่พัฒนาGUIใหม่ มีcandidatequeue24ตามกล้องแต่ยังต้องยืนยันvisualcoverage/human-firstก่อนfreeze; nohardpixeldeletion, helperSAM3แยกจากผู้เข้าสอบแต่ไม่รับรองarchitecture/trainingindependence CPUfixtures14ผ่านและprecheckจริงผ่านimports/inputs/weightsbindings ไม่มีGPUmodelcalls ไม่ถือว่าnativeSAM3personหรือpartqualityผ่านแล้ว ข้อความประวัติด้านล่างที่บอกยังไม่มีtoolsต้องอ่านคู่กับสถานะนี้

## แผน pilot ปัจจุบัน — 4 พฤศจิกายน 2026

อ่าน [คู่มือสั้นและกฎขนาดคน/การใช้pseudo-labels](../docs/ANNOTATION_GUIDELINE_V0_2_TH.md) ประกอบ: pilotต้องได้maskที่ใช้ต่อได้, เก็บขนาดจริงจากmask, ไม่ตีความขนาดเป็นระยะเมตร และไม่จำกัดGTตามคนที่detectorพบ

ผู้ใช้เลือก workflow pilot **24 ภาพ** แล้วขยายเป็น **300 ภาพรวม pilot** แทนข้อเสนอ 8 ภาพเดิมด้านล่าง รายชื่อยัง NOT_SELECTED และยังไม่เริ่ม annotation เสนอ 6 calibration + 18 workflow โดยเลือก 6 ใน workflow ให้ผู้ใช้ทำจาก RGB ก่อนเห็น AI draft ไม่มีการประเมินจากผลโมเดลเพื่อเลือกภาพ

| Gate | หลักฐานก่อนเดินต่อ |
| --- | --- |
| Membership | 24 unique pixel groups ที่เปิดต้นฉบับแล้ว พร้อม coverage/เหตุผลเลือกและประวัติเห็นข้อมูล; ไม่อ้างว่าเป็น sample แทนประชากรทั้งหมด |
| Annotation contract | กติกา 4 targets/auxiliary/owner/unknown/color มี revision ชัด; ห้ามทำ unknown เป็น BG, เติมส่วนซ่อน หรือตัด dress ด้วย heuristic |
| Tool readiness | export/import รักษาขนาด orientation holes disjoint parts owner และ unknown; synthetic expected masks ไม่ผูกกับ logic ของ exporter; ต้องทดลอง GUI/API จริง |
| AI draft | บันทึก model/checkpoint/source/prompt/config/device/calls/error; ร่างแยกจาก HUMAN_REVIEW ไม่ auto-accept |
| Human review | ผู้ใช้ตรวจทุกภาพ แยก NEEDS_FIX กับ ACCEPTED; 6 ภาพ blind เก็บผลก่อนเห็น AI และก่อน adjudication ไม่อ้าง independent annotators สองคน |
| Pilot closure | รายงานปัญหา mask/class/owner/color, เวลาเครื่องและเวลาคนที่วัดจริง, corrections และผลกระทบของ rule revisions; ไม่มีเกณฑ์ agreement ที่แต่งเป็นมาตรฐาน |
| ขยายงาน | freeze คู่มือหลังแก้ปัญหา pilot; ทำ batches 20 พร้อม checkpoint ไม่เปิดทั้ง 2,200 โดยอัตโนมัติ |

ข้อเสนอ 24 dev + 276 evaluation ยังไม่ใช่ split ที่รับรอง ต้องตรวจ duplicate/event/exposure และใช้กฎเดียวกันก่อน release สถานะทำงาน DRAFT → HUMAN_REVIEW → NEEDS_FIX หรือ ACCEPTED; checksum ผ่านอย่างเดียวไม่ให้ ACCEPTED

## แผนและคำถาม v0.1 เดิม — ประวัติ

ปรับแบบฟอร์ม QA เดิมเป็นแผนที่ตรวจทานได้ ยังไม่เริ่ม annotation จริง ไม่กำหนดเกณฑ์ agreement/คะแนนผ่าน จำนวน Final Dataset หรือ Final Test ผู้ทำ ผู้ตรวจ เวลา และกำหนดส่ง **OPEN**

## 1. ประเด็นตัดสินก่อน pilot เรียงตามผลกระทบ

ทุกแถวรอมนุษย์ทบทวน ข้อเสนอไม่ใช่คำตอบที่อนุมัติ หลักฐาน/Exploration IDs/locator อยู่ใน review packet ภายในตาม rule IDs ของ [คู่มือ v0.1](annotation_guideline.template.md)

| ลำดับ | Rule | เรื่องที่ต้องตัดสิน | ข้อเสนอพร้อมทบทวน / สิ่งที่ต้องรู้ก่อนทำจริง |
| --- | --- | --- | --- |
| 1 | R01/R02 | person mask scope: body/clothes/อุปกรณ์ | ทดลอง base view + accessory relation; ผู้ทบทวนต้องระบุ bag/headwear/สิ่งถือรวมใน view ใด ไม่เลือกตาม output โมเดล |
| 2 | R03/R07/R09 | partial/occluded/black region กับ validity | คง partial person และ valid regions; state/ignore policy แยก ไม่ใช้ส่วนที่หายเป็น background หรือ absent |
| 3 | R04/R11 | owner และ person IDs | image-local refs; unknown owner ไม่เดา ไม่ใช้ temporary locator/category เป็น GT ID; ต้องได้วิธีรักษา refs ในเครื่องมือ |
| 4 | R05 | outer layer/one-piece และ upper/lower | คง unresolved garment extent จนมีกฎและหลักฐาน; เคส one-piece ชัดยังขาด ไม่สร้างเส้นแบ่งสมมติ |
| 5 | R06 | footwear/bare foot/sandal | ดู material ที่เห็นกับผิวแยก; no view ไม่ใช่ absent; ยังต้องตัวอย่างชัด/มนุษย์ตรวจ |
| 6 | R08 | apparent color / multi-color / no answer | สีบน–ล่างเป็นเป้าหมายยืนยันแล้ว แต่ palette/หลายชั้น/unknown rule ยังเสนอ ไม่ถามความจำเป็นสีซ้ำ |
| 7 | R10 | blur/ghosting boundary | uncertain boundary + adjudication ร่าง; ยังไม่ตั้งขอบนอกสุดหรือ threshold สากล |
| 8 | R12 | geometry/export representation | ตกลง original-coordinate master และ transform chain; ทดสอบ file/GUI จริงก่อนใช้ annotations จริง |
| 9 | ทุก Rule | เครื่องมือ/ผู้ทำ/ผู้ตรวจ/เวลา | ยังไม่เลือกเครื่องมือถาวรหรือระบุคนแทนผู้ใช้; inventory ปัจจุบันยังไม่มี GUI ที่ตรวจใช้งานได้ ต้องรู้ทรัพยากรก่อนจัดคิว pilot |

## 2. คำถามที่ pilot ต้องตอบ

- ผู้ทำเข้าใจ person/part/owner/validity เหมือนกันหรือไม่ และความขัดแย้งมาจากนิยาม ภาพ เครื่องมือ หรือการพลาดงาน?
- กฎทำให้คงข้อมูล partial person ได้เพียงใดโดยไม่เพิ่ม unsupported guesses? unknown/ignore มีเหตุผลตรวจย้อนกลับหรือกลายเป็นการหลบภาพยาก?
- bag/ชั้นเสื้อ/one-piece/sandal/ghosting มีภาระและความไม่แน่ใจอย่างไร ต้องแก้คู่มือหรือเพิ่มตัวอย่างใด?
- เครื่องมือเก็บ geometry/IDs/owner/states/display-color separation ได้ครบหรือมีการสูญข้อมูลระหว่างส่งออก?
- schema เก็บ structured facts/claim refs และเหตุผลที่ไม่ให้คำตอบพอรองรับคำบรรยายที่ไม่เติมรายละเอียดเกินภาพหรือไม่? รอบเตรียมนี้ยังไม่มี description GT หรือผล caption model
- เวลาเรียนเครื่องมือ ทำแต่ละคน/region ตรวจ และแก้ไขจริงเป็นเท่าใด? ไม่ใช้เวลา AI exploration ทำนายแรงงาน annotation มนุษย์

## 3. ขนาดและวิธีเลือกเริ่มต้นที่เสนอ

เสนอ **8 unique payloads** จากชุดทบทวนที่มีอยู่เพื่อทดสอบ workflow รอบเล็ก ครอบคลุม baseline upper/lower/color, หลายชั้น/owner, บัง/overlay, ghosting, รองเท้า/เท้าเปล่า และ bag/truncation เหตุผลคือมีแต่ละกลุ่มปัญหาให้ทดลองโดยยังจำกัดภาระ ไม่เป็น statistical sample size หรือโควตาที่อนุมัติ จำนวน/เวลาจริงอาจเปลี่ยนตามผู้ทำและความซับซ้อนของคนในภาพ

เสนอแบ่งเป็น 2 ภาพ calibration ที่เรียน/อภิปรายกติกา และอีก 6 ภาพสำหรับ independent first pass เมื่อมีผู้ทำหลายคน ภาพ calibration ไม่ใช้รวมเป็นหลักฐาน independent agreement จัดลำดับและบันทึก seed เมื่อกำหนด run จริง รายชื่อ/เหตุผล/coverage ร่างอยู่ภายนอก Git ไม่มี pilot membership ที่ตรึงแล้วและไม่มี annotation จริงรอบนี้

ชุดนี้เป็น protocol development ที่มี exposure แล้ว ไม่เรียกว่า unseen/Final Test ต้องพิจารณาภาพซ้ำและกลุ่มบริบทก่อนจัด final ภายหลัง โดยยังไม่ตัดสิน final split หรือบังคับ train/validation/test

## 4. ขั้นทำงานเมื่อพร้อมเริ่มจริง

1. **Human review ก่อน:** กรอกตัวเลือก/เหตุผลใน decision sheet ทบทวนข้อที่กระทบ mask support/validity/owner มากก่อน กฎที่ยังไม่ได้ข้อยุติให้มี pilot alternative/uncertainty ที่เขียนไว้ ไม่เปลี่ยนเงียบ ๆ
2. **Tool rehearsal ด้วย synthetic:** ใช้ schema draft ทดสอบ import/export ใน GUI ที่เลือกจริงก่อน ขณะนี้ผ่านเฉพาะ Pillow PNG + JSON และ point transforms ไม่มีผล GUI export/import ที่อ้างได้
3. **Training/calibration:** ฝึกเครื่องมือและอ่านคู่มือ เก็บเวลา/คำถามต่างหาก ยังไม่ให้ model predictions เป็นคำตอบอ้างอิง ระบุว่าภาพใดได้เห็นตัวอย่าง/คำตอบร่วม
4. **First pass:** คนที่ทำอิสระเก็บผลก่อนเห็น annotation ของอีกคน ผูก image/person/region และเหตุผล unknown แต่ละ task อย่าตัดคนเพียงเพราะ footwear/color ไม่ครบ
5. **Structural QA:** dimensions/refs/ownership/code values/validity/coordinates กับ roundtrip artifacts ตรวจแยกจาก semantic correctness แล้วให้คนทบทวนเนื้อหา
6. **Disagreement review:** เก็บผลก่อนคุยกัน ระบุชนิด disagreement/ผู้ตัดสิน/หลักฐาน บันทึกผล adjudication แยก ไม่ลบผลเดิมหรือเรียก consensus ว่า independent agreement
7. **Revision:** เปลี่ยน guideline version และ annotation revision พร้อม affected rule/image/person/region refs; ถ้ากฎเปลี่ยนให้เก็บเวลาแก้และเหตุผล ไม่เปรียบเทียบ agreement คนละ guideline โดยไม่แยก

## 5. หน่วยบันทึกและการจับเวลา

| หน่วย | สิ่งที่ต้องเก็บใน private pilot run เมื่อเริ่มจริง |
| --- | --- |
| run/image | source/hash, guideline/tool/config version, selection/exposure, จำนวน candidates/regions ตามนิยาม และข้อที่ไม่แน่ใจ |
| person | image-local ID, locator ref เดิมถ้ามี, visible/partial support, owner/occlusion/truncation และ task validity |
| region/attribute | target/geometry/owner/value state/reason, ขอบหรือคำถามกำกวม, review/revision refs |
| ช่วงเวลา | stage = training / annotation / self-check / independent review / adjudication / revision; start-stop/pause/resume และ actor จริง |
| QA/revision | checks ที่ผ่าน/ผิด, ข้อขัดแย้งก่อนคุย, ผู้ตัดสิน, เหตุผล/ผลกระทบของการแก้และเวลาที่ใช้ |

แยก active time กับ elapsed/pause และ tool CPU time งานซ้อน image/person/region ไม่บวกซ้ำ: ใช้ exclusive stage intervals เป็นฐานแรงงานรวม ส่วน person/region intervals เป็น breakdown ที่เชื่อม parent เวลาใดไม่วัดให้ null ไม่สร้างย้อนหลัง และไม่รวม training/review เข้า annotation-only time โดยไม่ระบุ

## 6. หลายคนกับคนเดียว

ถ้ามีหลายคนและทำ first pass แยกได้ จึงวิเคราะห์ความต่าง label/geometry/owner/validity พร้อม coverage, confusion และเวลา ต้องตกลงวิธี matching/domain/ignore ก่อน scoring ไม่มี universal threshold ที่กำหนดในเอกสารนี้

ถ้ามีผู้ทำคนเดียว ให้ repeat subset ในรอบแยก/ลำดับที่บันทึกและซ่อนผลเดิมเมื่อทำได้ ระบุ memory/prior exposure เรียก intra-annotator consistency ไม่ใช่ inter-annotator agreement/independent review การตรวจ structural หรือการให้ Codex อ่านภาพไม่ประเมิน shared bias หรือความถูกต้องของมนุษย์ได้ ต้องคงข้อจำกัดและรอผู้ตรวจอิสระ

## 7. เหตุผลให้ขยาย/แก้แผนและช่องว่าง

ขยายเฉพาะเมื่อเคส/กฎยังไม่ถูกทดสอบ export สูญข้อมูล หรือ ambiguity ใหม่ทำให้กฎใช้ไม่ได้ โดยระบุเหตุผลและเวลาจริง ไม่เพิ่มตามตัวเลขอัตโนมัติ ปัญหา one-piece ที่เห็นเต็มตัว รองเท้า/เท้าเปล่าหลายมุม known modality/สีภายใต้แสง และกลุ่มกล้องที่ขาดยังต้องแผนสำรวจใหม่ ไม่มีการเปิดภาพเพิ่มในรอบเตรียมคู่มือนี้

ก่อนเริ่มต้องมีผู้ทำ/ผู้ตรวจ (หรือแผนคนเดียวพร้อมข้อจำกัด), เครื่องมือที่ทดสอบ format จริง, data access ที่ใช้ได้ และคู่มือ/ทางเลือกที่มนุษย์ทบทวนแล้ว จำนวนคน เวลา และกำหนดส่งยัง OPEN ไม่ถือว่าเอกสารพร้อมคือเริ่ม pilot ได้ทันที


## เคสต้องครอบคลุมเพิ่มจาก intake รอบต่อ — PROPOSED

ก่อน freeze pilot ให้ผูก [N01–N06](../docs/CASE_REGISTER_DRAFT_TH.md#ข้อสังเกตภาพจริงรอบต่อ--4-พฤศจิกายน-2026) กับรายชื่อ private: near-monochrome แยกจาก IR ที่ยืนยันแล้ว, source overlays, reflection, โครงสร้างบัง/ท่าก้ม, motion blur/หลุดขอบ, คนชิดกัน และ uncertain presence ตัวอย่าง6ภาพที่ตรวจนี้ยังไม่ใช่ pilot membership โดยอัตโนมัติ

ตรวจว่า GUI/export รักษา scene/task validity ของ reflection/contaminated pixels แยกจาก class/owner และผู้ใช้มองเห็นเหตุผลของ unknown; ต้องไม่เปลี่ยน pixel validity ตามโมเดล และไม่ตัดทั้งคนเพราะสีระบุไม่ได้ หาก coverage บางกรณีไม่มีในข้อมูลที่ตรวจ ให้รายงานช่องว่าง ไม่เติมว่า FOUND เพื่อให้ครบตาราง
