# ขอบเขตพื้นที่งานและวิธีใช้งาน

Repository นี้เป็นงานสร้าง CCTV Human Parsing Evaluation Dataset แยกจากงานทดลองโมเดล พื้นที่งานเดิมและผลทดลองเดิมยังคงอยู่ ไม่มี Git repository ซ้อนอยู่ใน workspace เดิม

| พื้นที่ | บทบาท | การจัดการ |
| --- | --- | --- |
| repository | source, config example, docs, tests, templates, reports index, VS Code workspace | local Git; ตรวจ staged ก่อน commit |
| dataset_root จาก local config | ต้นทางภาพ/metadata ที่อยู่เดิม | read-only ในเครื่องมือ; ไม่เปลี่ยน permissions หรือสถานะคัดภาพ |
| work_root จาก local config | generated runs, annotation working files, outputs และ real release manifests | นอก repository; ยังไม่มี annotation/release จริง |
| work_root/legacy | สำเนาเดิมแบบ byte-identical รวมรายงาน/หลักฐานส่วนตัว | เก็บ provenance; ไม่แก้ path ใน historical run records |
| work_root/provenance | mapping old→new, SHA256, validation และ staged review receipt | local/private |

Absolute paths อยู่เฉพาะ ignored local config และ external report; code resolve root จากตำแหน่งตัวเอง เครื่องมือปฏิเสธ source/work/repository ที่ทับซ้อนกัน ไม่มี symlink data ภายใน repository

ขั้นถัดไปต้องระบุว่ากำลังออกแบบคู่มือ สำรวจภาพ หรือ annotate และใช้หลักฐาน/decision ตามขั้นนั้น การย้าย workspace ไม่อนุมัติ annotation, inference, training หรือ benchmark และไม่ตรึง class/color/QA policy

รายงานเดิมที่ขัดกันด้านเวลาเก็บเป็นประวัติทั้งหมด: package-only report เกิดก่อน bounded visual review คงความต่างระหว่าง observed/measured/reported และไม่ย้ายข้อสรุปใน sample ไปเป็น prevalence ทั้งชุด

## เปิด workspace และเตรียม local config

เปิด [CCTV_Dataset_Development.code-workspace](../CCTV_Dataset_Development.code-workspace) ด้วย VS Code: File → Open Workspace from File หรือ `code CCTV_Dataset_Development.code-workspace` บนเครื่องที่มี CLI หากข้อมูลอยู่บน remote ให้เปิด remote session ที่เข้าถึงข้อมูลนั้น Workspace เปิดเฉพาะ repository นี้และไม่แก้ settings ส่วนตัว

การทดสอบใน `tests/` ใช้ข้อมูลสังเคราะห์ ไม่ต้องมี local config หรือข้อมูลบริษัท ส่วนคำสั่งที่ใช้ config ต้องเตรียมตำแหน่งที่มีอยู่จริงก่อน:

```bash
cp -n config/audit.example.json config/local.json
```

คำสั่งนี้ใช้ตอนตั้งค่าครั้งแรกและไม่เขียนทับ config เดิม แก้ [config example](../config/audit.example.json) ที่คัดลอกแล้วใน `config/local.json` โดยระบุ absolute paths ตามเครื่องจริง:

| Key | ต้องชี้ไปที่ |
| --- | --- |
| `dataset_root` | โฟลเดอร์ source package เดิม ห้ามสร้าง outputs กลับเข้าไป |
| `metadata_csv`, `metadata_json`, `metadata_xlsx` | ไฟล์ export ทั้งสามรูปแบบที่ต่างกันและอยู่ใต้ dataset_root โดยตรง |
| `work_root` | โฟลเดอร์งานภายนอก Git ที่สร้างไว้แล้ว และไม่ทับซ้อน source/repository |
| `source_read_only`, `inspect_images`, `run_models` | คงค่า `true`, `false`, `false` สำหรับเครื่องมือปัจจุบัน |
| `phase` | local config ปัจจุบันใช้ `exploration_manifest_preparation_only`; เป็นคำอธิบายงาน ไม่ใช่ permission gate และไม่เปิดสิทธิ์ภาพ/annotation/inference |

ตรวจ current scripts แล้ว phase ไม่ถูกใช้ควบคุมการเข้าถึง: validator ตรวจ safety flags และพื้นที่ ส่วน audit output มี phase ของตัวเอง เปลี่ยนเพียง phase ใน ignored local config หลังสำรอง และตรวจ --check-config ผ่าน ทดสอบว่า inspect_images/run_models=true ยังถูกปฏิเสธ ไม่แก้ source code เพื่อขยาย capability; config example ยังคง label setup สำหรับการตั้งเครื่องครั้งแรก

Validator ใช้ path ที่ resolve แล้วและปฏิเสธ source/work/repository ที่ทับซ้อนกัน การเปิด source แบบอ่านอย่างเดียวเป็นพฤติกรรมของเครื่องมือ ไม่ได้เปลี่ยน permissions หรือ mount ต้นทางให้เป็น read-only ระดับระบบ Local config เป็นข้อมูลเฉพาะเครื่องที่ ignored ห้าม commit แม้จะเป็น repository public

## คำสั่งที่มีอยู่จริง

รันจาก repository root ด้วย Python 3.10+ และ standard library ไม่ต้องติดตั้งแพ็กเกจหรือใช้ environment ของโมเดล:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B scripts/audit_package.py --check-config
python3 -B scripts/prepare_handoff.py
```

| คำสั่ง | สิ่งที่ตรวจ/อ่าน | ผลลัพธ์ |
| --- | --- | --- |
| `unittest discover` | ข้อมูลสังเคราะห์ใน temporary directories | ทดสอบ I/O, comparison, path isolation; ไม่พิสูจน์คุณภาพ annotation |
| `audit_package.py --check-config` | การมีอยู่และขอบเขตของ paths โดยไม่อ่านเนื้อหา package | JSON สรุป config validation; ไม่สร้าง package run |
| `prepare_handoff.py` | README, AGENTS และไฟล์ Markdown ใน docs | document inventory/hash กับสถานะเฉพาะคำสั่งใน fresh external run |

ทั้งสองสคริปต์รับ `--config` และมี `--help` ค่า default คือ `config/local.json` ใต้ repository ที่หาได้จากตำแหน่งสคริปต์ หากรันจาก directory อื่นให้ส่ง path ไปยังสคริปต์/ไฟล์ config ตามจริง

คำสั่งต่อไปใช้เมื่อเริ่ม metadata/package audit ในขอบเขตที่ได้รับอนุญาต ไม่ใช่คำสั่งตั้ง workspace:

```bash
python3 -B scripts/audit_package.py --config config/local.json
```

สคริปต์นี้อ่าน CSV/JSON/XLSX ตาม filenames ใน config ตรวจ ZIP central directory ด้วย split parts รูปแบบ `_partNN.zip.NNN` ตามลำดับ และบันทึก SHA256 ของ source-package files ในโฟลเดอร์ต้นทาง รองรับ schema/export layout ที่ระบุใน [data dictionary](DATA_DICTIONARY_TH.md) ไม่ใช่ importer สำหรับทุก dataset format หาก layout เปลี่ยนต้องตรวจ reader/config ก่อนใช้

เครื่องมือไม่ decode/extract ภาพ ไม่ execute merge script และไม่แก้ statuses/notes ยังไม่มีคำสั่ง annotation, adjudication หรือ release building อัตโนมัติอยู่ใน repository นี้

## ผลลัพธ์และการทำซ้ำ

แต่ละ execution สร้าง `work_root/runs/<kind>-<UTC>-<id>/` ใหม่ Output มีเวลารันและ hashes ตามขอบเขตคำสั่ง เช่น `audit_configuration.json` เก็บ `script_sha256` สำหรับ package audit คำสั่งปัจจุบันยังไม่บันทึก code commit หรือสร้าง release manifest ให้อัตโนมัติ

รายละเอียดแพ็กเกจ, filenames จริง, linkage, notes และสถิติเฉพาะบริษัทอยู่ภายนอก Git ส่วน repository เก็บ schema/แบบฟอร์มให้ตรวจวิธีทำได้ ดูการสำรอง source/docs และ local config แยกกันที่ [ทะเบียนไฟล์](FILE_REGISTER_TH.md)
