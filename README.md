# CCTV Human Parsing Evaluation Dataset

งานพัฒนา dataset แยกเป็น Git repository อิสระ สถานะ **WORKSPACE_READY / NO_NEW_ANNOTATION_OR_MODEL_RUN** อ่าน [ขอบเขตงาน](docs/SCOPE_AND_OWNERSHIP_TH.md), [ทะเบียนไฟล์](docs/FILE_REGISTER_TH.md) และ [เอกสารตั้งต้น](docs/FOUNDATION_INDEX_TH.md) ก่อนทำขั้นถัดไป

## จุดเริ่มต้นและตำแหน่งข้อมูล

เปิด `CCTV_Dataset_Development.code-workspace` ด้วย VS Code: File → Open Workspace from File หรือ `code CCTV_Dataset_Development.code-workspace` บนเครื่องที่มี CLI ใช้ remote SSH เข้าเครื่องเดียวกับที่เก็บข้อมูลก่อน Workspace นี้เปิดเฉพาะ repository ไม่แก้ settings ส่วนตัว

ต้นทางภาพ/metadata คงตำแหน่งเดิมแบบอ่านอย่างเดียว Path จริงทั้งหมดอยู่ใน `config/local.json` ที่ ignored รูปแบบตัวอย่างคือ [config/audit.example.json](config/audit.example.json) ใช้ absolute paths และต้องให้ `dataset_root`, `work_root`, repository อยู่คนละต้นไม้

`work_root` อยู่นอก Git มี `runs/`, `annotations/`, `outputs/`, `releases/`, `provenance/`, `legacy/`, `backups/` รายงานตั้ง workspace ที่มี path จริง/commit receipt คือ `work_root/WORKSPACE_SETUP_REPORT_TH.md` สำเนาประวัติเดิมทั้งหมดอยู่ใน `work_root/legacy/` และ checksum/path map อยู่ใน `work_root/provenance/`

## วิธีตรวจและรัน

ใช้ Python 3.10+ standard library ไม่ต้องติดตั้งแพ็กเกจ ไม่ใช้ environment ของโมเดลเดิม จาก repository root:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/audit_package.py --check-config
python3 -B scripts/prepare_handoff.py
```

สองคำสั่งหลังใช้ local config ที่ตั้งให้เครื่องนี้แล้ว `--check-config` ตรวจ path/scope โดยไม่อ่านแพ็กเกจ ส่วน prepare_handoff อ่านเฉพาะเอกสาร repository และเขียน provenance ออกไปยัง work_root

เมื่อต้องการ metadata/package audit ในรอบที่ได้รับอนุญาต ใช้ `python3 -B scripts/audit_package.py` สคริปต์อ่าน CSV/JSON/XLSX และ ZIP directory โดยไม่ decode ภาพ และเขียน run ใหม่ภายนอก Git ใช้ชื่อ metadata จาก config และ split ZIP `_partNN.zip.NNN` ไม่ใช้ row order แทน image identity

## สถานะหลักฐานและงานที่จะทำต่อ

มีหลักฐาน package/metadata audit และ bounded visual review จากงานก่อนย้าย ซึ่งเก็บครบใน private legacy archive คำว่า “ยังไม่ดูภาพ” ในรายงานเก่าบางฉบับเป็นสถานะ ณ วันนั้น ไม่ลบล้างรายงาน visual review ที่ใหม่กว่า การตั้ง workspace รอบนี้ไม่ได้เปิดดูภาพใหม่ ไม่สร้าง annotation หรือผลโมเดล และไม่ใช้ข้อมูลทดลองเดิมมาเป็น GT

Ontology, class IDs, display colors, attribute sets, QA thresholds, splits และ release policy ยังไม่ตรึง เตรียมแบบฟอร์มสำหรับที่มา/รุ่นข้อมูล เหตุผลคลาส/attribute คู่มือ annotation/QA การตัดสินใจ และ release manifest ใน `templates/` ทั้งหมดเป็นร่างไม่มีข้อมูลจริง

รักษาสถานะคัดภาพและ raw notes ตามต้นฉบับ `pending` ใน export ปัจจุบันไม่ยืนยันว่าผล selected/rejected/flagged เดิมถูกยกเลิก `category` ที่ผูกกับ record ยังไม่เป็นบทบาทรายคนหรือ parsing GT โดยอัตโนมัติ

สำรอง repository ด้วย Git bundle และสำรอง local config/external work แยกกันตาม [ทะเบียนไฟล์และการกู้คืน](docs/FILE_REGISTER_TH.md) ยังไม่มี GitHub remote หรือ push
