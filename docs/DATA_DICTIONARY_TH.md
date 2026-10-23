# Data dictionary — schema ที่นำมาจาก export เดิม

ทบทวน 22 ตุลาคม 2026: อ่าน CSV ปัจจุบันและ hash ของสาม metadata exports เทียบหลักฐานเดิมแล้ว ตารางด้านล่างแยกชื่อ field ที่ตรวจได้ออกจากความหมายระบบที่ยังขาด สถิติ/ค่า/path จริงเก็บภายนอก Git ตาม [รายงานฐานงาน](../reports/README.md) ไม่ใช้ schema inspection เป็นการตรวจภาพ

พบเพียงแปด fields ในตาราง ไม่มี explicit event ID, sequence/burst ID, track/person ID, bbox/mask หรือ modality field กลุ่ม site+camera+เวลาเป็น candidate สำหรับสำรวจ ไม่ใช่ลำดับเหตุการณ์ที่ยืนยันแล้ว ค่า unknown ที่เป็น literal ต้องแยกจากจำนวนสถานที่จริง

| Field | ประเภท | ความหมายและข้อจำกัด |
| --- | --- | --- |
| filename | string | join key ที่ต้องตรวจค่าว่าง/uniqueness กับ archive ทุกครั้ง ไม่ใช้ row order หรือ content hash แทน identity |
| site | string | ข้อมูลสถานที่ตาม record; แยก unknown literal ออกจากสถานที่จริงโดยเก็บ raw |
| camera_name | string | ข้อมูลมุมกล้อง; ใช้ร่วมกับ site และตรวจ uniqueness |
| category | string | ข้อมูลกำกับ record ตามต้นทาง ไม่ใช่ person-instance ownership หรือ parsing GT |
| incident_timestamp | string | เก็บ raw/explicit UTC offset และ parse แยก ไม่เดา named timezone; ยังต้องยืนยันความหมาย event/capture time กับ source dictionary ไม่แทนด้วย timestamp ในชื่อไฟล์หรือ filesystem mtime |
| curate_status | string | คง raw status; pending ไม่ลบล้างประวัติ selected/rejected/flagged และไม่ map เป็น unreviewed โดยไม่มีนิยาม |
| curate_note | string/null | คง notes เดิม; ช่องว่างใน export ไม่พิสูจน์ว่า notes ต้นทางไม่มีหรือถูกลบ |
| remark | string/null | ข้อความประกอบที่อาจละเอียดอ่อน เก็บภายนอก Git ไม่แปลงเป็น label โดยอัตโนมัติ |

เทียบ CSV/JSON/XLSX ทุก field และจำนวนซ้ำ ใช้ null→empty normalization เฉพาะ comparison โดยไม่เขียนกลับต้นทาง CSV row locator ใช้ trace ภายใน snapshot ไม่ใช่ stable event/person ID

Identity, byte SHA256, ZIP CRC header, decoded image validity และ person geometry เป็นคนละข้อมูล CRC header ไม่เท่ากับ payload verification คนหลายคนในภาพต้องมี binding ที่พิสูจน์ได้ ไม่ถ่ายทอด category ให้ทุกคนเอง

## Annotation schema ทดลอง v0.1 — PROPOSED หลัง c5139f4

metadata dictionary ด้านบนคงความหมายตาม export ไม่เพิ่ม raw curation notes/status จากงาน annotation แบบ [contract example](../templates/annotation_contract_v0_1.example.json) เป็นโครง placeholder ไม่ใช่ข้อมูลจริง และไม่ใช่ JSON Schema ที่ตรวจครอบคลุมทุก field ด้วย validator อัตโนมัติ

| Entity / field group | ความสัมพันธ์ที่เสนอ / สิ่งที่ยังไม่ตรึง |
| --- | --- |
| image | image ID + source record ref + payload SHA256 แยกจากกัน; original width/height/orientation/coordinate frame; ไม่เอา filename time เป็น event identity |
| person | image-local person ID ที่สร้างเมื่อ annotate จริง แยก temporary locator ref; visible mask ref/mask-scope policy, presence/observability/workflow; ไม่ยืนยันบุคคลข้ามภาพ |
| region | region ID → owner person ref เมื่อ known; unknown owner เป็น null พร้อม candidates/reason, geometry/validity refs แยก; เสื้อหลายชั้น/one-piece relation และ candidate concepts ยัง PROPOSED |
| attribute | attribute ID → region ref; apparent color target เป็นข้อเสนอ, value/state/reason/applicability/lexicon ref แยกกัน ไม่กำหนดชื่อ/จำนวนสี |
| display | palette/style refs เพื่อดู masks ไม่ใช่ attribute สีเสื้อ; เปลี่ยน palette ต้องไม่เปลี่ยน semantic/instance raster หรือคำตอบสี |
| geometry | canonical original encoded-pixel coordinates; crop/scale/padding/affine chain ชัดเจน; raster dimensions ตรง image; การย่อสูญรายละเอียดได้แม้ inverse จุดถูก |
| provenance/revision | source/tool/schema/guideline/ontology/code versions, annotator/reviewer, decision refs, annotation revision/supersedes; human review ไม่เกิดจาก checksum |
| description | text/claim refs/status; สร้างจาก facts ที่มี support และ uncertainty ไม่เติมสี/บทบาท/identity ที่ไม่มีหลักฐาน; ยังไม่มี description GT |
| evaluation | disposition/policy ref และ Final Test UNASSIGNED; unknown/ignore/not annotated ไม่ถูกแปลงเป็น background/absent; ไม่กำหนด metric domain สุดท้ายในร่างนี้ |

ศูนย์ของ binary region mask หมายถึงนอก support ของ region นั้น ไม่ได้ยืนยันว่าเป็น known background ของทุก task บริเวณไม่เห็น/ถูกปิด/ยังไม่ annotate ต้องใช้ validity/state ที่ยังเสนอแยกกัน ไม่สร้าง person ปลอมเพื่อให้ owner field ไม่ว่าง และไม่ทิ้ง partial people เพราะข้อมูลไม่ครบ

[annotation_contract.py](../scripts/annotation_contract.py) ตรวจ subset ของ contract (IDs/owner refs/value states/dimensions) และทำ synthetic-only PNG/JSON roundtrip ไม่ได้เป็น annotation GUI/importer หรือ validator ครอบ schema ทั้งหมด Numeric IDs และ validity codes ใน fixture เป็นค่าทดสอบสมมติ ไม่ใช่ ontology ที่อนุมัติ ตัวอย่างจริง/รายชื่อและ masks จริงทั้งหมดต้องอยู่นอก repository
