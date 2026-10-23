# ทะเบียนไฟล์และการย้าย

ทะเบียนเดิมฉบับเต็มอยู่ใน private legacy archive พร้อม reports/runs/notes เดิม Repository นี้เก็บเฉพาะ source และเอกสารกระบวนการ ไม่มี real images/metadata/annotations

| รายการใหม่ | ที่มา / การจัดการ |
| --- | --- |
| scripts/audit_package.py | คัดลอก reader เดิม; ปรับ root/config/output ภายนอกและ metadata filenames จาก config |
| scripts/prepare_handoff.py | ปรับ document provenance ให้จำกัด repository นี้และออก work_root |
| scripts/workspace_paths.py | absolute paths/disjoint/read-only validation; dedicated hash-pinned bounded visual scope, ปฏิเสธ capability อื่นและ closed scope |
| tests/test_visual_scope.py | synthetic checks ของ phase/flags/manifest/hash/snapshot/count/IDs/path isolation; ไม่อ่านภาพจริง |
| tests/test_split_archive.py | tests เดิมที่ปรับ import path และใช้ timestamp สมมติ |
| tests/test_workspace_setup.py | synthetic CLI tests, output isolation, readonly source, config rejection และ independent working directory |
| templates/source_inventory.csv, metadata_linkage.csv, duplicate_groups.csv | แบบฟอร์มเดิม header-only สำหรับหน่วยที่ต่างกัน |
| templates/visual_sample_manifest.csv, visual_case_register.csv | แบบฟอร์มเดิม ไม่มี sample/case จริง |
| templates/metadata_audit.example.json | แบบฟอร์มเดิมปรับสถานะเป็น template-only ไม่มีผล audit |
| docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md | ส่วนกระบวนการ/REQ/DEC จาก foundation เดิม ตัด company baseline ออก |
| docs/EVIDENCE_AND_HYPOTHESES_TH.md | เนื้อหา sources/candidates/hypotheses จาก foundation เดิม ไม่ยืนยันผลใหม่ |
| docs/CASE_REGISTER_DRAFT_TH.md | case/test forms จาก foundation เดิม ตัด historical company arithmetic ออก |
| docs/AUDIT_PROTOCOL_DRAFT_TH.md, DATA_DICTIONARY_TH.md | ปรับเอกสารเดิมเป็น protocol/schema ที่ไม่มีสถิติจริง |
| docs/FOUNDATION_INDEX_TH.md, SCOPE_AND_OWNERSHIP_TH.md, DECISION_LOG_TH.md | แก้ตำแหน่งอ้างอิงและขอบเขต repository ใหม่; คงประวัติเต็มไว้ข้างนอก |
| config/audit.example.json | placeholder paths เท่านั้น; config/local.json จริง ignored |
| README.md | หน้าแนะนำงานวิจัย วัตถุประสงค์ สถานะ วิธีพัฒนา หลักการ reference annotation และข้อจำกัด |
| AGENTS.md, .gitignore | กฎเฉพาะงานและขอบเขตข้อมูลที่เก็บใน Git |
| docs/SCOPE_AND_OWNERSHIP_TH.md | คู่มือตั้ง workspace/local config, ใช้สคริปต์ และแยก source/work/repository |
| CCTV_Dataset_Development.code-workspace | VS Code เปิด checkout นี้หนึ่ง folder; ไม่มี personal/system settings |
| requirements.txt | standard library; ไม่มี package install ใน setup |
| reports/README.md | รายงานฐานงาน/หลักฐานห้าระดับและช่องว่าง; ชี้ external setup report/ผลตรวจปัจจุบัน/รายงานเดิมโดยไม่เผยแพร่ raw evidence |

แบบฟอร์มสำหรับ source version, class/attribute rationale, annotation guide, QA และ release manifest ใช้ใน templates/ ตามสถานะ DRAFT ไม่เป็น annotation จริงหรือ class policy ที่อนุมัติแล้ว

`templates/release_manifest.example.json` มีช่อง source version, annotation revision, ontology/guideline/QA versions, code repository/commit และ references/hashes ที่ต้องใช้ก่อนออกรุ่น ช่องยังเป็น `null` และ runner ปัจจุบันไม่ได้เติมให้อัตโนมัติ การเพิ่มช่องในแบบฟอร์มเป็นการเตรียม traceability ไม่ใช่การสร้างหรืออนุมัติ dataset release

รอบ foundation review ใช้ไฟล์เดิม: เพิ่มตารางขอบเขต/DEC ในข้อกำหนด ปรับ protocol เป็นแผนสำรวจร่าง เพิ่มการตรวจแหล่งต้นฉบับในทะเบียนหลักฐาน และปรับ README/index/dictionary/decision log ให้สถานะตรงกัน ไม่สร้างเอกสารเปล่าหรือ annotation specification หลายชุด สำเนาก่อนแก้และหลักฐานตรวจ metadata จริงอยู่ใน external provenance ไม่แก้ archive ประวัติ

รอบเตรียม exploration หลัง eafe703: public เก็บ requirements/วิธีเลือกและแบบคำถามในเอกสารเดิม ส่วน `proposed_exploration_manifest.json/.csv`, `prior_exposure_log.csv`, `coverage_matrix_private.csv`, `exploration_observations_draft.csv`, private builder/input hashes/validation และรายงานภายในอยู่ใน fresh external run เท่านั้น generic CSV templates ใน Git ไม่ใช่แบบบันทึก actual run ทั้งหมด รายการเสนอไม่ใช่ curation หรือ final membership

รอบ bounded visual หลัง b8bb9ed: public เพิ่มเฉพาะ guard/tests และวิธีการ/สรุปที่ไม่มี per-image IDs รายชื่อบริษัท หรือภาพ ส่วน payload/crops, CRC/SHA/decode receipts, fresh observations/locator rows, discovery/legacy comparison, exposure/time gaps และรายงานจริงเก็บใน fresh external run ไม่แก้ draft หรือ historical reports

## Mapping และ checksum

`work_root/provenance/migration_copy_manifest.json` บันทึกทุก old path→copy path, size, SHA256 และผล copy verification ก่อนปรับ code/doc สำเนาเดิมทั้งหมดคง byte-identical ภายใต้ legacy/ ส่วน versionable migration index บันทึกการปรับโดยไม่แนบ raw records หรือ filenames รายภาพ

เอกสารเฉพาะบริษัทและ preview evidence ไม่ถูกคัดลอกเข้า Git ต้นทางภาพ/metadata ยังคงที่เดิม ทุก source-package stat และ hash ของ metadata/document ขนาดเล็กบันทึกก่อน/หลัง setup โดยไม่มี image decode ใหม่

## สำรองและกู้คืน

เก็บ Git bundle ภายนอกที่ work_root/backups และตรวจด้วย git bundle verify ก่อนใช้ กู้ checkout ใหม่ด้วย git clone <bundle-path> <new-empty-directory> แล้วคัดลอก config/local.json จาก private backup ปรับ absolute paths ให้ตรงเครื่อง ใช้ bundle กู้ source/docs ได้แต่ไม่มี dataset หรือ annotations

สำรอง work_root และ source dataset แยกด้วยวิธีของผู้ดูแลข้อมูล การตั้ง workspace นี้สำรอง legacy evidence/local config แล้ว แต่ไม่ได้สำรองภาพต้นทางทั้งชุด ห้ามใช้ git reset หรือการลบต้นฉบับเพื่อกู้โดยไม่มีอนุมัติ
