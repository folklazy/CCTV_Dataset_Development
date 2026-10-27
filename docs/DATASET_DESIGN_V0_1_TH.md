# Dataset Design v0.1 — ข้อเสนอของโครงการ (PROPOSED)

ร่าง 27 ตุลาคม 2026 จาก requirements ที่ยืนยันแล้ว การตรวจไฟล์ทั้ง export และข้อสังเกตภาพจริงที่มี provenance ไม่ใช่ taxonomy ของ CCIHP/โมเดล และไม่ใช่ specification ที่ผู้ใช้อนุมัติแล้ว **การคัดกรองภาพทั้งชุดยังไม่เสร็จ** ดูจำนวนล่าสุดใน [รายงานสถานะ](../reports/README.md) และ private checkpoint ห้ามตีความการตรวจ decode ครบว่าเปิดดูครบ

เอกสารนี้เสนอคำตอบด้านโครงสร้างที่นำไปวางแผนได้ทันที โดยไม่รอผล annotation agreement หรือเวลาทำ mask ซึ่งยังไม่ได้วัด หลักฐานภาพ/IDs และความไม่แน่ใจรายกรณีอยู่ใน private evidence binding ไม่เผยแพร่ภาพ/metadata/paths บริษัท

## 1. เป้าหมายและสิ่งที่ยืนยัน

End-to-End จากภาพเต็มเป็นผลหลัก; Oracle แยกวิเคราะห์ ขั้นต่ำมี person instance/mask และ upper/lower/footwear masks ที่ผูก owner ถูกต้อง สีบน–ล่างเมื่อสังเกตได้ และ structured output/คำบรรยายเป็นความสามารถระบบสุดท้าย Attributes เพิ่มยังไม่ mandatory

ล่าสุดผู้ใช้อนุญาตตรวจไฟล์/ภาพทั้ง current dataset แบบ read-only และขอแผนชุดประมาณสองพันกว่าภาพ ไม่เกินสามพัน นี่คือกรอบคัดชุดพัฒนา/ประเมินที่เสนอ ไม่ใช่จำนวน Final Dataset ที่ตรึงหรือ Final Test ไม่มี annotation/pilot/inference/training/benchmark ในงานนี้

## 2. Mask classes ที่แนะนำ

เสนอ **6 core parsing classes** และ **1 auxiliary object class** IDs ต่อไปนี้เป็น proposed IDs ไม่ใช่สีแสดง mask และไม่ใช่ IDs ของ benchmark อื่น หลักฐานรายภาพผูก C01–C06/A101 ในเอกสารภายใน ความชัดของ class presence, mask boundary และ attribute แยกประเมินกัน

| Proposed ID | ชื่อ | รวม / ไม่รวม | ขอบเขตและเหตุผล |
| --- | --- | --- | --- |
| 1 / C01 | `head_region` | หัวที่เห็น รวมผม/หน้าและสิ่งสวมติดศีรษะ เช่นหมวกใน composite view; ไม่รวมวัตถุที่เพียงบังหัว | ใช้ coarse head support ก่อน ไม่บังคับแยก face/hair/hat/eyes หรือซ้าย–ขวาในภาพที่รายละเอียดจำกัด ชนิด headwear เป็น optional attribute ห้ามเติมส่วนหัวที่ซ่อน |
| 2 / C02 | `exposed_body` | ผิวกายที่เห็นนอก head_region เช่น torso/แขน/มือ/ขา/เท้าเปล่า; ไม่รวมเสื้อผ้า รองเท้า หรือถุงเท้า | รองรับลำตัวเปลือยและ skin ที่ลอด sandal โดยไม่เรียกเป็น background ไม่บังคับ fine limb labels/side หรืออนุมานข้อต่อที่ไม่เห็น |
| 3 / C03 | `upper_garment` | เสื้อ/ชั้นผ้าที่สวมช่วงบนที่ระบุได้ เช่น shirt/T-shirt/jacket/vest; ไม่รวมกระเป๋าหรือสิ่งถือที่สีใกล้กัน | ใช้เฉพาะ visible fabric ของแต่ละ garment layer เก็บ layer relations; long garment ที่ยืนยันว่าข้ามช่วงตัวใช้ C05 ไม่ตัดตามสัดส่วนเอวสมมติ |
| 4 / C04 | `lower_garment` | กางเกง ขาสั้น กระโปรงและวัสดุเสื้อผ้าช่วงล่างที่ระบุได้; ไม่รวมผิวขา footwear ถุงเท้า หรือ accessory ที่ยังแยกประเภทไม่ได้ | ประเภท pants/skirt/shorts เป็น attribute ไม่สร้างคลาส geometry หลายชุดก่อนมีเหตุผล ต่างคน/ต่าง garment มี region refs แยก แม้ class เดียวกัน |
| 5 / C05 | `cross_zone_garment` | garment ที่มีหลักฐานว่าครอบคลุมช่วงบนและล่าง เช่น dress/robe/coverall/long outer garment; ไม่ใช่ที่ทิ้งทุก region ที่ไม่รู้ | เก็บขอบผ้าต่อเนื่องทั้งชิ้นเมื่อยืนยัน cross-zone/type ได้ หากยังไม่รู้ชนิดหรือจำนวนชิ้น ให้ semantic state=unknown พร้อม candidate concepts ไม่ใส่ C05 เพื่อเลี่ยงความไม่แน่ใจ หลักฐานปัจจุบันมีเคสต่อเนื่อง/ทรงยาว แต่ garment construction บางเคสยังไม่ยืนยัน |
| 6 / C06 | `footwear` | วัสดุ shoe/boot/sandal/flip-flop ที่เห็น; ไม่รวมช่องที่เห็นผิวเท้า ถุงเท้า หรือพื้น/เงา | รวมชนิดรองเท้าเป็น class เดียวก่อน เก็บ subtype ถ้าอ่านได้ ไม่แยกซ้าย–ขวาบังคับ และไม่ให้ footwear absent เพราะเท้าถูกบัง/หลุดขอบ |
| 101 / A101 | `associated_object` — auxiliary | กระเป๋า/เป้/อุปกรณ์สะพายและสิ่งถือที่สัมพันธ์กับคน; ไม่ใช่ human-part class | เสนอ geometry เฉพาะเมื่อจำเป็นต่อ person boundary/owner/สี ไม่บังคับ annotate ทุก object ในฉาก เก็บ `worn/carried/held/unknown` และ owner validity แยก ห้ามแจก owner จากระยะใกล้ที่สุด |

**ข้อเสนอที่ยังไม่รับเป็น core class:** fine hair/face/eyes/limbs/left-right, ชนิดเสื้อทุกแบบ, coat subclass, รองเท้าแต่ละชนิด, กระเป๋าแต่ละชนิด และคลาสสี เหตุผลคือไม่ได้เป็นข้อกำหนดขั้นต่ำและความละเอียดที่อ่านได้ต่างกันมาก ไม่ใช่การอ้างว่าสิ่งเหล่านี้ไม่มีใน dataset

**Socks/gloves/ชิ้นสวมเล็ก:** แนะนำบันทึก visible worn-item support/ชนิดที่อ่านได้ใน auxiliary relation ก่อน ไม่ผสม sock กับ footwear/skin หรือเติม class จากรูปลักษณ์ที่อ่านไม่พอ หากหลักฐานทั้งชุดรองรับการแยก sock mask อย่างสม่ำเสมอ ให้เสนอ ontology revision เพิ่มโดยไม่เปลี่ยน ID เดิม รอบนี้ยังไม่มีหลักฐาน native ที่ชัดพอสำหรับตัดสิน sock core class ไม่อ้างว่าไม่พบ socks ทั้งประชากร

ชิ้นสวมที่ทราบว่าอยู่นอก core vocabulary ยังอยู่ใน visible person support ได้ เก็บ `semantic_assignment=outside_core_vocabulary` พร้อมชนิด/เหตุผลเมื่อทราบ แยกจาก `unknown` ที่ยังไม่ทราบชนิด ไม่ใช้ storage 0 ของส่วนนี้ยืนยัน background และไม่ให้สีถุงเท้ากลายเป็นสีของ lower primary garment

## 3. Person, geometry และ ownership

- `image` มี source record ref, encoded-payload SHA256, decoded-pixel hash พร้อมวิธี/decoder, dimensions และ EXIF/orientation การตรวจพบขนาดภาพหลายแบบห้ามใช้ constant dimensions หรือถือทุกไฟล์เป็น full frame
- `person_id` เป็น image-local ID เมื่อเริ่ม annotation จริง ไม่ใช่ temporary locator, category, detector order หรือ identity ข้ามภาพ ในรอบสำรวจใช้ record/locator refs เท่านั้น
- `person_mask` เก็บ visible person support แยกจาก parsing labels รวมร่างกายและเสื้อผ้าที่สวม/footwear/headwear แต่แยก bag/held equipment; ไม่เติมร่างกายใต้สิ่งบัง การขาด class assignment บนพิกเซลคนไม่ทำให้พิกเซลนั้นเป็น background
- `bbox_visible` แนะนำ derive tight box จาก visible person mask ในอนาคต หรือเก็บวิธีสร้างชัดเจน ต่างจาก amodal box และ display crop rectangle ที่ไม่ใช่ GT
- `region_id` เชื่อม geometry → class/state → owner เมื่อ known; owner unknown เป็น null พร้อม candidates/reason ไม่มี person ปลอมมาเติมช่อง และไม่ merge คนให้ export ง่าย
- geometry master อยู่ใน original encoded-pixel coordinates เก็บ original dimensions, orientation และ crop/scale/padding/affine chain ทุกขั้น ตรวจ inverse จุดและ dimensions; การ inverse พิกัดไม่คืนรายละเอียดที่สูญจาก downsample

เสนอ visible semantic view ให้แต่ละ valid pixel มี topmost material class ของ owner ที่มีหลักฐานเพียงค่าเดียว ไม่วาด inner garment ทับตำแหน่งที่ outer บัง Layer relation เชื่อมเฉพาะชิ้น/ส่วนที่เห็น และคง unknown หากแยก garment identity ไม่ได้ Person support อาจมี core-class coverage ไม่ครบจาก outside-vocabulary/unknown โดยเก็บ validity แยก ช่องว่างนี้ไม่ใช่ scene background

เสนอ canonical binary masks ต่อ person/region พร้อม JSON relations/validity แล้วค่อยสร้าง semantic/instance rasters เป็น derived views เมื่อ represent uncertainty ได้ครบ ไม่ผูก schema กับ polygon-only/COCO/YOLO export ขณะยังไม่ทดสอบ format จริง

หากวัด scale ให้เก็บ visible extent ใน original pixels พร้อม locator/วิธี/ความไม่แน่ใจ แยก full-body height ที่คาดเดาออกเป็นคนละ field และคง null หากไม่ได้วัด ไม่มีการแปลงเป็นเมตรเมื่อไม่มี calibration และไม่รับ 30/50/100 px เป็นเกณฑ์คุณภาพอัตโนมัติ

## 4. Background, validity และสถานะที่ไม่ใช่ class

| แกน | ความหมายที่เสนอ |
| --- | --- |
| presence | present / absent / unknown; absent ต้องมีหลักฐานเชิงบวก เช่นบริเวณลำตัวเปลือยที่เห็น ไม่ใช่ mask ว่าง |
| visibility | visible / partial / occluded / out_of_frame / unknown; แยกสิ่งบังกับการตัดขอบ |
| maskability | boundary_supported / partially_supported / unresolved / not_assessed; คนมีอยู่ไม่แปลว่าทุกขอบ mask อ่านได้ |
| attribute readability | readable / partial / unobservable / unknown / not_assessed; สี/ชนิดอ่านได้ไม่เท่ากับขอบ mask อ่านได้ |
| workflow | not_reviewed / overview_reviewed / detail_reviewed และ not_annotated / draft / reviewed แยกคนละกระบวนการ |
| semantic/owner assignment | known / unknown พร้อม reason/candidates; ไม่ใช่ semantic class `unknown` |
| evaluation disposition | UNDECIDED จนมี policy; ignore/background/exclude เป็นนโยบายและ support ที่บันทึกแยก ไม่ใช่ taxonomy classes |

ค่า storage 0 หรือ mask support=0 ต้องมี encoding/validity metadata กำกับ ไม่แปลพร้อมกันว่า scene background, absent, unknown และยังไม่ทำ Source black regions, text/boxes/overlays, saturation, blur และ ghosting ต้องบันทึก loss/uncertainty ไม่ถือกรอบฝังมาเป็น GT หรือสังเคราะห์ส่วนที่หาย

## 5. การรองรับ upper/lower/footwear และ attributes

| Requirement | สิ่งที่ schema รองรับ / ข้อจำกัด |
| --- | --- |
| End-to-End หลัก | เก็บคนทุกคนที่มีหลักฐานโดยไม่ขึ้นกับ detector; image_scope และ eligible/task validity แยก ภาพจัดกรอบใกล้คนไม่กลายเป็น full-scene evidence โดยอัตโนมัติ |
| upper/lower | visible C03/C04 เป็น direct garment views; C05 เก็บ cross-zone extent และ mapping status หากต้อง anatomical upper/lower view ให้ใช้ landmarks/ขอบที่มีหลักฐานพร้อม uncertainty ไม่ใช้ fixed waist fraction หรือวาด mask ซ้ำทั้งชิ้นให้สอง class |
| ข้อจำกัด C05 | ถ้าไม่เห็นเส้นแบ่งที่รองรับ ให้ upper/lower projection unresolved และคง C05/person geometry พร้อมรายงาน task coverage; ไม่ประกาศ masks ครบทุก task ของคนนั้นอย่างไม่จริง |
| footwear/owner | material C06 กับ person ref และ validity; ผิวเท้าไป C02 ไม่มีภาพเท้า→unobservable ไม่ใช่ absent; unresolved owner ไม่เท่ากับ no person |
| สีบน–ล่าง | `apparent_color` ผูก visible garment/layer support + value_state/reason; upper/lower color view อ้าง region refs ที่เกี่ยวข้อง ไม่ใช้สี bag/headwear แทนเสื้อ ไม่เดาสีวัตถุจริงจาก grayscale/แสง cast |
| หลายสี/ชั้น | รายการ color components และ layer refs ไม่มีจำนวนสี/เปอร์เซ็นต์ dominant ที่ตรึง สี UI palette แยกจาก attribute values ถ้าอ่าน hue ไม่ได้อาจเก็บ intensity observation แยกโดยไม่ตั้ง hue ปลอม |
| attributes เพิ่ม | garment/footwear/headwear subtype, length/pattern เป็น optional พร้อม observability/reason ไม่เป็น class label ของบุคคลตาม category |
| structured output/คำบรรยาย | image/person/region/attribute/relation refs และ claim refs; สื่อ unknown/absent/unobservable ตามเหตุผล ไม่เติม role/identity/สีที่ไม่ได้สังเกต ยังไม่มี description GT |

## 6. แผนคัดประมาณสองพันกว่าภาพ ไม่เกินสามพัน — PROPOSED

เสนอ **2,400 unique decoded-pixel groups เป็นจุดตั้งต้นสำหรับวางแผน** ปรับได้ในกรอบผู้ใช้ ไม่ใช่ Final Test/โควตาย่อยหรือการคำนวณ statistical power จำนวน 2,400 เป็น operating target เพื่อให้เสนอแผนที่รันได้ ไม่ใช่จำนวนที่พิสูจน์ว่าเหมาะที่สุด

1. ใช้ file-readable inventory และ duplicate groups ปัจจุบันเป็น sampling frame คงทุก filename/source record และ curation history; candidate unit คือ unique image content ไม่ใช่จำนวน metadata rows
2. สร้าง coverage matrix ตาม site-camera, calendar period ของ timestamp ที่เก็บ raw และ record-category ซึ่งไม่ใช่ person class ผูกทุก alias กลับหลาย strata ได้โดยไม่เลือก payload ซ้ำ
3. ใช้ greedy coverage-first เลือกกลุ่มที่เติม strata/สภาพภาพที่ยืนยันจากการเปิดจริงได้มากก่อน แล้วกระจายส่วนที่เหลือด้วยน้ำหนัก `sqrt(n_camera)` และ seed ที่บันทึก เพื่อลดการครอบงำของกล้องข้อมูลมาก รายงาน inclusion/ranking rule ชัด ไม่เรียกว่าตัวแทนสุ่มเท่ากันของประชากรทั้งหมด
4. ส่วน case diversity ใช้ tags จากภาพจริง เช่น cross-zone garment, skin/garment, layer/object ambiguity, multi-person ownership, partial body, footwear และ color limits ไม่มีโควตาต่อ tag ที่ตรึงจากตัวอย่างน้อย
5. near-duplicate hash similarity และ camera-time proximity ส่งเข้า review queue เท่านั้น ดู motion/appearance/context ก่อนลดความซ้ำเชิงบริบท ไม่สรุป same person/event หรือคัดออกอัตโนมัติ ไม่ใช้ gap scenario เป็น burst truth
6. เมื่อได้ candidate ranking ให้ตรวจ coverage ใหม่และบันทึกเหตุผลเติม/ลด/คงเคส ไม่ตัดคนเล็ก/partial ทั้งภาพเพราะบาง task ทำไม่ได้ คงภาพยากที่ตอบบาง requirements ได้ พร้อม validity

การคัดกรองทั้งชุดยังไม่เสร็จ จึงยังไม่สร้าง membership 2,400 ภาพหรืออ้างความถี่ visually tagged cases ของทั้งประชากร การแก้จำนวนในกรอบถึง 3,000 ต้องอิง diversity/coverage ที่ยังเพิ่มจริง ไม่ใช่เพิ่มใกล้ซ้ำให้ครบยอด และไม่สรุปว่าลดเหลือเป้าหมายได้จาก exact duplicates เพียงอย่างเดียว

## 7. วิธีวิจัยสำหรับนำไปเขียนรายงาน

งานใช้กรอบข้อมูลที่เข้าถึงได้จาก metadata export และ split archive ปัจจุบัน ตรวจความสอดคล้อง CSV/JSON/XLSX, unique filenames และ record-to-member linkage ก่อนอ่านภาพแบบ read-only เก็บ hashes/CRC/decode/dimensions ต่อ payload และแยก byte duplicates ออกจาก equality ของ decoded pixels ด้วยนิยาม decoder/mode/orientation ที่ทำซ้ำได้ ภาพซ้ำมี representative และ alias provenance โดยไม่ลบต้นฉบับ

การสำรวจภาพแยก overview screening จาก native-resolution detail review ภาพย่อ/contact sheet เป็นเครื่องมือจัดลำดับ ไม่ใช่หลักฐานว่าได้ตรวจแล้วจนมี display event และ observation รายการที่คน/รายละเอียดเล็กต้องเก็บข้อจำกัดและตรวจ native frame/crop ก่อนใช้ตัดสินขอบหรือ attribute เลือก detail cases เพื่อทดสอบความต่างของสภาพภาพและ ambiguity ของ class พร้อมเหตุผล ไม่อ้างเป็น probability sample หรือ prevalence ของ dataset

การออกแบบเป็น task-driven ontology โดยแยก garment geometry, person ownership, observability และ attributes จึงรักษาข้อมูล partial people และหลีกเลี่ยงการใช้ missing/unknown เป็น background ข้อสรุป class เป็นข้อเสนอจากงานวิจัยและภาพ CCTV ที่ตรวจจริง การเห็น class/type ไม่พิสูจน์ความแม่นของ annotation; annotation agreement, เวลาทำ mask และความเข้ากันของเครื่องมือจริงยังไม่ได้วัด

## 8. แหล่งต้นฉบับและขอบเขตการปรับใช้

- [CIHP/PGN v1](https://arxiv.org/pdf/1808.00157v1), §3.1–3.2 PDF pp.6–7: การตรวจ annotation และการเปลี่ยน label ตามชุดข้อมูลของงานนั้น ใช้เป็นเหตุผลให้บันทึก class rationale ไม่คัดลอก taxonomy/splits/เกณฑ์คัดภาพของ CIHP
- [MHP v2 / NAN v3](https://arxiv.org/pdf/1804.03287v3), §3.1 PDF p.4: parsing ราย person และ self-index; ใช้รองรับการแยก semantic กับ owner ไม่ใช้ per-person background ของงานนั้นเป็น global unknown policy
- [RAP](https://zhangzhang80.github.io/RAP.pdf), §III-B PDF p.5 (journal p.1579): แยก occlusion/attributes และอธิบายปัญหา fine parts ใน surveillance ใช้ประกอบ coarse proposal ไม่ใช่หลักฐานสัดส่วน/ความยากของ CCTV นี้หรือกฎ dense masks
- [Cityscapes v2](https://arxiv.org/pdf/1604.01685v2), §2.2 PDF pp.2–3: unclear/void และผลของ valid domain ใช้ประกอบการเก็บ validity/coverage แยก ไม่รับ ignore codes/quality thresholds หรือวิธีแบ่งชุดเป็นข้อบังคับ

นิยาม 6 classes, composite head, auxiliary scope, cross-zone projection และแผน 2,400 เป็น **ข้อเสนอเฉพาะโครงการนี้** แหล่งอ้างอิงไม่รับรอง taxonomy หรือ ISO conformance ของเรา CCIHP และ model comparisons เป็นงานแยก

## 9. ส่วนที่พร้อมและส่วนที่ยัง OPEN

พร้อมใช้วางแผน: entity/ID/ownership/coordinate contract, proposed core classes/auxiliary relation, task-specific validity, color provenance และขั้นคัด candidate ที่ทำซ้ำได้

ยัง OPEN: คัดกรองภาพทั้งหมดให้ครบ, verified source timestamp/modality/curation dictionary, ขอบเขต class ที่ยังมี ambiguity รายเคส, เพิ่ม sock class หรือไม่เมื่อมีหลักฐานพอ, เครื่องมือและ export format ที่ผ่านการตรวจจริง, กำลังคน/เวลา/กำหนดส่ง/สิทธิ์เผยแพร่ข้อมูลจริง ไม่มีข้อใดถูกเปลี่ยนเป็น CONFIRMED จากการมีเอกสารนี้

อ่าน [schema เดิมที่ขยายต่อ](DATA_DICTIONARY_TH.md), [คู่มือทดลอง v0.1](../templates/annotation_guideline.template.md) และ [decision log](DECISION_LOG_TH.md) ประกอบ เอกสารนี้ไม่เริ่ม annotation pilot และไม่กำหนด Final Test
