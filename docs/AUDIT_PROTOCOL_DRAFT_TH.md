# แผนและรายการเสนอสำรวจ 24+8 — PROPOSED

ปรับหลัง foundation review commit eafe703 ตาม [Research Objectives & Constraints ล่าสุด](BENCHMARK_REQUIREMENTS_DRAFT_TH.md) ส่วน 1–7 บันทึกวิธีและสถานะรอบ preparation ที่ยังไม่เปิดภาพ ณ b8bb9ed; ส่วน 8 บันทึก bounded visual exploration ที่ได้รับอนุญาตภายหลังและเสร็จแล้ว รายงาน/draft เดิมคงตามเวลา ไม่มี annotation หรือ Final Test ที่กำหนดแล้ว

## 1. สิ่งที่ exploration ต้องช่วยตัดสิน

End-to-End เป็นผลหลักและ Oracle แยก จึงต้องสำรวจภาพเต็ม/บริบทและ ownership เพื่อไม่ให้ crop กลบปัญหาคนซ้อน/คนตกหล่น เป้าหมายขั้นต่ำคือ person/upper/lower/footwear masks ที่มีเจ้าของถูกต้อง พร้อมสีบน–ล่างเมื่อมองได้ และการสื่อข้อมูลแบบ structured output/คำบรรยาย วิธีทำ masks/Oracle inputs/metrics/QA และ taxonomy ยัง PROPOSED; ความยาว/ลวดลายไม่ใช่งานบังคับ

| ตรวจจาก metadata/หลักฐานได้ | ต้องเปิดภาพภายหลังจึงจะตอบได้ |
| --- | --- |
| filename identity, raw site-camera grouping, ความครบถ้วนการเชื่อม snapshot/manifest | แยกคน/region owner ได้หรือไม่ คนที่อาจตกหล่นและขอบเขต person mask |
| incident_timestamp ที่มี explicit offset แบ่ง record-clock band/month และเทียบระยะห่างได้ | scale/occlusion/truncation/เสื้อผ้าชิ้นเดียว/ชั้นเสื้อคลุม/footwear ที่มองเห็น |
| source labels/history ตามที่มีจริง โดยไม่แปลงสถานะ | สีบน–ล่างอ่านได้หรือไม่ แสง/modality และเหตุที่ไม่แน่ใจ ไม่เดาสีวัตถุจริง |
| category เป็นค่าระดับ record ที่ยังขาด dictionary/event-person binding | category/Category_EN ไม่เป็น label รายคนหรือ event ID; ชื่อไฟล์/เวลา/category ไม่พิสูจน์กลางคืน IR หรือคนเล็ก |

## 2. การใช้ประวัติ 12 ภาพเดิม

ตรวจ manifest/report/receipt เดิมกับ CSV ปัจจุบัน: filename และ fields ใน records เดิมเชื่อมได้ พร้อม hash metadata/manifest/report และ archive member/CRC header ใน inventory เดิม ไม่อ่าน image payload หรือเปิด preview เพื่อยืนยันใหม่ ดังนั้นข้อสังเกต/CRC/decode รายภาพยังเป็น **historical reported evidence**

ใช้ records เดิมทั้ง 12 เป็น coverage ส่วนแรก และใช้ข้อสังเกตเดิมบางรายการเป็น anchors เพื่อหา context candidates สำหรับ discovery ไม่ถือว่า checklist ตาม requirements ล่าสุดถูกกรอกแล้ว ประวัติการเปิดดูโดย assistant เพื่อพัฒนา scope/protocol เก็บใน `prior_exposure_log.csv` แยกจาก `curate_status` ผู้สำรวจ/ผู้ทบทวนจริงยังไม่ระบุ และไม่มี independent human review ที่ทำแล้ว

ศัพท์ historical `night-supplement` ในวิธีเลือกเดิมเป็น record-clock criterion เท่านั้น ไม่รับรองว่าภาพมืด/กลางคืน/IR ไม่แก้ manifest เก่าย้อนหลัง รายการที่เคยเห็นเก็บ exposure ต่อเนื่อง ไม่ย้อนเรียกว่า unseen/final holdout

## 3. องค์ประกอบและวิธีเลือกที่ทำซ้ำได้

**32 เป็นข้อเสนอเริ่มต้นที่แก้ได้ ไม่ใช่ final quota/statistical sample size หรือจำนวน annotation pilot** นับ unique ด้วย filename ที่เชื่อมได้; ยังไม่ทราบ unique image content ของทั้ง proposal

| ส่วน | records เดิมที่มีประวัติเปิดดู | records ใหม่ต่อประวัติที่ตรวจ | รวม distinct filenames |
| --- | --- | --- | --- |
| Coverage | 12 | 12 | 24 |
| Case discovery candidates | 0 | 8 | 8 |
| รวมแบบไม่ซ้อนกัน | 12 | 20 | 32 |

“ใหม่” หมายถึงไม่มีชื่อใน exposure manifest เดิมที่ตรวจ ไม่ใช่รับรองว่าไม่มีใครเคยดูที่อื่น รอบนี้จำนวนเปิดใหม่/เปิดซ้ำเป็นศูนย์ทั้งคู่

**กติกา v1:** ใช้ seed string `cctv-exploration-24plus8-v1` เป็น salt สำหรับ SHA256 ของ UTF-8 `seed|stage|filename` เป็น deterministic tie-break ไม่ใช่ probability sampling ไม่ใช้ file mtime หรือดึงเวลา/สภาพภาพจากชื่อไฟล์

1. เริ่ม 12 coverage ตามลำดับ alias ใน legacy manifest คง source record identity/history แต่ทุก field observation รอบใหม่ยัง NOT_STARTED
2. เติม coverage อีก 12 แบบ greedy: พิจารณาเฉพาะ filename ที่ยังไม่อยู่ในรายการและ raw site-camera pair ที่ยังไม่ครอบคลุม จัดอันดับด้วยจำนวน coverage ของ raw site ปัจจุบันน้อยสุด → จำนวนใน record-clock band 6 ชั่วโมงน้อยสุด → จำนวนใน record-month น้อยสุด → SHA256(`seed|coverage|filename`) น้อยสุด อัปเดต counts หลังเพิ่มทีละรายการ คง Unknown เป็น raw stratum ไม่เรียกไซต์จริง
3. เติม discovery ใหม่ 8 ตามลำดับ anchors แปดรายการที่กำหนดและบันทึกไว้ใน private manifest (aliases/order จริงไม่เผยแพร่ใน Git) ซึ่งมีรายงานเคสขอบภาพ/ระยะไกล-แสง/สิ่งกีดขวาง/อุปกรณ์/ไม่เห็นคนชัด/หลายคนใกล้กัน เลือก filename ที่ยังไม่ใช้ใน raw site-camera pair เดียวกับ anchor โดยระยะห่าง incident_timestamp น้อยสุด → SHA256(`seed|discovery|filename`) น้อยสุด เก็บ signed/raw time หรือ absolute gap ตาม manifest ไม่อ้างว่าเป็นเหตุการณ์/บุคคลเดียวกัน
4. ไม่ใช้ category, Category_EN, curate_status, curate_note หรือ remark จัดอันดับ ข้อมูลนี้ไม่รองรับการเลือกคนเล็ก/กลางคืน/IR หรือคนตามบทบาท และไม่ใช้ pending แทนกลุ่มผลคัดเดิม

รายชื่อ/row locator/raw grouping/time/gaps/reasons/input hashes อยู่ใน private manifest พร้อม builder ที่บันทึก hash และคำสั่งทำซ้ำ; JSON และ CSV เป็น proposal เดียวกัน ทดสอบสร้างใน fresh output อีกแห่งแล้วลำดับ/membership ตรงกัน ไม่มีภาพหรือ paths จริงใน Git

## 4. ข้อจำกัด coverage และวิธีหาเคสเพิ่ม

- ตัวอย่างน้อยกว่าจำนวน site-camera pairs จริง รายการ coverage เติมกล้องที่ยังไม่ครอบคลุม ส่วน discovery กลับไปยังกล้องที่มี anchors จึงไม่เพิ่ม coverage ทุกกลุ่ม ตาราง `coverage_matrix_private.csv` ระบุทั้งกลุ่มที่มี/ไม่มีใน proposal รวม record-clock/month gaps ไว้ในรายงานภายใน ห้ามอ้างครบทุกกล้อง/ทุกปัจจัยหรือเป็นตัวแทนเชิงสถิติ
- Discovery ใหม่ทั้งแปดยังเป็น **case presence unknown** กล้องเดียว/เวลาใกล้ไม่พิสูจน์ว่ามีเคสตาม anchor บางคู่ห่างกันหลายนาทีจึงเป็นเพียงบริบทที่อ่อนกว่า ไม่มี threshold ยืนยัน event และไม่คัดเป็น “ภาพยาก” จาก metadata
- เสื้อผ้าชิ้นเดียว การแบ่ง upper/lower เสื้อคลุม ownership อุปกรณ์ footwear และสีที่ตัดสินไม่ได้ยังเลือกจาก metadata ตรง ๆ ไม่ได้ เมื่อเปิดรอบหน้าจึงบันทึก found/not found/uncertain หากไม่พบให้เสนอเพิ่มจาก raw pairs ที่ยังขาด หรือบริบทของเคสที่มนุษย์พบจริง พร้อมเหตุผล/ลำดับ/seed และ manifest revision ไม่ลบตัวอย่างที่ไม่พบเงียบ ๆ
- งบเริ่ม 24+8 มีไว้จำกัดงานอ่านและบันทึกอย่างละเอียด ไม่ใช่ minimum ทางสถิติ หลังทราบเวลาทำจริงอาจเสนอเพิ่มรอบละราว 8 ตาม coverage/ambiguity ที่ขาด; ที่ราว 48 ภาพหรือเมื่อเจอปัญหาเปลี่ยน scope ให้ทบทวนแผน/ทรัพยากรก่อนเพิ่ม จำนวน กำหนดส่ง กำลังคน และเวลายังคง OPEN

## 5. แบบบันทึก บทบาท และเวลา

ใช้ [แบบบันทึกในทะเบียนเคส](CASE_REGISTER_DRAFT_TH.md) เป็นคำอธิบาย fields ของ `exploration_observations_draft.csv` ภายใน โครงเดิม [visual sample template](../templates/visual_sample_manifest.csv)/[case template](../templates/visual_case_register.csv) ยังเป็น generic headers ไม่ใช่ schema ใหม่ที่ตรึง

แยก `observed_from_image`, `inference_hypothesis`, `needs_human_review` และเก็บข้อสังเกตเดิมใน `historical_observation_reported_only` ทุกช่องใหม่ยังไม่กรอก ไม่มี person/mask GT ผู้สำรวจบันทึกสิ่งเห็น/ข้อสงสัย ผู้ทบทวนให้ความเห็นอีกขั้นโดยเก็บความต่างและที่มา ผู้รับผิดชอบจริงยัง UNASSIGNED และ independent review ยัง NOT_PERFORMED

เก็บ visual exploration time กับ recording time แยกกันเมื่อทำจริง ไม่กรอกเวลา annotation และ **ไม่ใช้เวลาสำรวจประมาณแรงงานทำ masks ทั้งชุด** ข้อมูลสังเคราะห์/การเชื่อมไฟล์ไม่ใช่ความถูกต้อง annotation

## 6. ข้อมูลซ้ำ ภาพต่อเนื่อง และข้อห้าม

ตอนนี้ตรวจได้เพียง distinct filenames; image-content hash/decode ของ proposal ใหม่ยังไม่ทำ หากรอบหน้าต้องตรวจ exact bytes ให้ใช้ SHA256 image payload และบันทึกผลแยกจาก identity; CRC/size หรือ perceptual similarity เป็นคนละระดับหลักฐาน ไม่ลบ/เปลี่ยน source/status เพื่อ deduplicate

ใช้ site-camera+record-time เป็น candidate neighborhood เท่านั้น ค่า gap 5/30/60 วินาทีถ้านำมาเปรียบเทียบเป็น sensitivity scenarios ไม่ใช่ event truth ไม่ติดตั้งเครื่องมือหรือรันโมเดลจาก protocol นี้ เก็บ discovery/protocol exposure แยกจาก final evaluation และไม่กำหนด Final Test/split ในรอบนี้

## 7. สถานะระบบและเงื่อนไขก่อนเปิดภาพ

ณ preparation config phase เป็น `exploration_manifest_preparation_only` และตอนนั้น script ไม่ใช้ phase เป็น permission gate แต่ใช้ safety flags/ขอบเขตความสามารถจริง คง `source_read_only=true`, `inspect_images=false`, `run_models=false`; ไม่เพิ่ม runner หรือสิทธิ์ annotation/inference ดู [คู่มือพื้นที่งาน](SCOPE_AND_OWNERSHIP_TH.md)

ก่อนเริ่ม visual exploration ต้องระบุผู้สำรวจ/ผู้ทบทวนและเวลาที่ใช้ได้ พร้อมยืนยันขอบเขตรอบภาพใหม่แยกจากงานเตรียมนี้ หาก curation/dictionary ยังไม่พบ ให้ระบุ missing และสำรวจในกรอบ export ที่เข้าถึงได้ ไม่เปลี่ยน pending/selected/rejected/flagged หรือเดา label ของบุคคล

## 8. วิธีสำรวจภาพจริงแบบจำกัดหลัง b8bb9ed — COMPLETED

ใช้ manifest เดิมทั้ง 32 records ไม่มีการแทน/เพิ่มรายการ ตรวจ metadata SHA256 และ mapping ไป current ZIP central-directory member ที่ไม่กำกวม อ่าน split ZIP โดยไม่ merge/extract ทั้งแพ็กเกจ เก็บเฉพาะ encoded payload ที่อนุญาตใน private run ตรวจ ZIP CRC, SHA256, strict decode และ dimensions; ไฟล์ที่อ่านไม่ได้ต้องมี error record ไม่แทนเงียบ ๆ การตรวจเหล่านี้ไม่เป็น annotation QA

- ใช้ dedicated `load_visual_scope()` และ `require_visual_ids()` ใน [workspace_paths](../scripts/workspace_paths.py): phase ต้องตรง bounded visual, source read-only, inspect_images เปิดโดย explicit scope, models/annotation/training/benchmark ปิด; private manifest hash/count<=32/IDs/order/snapshot ต้องตรง นี่เป็น operational cap ของขั้นที่อนุญาต ไม่ใช่ final dataset quota
- เริ่ม 8 records แรกแล้วทบทวนฟอร์มเป็น exploration-v1.1: เพิ่ม locator รายคน/region question, source overlay/สี/ความไม่แน่ใจ และ discovery component results โดยไม่สร้าง person GT ID/masks แล้วทำต่อจนครบ
- ดูภาพเต็มก่อน ใช้ crop เมื่อจำเป็น บันทึก source-pixel rectangle ว่าเป็น **display crop ไม่ใช่ GT bbox** ไม่มี generative enhancement/เติมส่วนที่หาย ภาพ/crops/รายชื่อ/record notes ทั้งหมดอยู่ภายนอก Git
- บันทึก observed/inference/needs-human-review ใหม่ก่อน explicit comparison กับ legacy notes; assistant มี prior context จึงไม่อ้าง blinded review/independent validation รายงานผู้สำรวจ assistant/Codex และ human review NOT_PERFORMED
- ใช้ SHA256 เปรียบเทียบ exact encoded-byte duplicates ภายในชุดที่อ่านจริง คง record identity และประวัติแยกจาก byte identity; near-duplicate/same-event ไม่ได้ยืนยันด้วยภาพกล้องเดียวหรือเวลาห่างสั้น
- Discovery บันทึก found/not_found/uncertain ราย component เป้าหมายอิง anchor ที่เสนอไว้ ไม่ใช้เป็น success rate; ผลของ record ที่ bytes ซ้ำไม่ใช่หลักฐานใหม่อิสระ
- แยกเวลา read/CRC/decode, display-tool calls และ recording เท่าที่วัดได้ active visual/เวลา annotation ไม่ได้วัดจึง null ระหว่างการหยุดข้าม turn มี timestamp บางส่วนไม่ถูก persist ให้รายงาน missing ไม่ใช้เวลา extract/resume/elapsed days แทน
- เพิ่ม exposure log ต่อ record/payload รวม reopens และ new filenames ที่ bytes อาจเหมือน record เดิม `final_test_membership=false` คือยังไม่จัดเข้า Final Test, `final_split_assignment=UNASSIGNED` ยังไม่ตัดสินว่าจะกันจาก final อย่างไร

หลังปิดรอบ local config เป็น `bounded_visual_exploration_completed`, inspect_images=false และ models/annotation/training/benchmark ปิดทั้งหมด visual loader ปฏิเสธ closed phase แต่ metadata CLI ยังตรวจ config ได้ ไม่เพิ่มภาพนอก manifest หรือเริ่ม pilot จากการทำ exploration เสร็จ

ข้อสรุปและข้อจำกัดที่เผยแพร่ได้อยู่ใน [รายงาน](../reports/README.md) ส่วน reference IDs รายภาพและหลักฐานจริงอยู่ในรายงานภายใน
