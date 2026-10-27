# สถานะฐานงานและหลักฐาน — 22 ตุลาคม 2026

รอบนี้ตรวจฐานงานและเตรียมแผนสำรวจ ไม่สร้าง specification ฉบับสุดท้าย เอกสารเดิมทุกส่วนยังแก้ไขได้ การมี REQ, template หรือข้อความใน README ไม่ใช่การยืนยันรายละเอียดวิจัยโดยผู้ใช้

## ขอบเขตการตรวจและแหล่งหลักฐาน

อ่าน Git/config/code/docs ปัจจุบัน รายงานตั้ง workspace รายงาน package audit และ bounded visual review เดิม ตรวจ schema/ชื่อไฟล์/เวลาใน CSV ปัจจุบันและ hash ของ metadata exports พร้อม stat ต้นทางก่อน–หลัง ไม่เปิดภาพ ไม่เลือกตัวอย่างจริง ไม่ทำ annotation หรือรันโมเดล

| รหัส | หลักฐานที่ตรวจ / ตำแหน่งภายใน | ขอบเขตและข้อจำกัด |
| --- | --- | --- |
| F01 | Git checkout, [AGENTS](../AGENTS.md), [README](../README.md), scripts/config/templates ปัจจุบัน | repo อิสระ; ตรวจ branch/remote และเทียบ remote ก่อนแก้; paths จริงอยู่ใน ignored local config |
| F02 | `WORKSPACE_SETUP_REPORT_TH.md` ใต้ external work_root และ migration provenance | พบไฟล์จริง; ใช้สำรอง/path map/checksums เดิม ไม่ใช่ผล QA ของ dataset |
| F03 | `CCTV_RETURN_TO_CHAT_TH.md`, `FILE_REGISTER_TH.md` และ package run ใน private legacy archive | อ่าน report และ machine-readable audit/inventory/linkage/format comparison ที่อ้างถึง; เป็น snapshot ประวัติ |
| F04 | metadata ปัจจุบัน + source stat + F03 | hash ของ CSV/JSON/XLSX ตรง audit เดิม; อ่าน CSV ใหม่เพื่อตรวจ fields/status/time และเทียบ filename กับ linkage/inventory เดิม; ไม่ตรวจเนื้อหา JSON/XLSX ซ้ำเพราะ bytes ตรง |
| F05 | bounded visual report, sample manifest และ validation receipt ใน private legacy archive | hash ของ manifest ตรง receipt และ hash metadata ใน manifest ตรง CSV ปัจจุบัน; ไม่เปิด preview หรือตรวจข้อสังเกตภาพซ้ำ |
| F06 | พื้นที่ annotation/release ภายนอกตาม local config | ตรวจแบบจำกัดไม่พบไฟล์จริงในสองพื้นที่นี้; ไม่ใช่คำยืนยันว่าทุกที่ไม่มี annotation |
| F07 | [แหล่งต้นฉบับห้างาน](../docs/EVIDENCE_AND_HYPOTHESES_TH.md) | ตรวจ PDF เฉพาะหัวข้อที่เกี่ยวข้อง; ไม่ตรวจ release assets/label IDs หรืออ้างมาตรฐานบังคับ |

หลักฐาน F04 และ paths/hash/สถิติ/รายการค้นหาที่ละเอียดอ่อนอยู่ใน `work_root/provenance/` ของรอบ foundation review ผู้ใช้เข้าถึงตำแหน่งจริงจากรายงานภายในได้ ไม่มี raw evidence หรือสำเนา metadata ใน Git

## สถานะแยกตามระดับหลักฐาน

| ประเด็น | ระดับสถานะ | ผลตรวจและสิ่งที่ยังกล่าวอ้างไม่ได้ |
| --- | --- | --- |
| ที่มาของ bytes ที่กำลังใช้งาน | **ตรวจยืนยันจากไฟล์จริงแล้ว** — F01/F04 | local config ชี้แพ็กเกจที่มีอยู่จริง; metadata bytes ตรง snapshot audit เดิมและ stat ของไฟล์แพ็กเกจตรง setup; ยังไม่ใช่ dataset release version ที่อนุมัติ |
| ภาพ ↔ metadata ↔ manifest | **ตรวจยืนยันจากไฟล์จริงแล้ว เฉพาะ metadata/หลักฐาน** — F03/F04 | filename ใน CSV ไม่ซ้ำและตรง linkage/inventory เดิม; checksum metadata และ byte/stat ของไฟล์หลักฐานตรวจได้วันนี้ แต่ไม่ได้อ่าน ZIP directory/payload ใหม่ |
| ความครบถ้วน archive และเทียบสาม export | **มีรายงานเดิมแต่ยังยืนยันกับข้อมูลปัจจุบันไม่ได้ทั้งหมด** — F03/F04 | ใช้ผล directory/join/format comparison เดิมเพราะ metadata hash ตรงและ archive stat ไม่เปลี่ยน; ไม่ rehash archive ขนาดใหญ่ ไม่ตรวจ CRC/decode ทั้งชุด; stat ไม่ใช่หลักฐานว่า archive bytes ตรงแน่นอน |
| สถานะ export ปัจจุบัน | **ตรวจยืนยันจากไฟล์จริงแล้ว** — F04 | raw status เป็น pending และ note ใน export ว่าง; ไม่ได้พิสูจน์ว่าผู้ใช้ยังไม่เคยคัดหรือไม่มี notes เดิม |
| selected/rejected/flagged เดิม | **มีรายงานเดิมแต่ยังยืนยันกับข้อมูลปัจจุบันไม่ได้** — F03 | พบยอดตามรายงานเดิม แต่ยังไม่พบ original curation export/notes ที่ใช้ join รายภาพ; ห้ามนำ pending มาทับผลเดิมหรือรวมยอดต่าง snapshot |
| ข้อมูลกล้อง/เวลา/เหตุการณ์ | **ตรวจยืนยันจากไฟล์จริงแล้ว เฉพาะ schema** — F04 | มี site, camera_name, incident_timestamp พร้อม explicit offset; ไม่มี event/track/person ID หรือ sequence field; category เป็นค่าระดับ record ยังไม่มี person binding |
| ความหมาย category และเวลาในระบบต้นทาง | **ยังไม่มีข้อมูลเพียงพอ** — F03/F04 | ต้องมี source dictionary/event export ยืนยันว่า label ผูกเหตุการณ์หรือคนใด และเวลาเป็น capture/event/export time อย่างไร; ไม่เดาจากชื่อไฟล์หรือ mtime |
| ประวัติดูภาพและคุณภาพ annotation | **มีรายงานเดิมแต่ยังยืนยันกับภาพปัจจุบันไม่ได้** — F05/F06 | รายงานเก่ามี assistant review ตัวอย่างแบบจำกัด ไม่มี independent human review; รอบนี้ยืนยันเพียงไฟล์หลักฐาน ไม่ใช่ visual findings/coverage/agreement ใหม่ |
| สถานะงานตามเอกสาร | **พบหลักฐานขัดแย้งในคำอธิบาย** — F01/F03/F05 | phase ใน config/กฎ setup เก่า และถ้อยคำเตรียม pilot ใน README เดิมไม่ตรงขอบเขตรอบนี้; แก้เอกสารให้เป็น audit/แผนร่าง เก็บ phase config เดิมพร้อมข้อจำกัด; รายงาน “ยังไม่ดูภาพ” เก่ากับ visual report ที่ใหม่กว่าคือคนละเวลา ไม่ใช่หลักฐานลบล้างกัน |
| การตีความ label ระดับเหตุการณ์ | **พบข้ออ้างเกินหลักฐาน** — F03/F04 | เอกสาร inherited เรียก Category_EN ว่าระดับเหตุการณ์ แต่ export ปัจจุบันมี category และยังไม่มีนิยามระบบยืนยัน; แก้ทะเบียนหลักฐานให้แยกคำบอกเล่าจากสิ่งตรวจได้ ไม่สรุปเป็น label ของทุกคน |
| ขอบเขต task/คลาส/สี/QA/split | **ข้อเสนอที่ยังไม่ตัดสินใจ** | ดู [ตารางขอบเขตและ DEC](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md); ผู้ใช้ยืนยันงานพัฒนา dataset และข้อห้ามรอบนี้ ไม่ได้อนุมัติรายละเอียดทั้งหมด |
| source-system revision/สิทธิ์/final release | **ยังไม่มีข้อมูล** | ยังขาด provenance ต้นทางที่ผูก curation snapshot กับแพ็กเกจ และหลักฐานขอบเขตสิทธิ์ใช้งานจริง; template ที่ว่างไม่แทนข้อมูลเหล่านี้ |

ยังไม่พบหลักฐานว่าประชากรและเวอร์ชันเดียวกันมีผลคัดเลือกขัดกันจริง ความต่างของ pending กับรายงานคัดเก่าจึงเป็นช่องว่างในการเชื่อมประวัติ ไม่ใช่เหตุให้เปลี่ยนสถานะ

## สิ่งที่พร้อมทำต่อและสิ่งที่ต้องรู้ก่อน

มีฐานสำหรับสำรวจ metadata ต่อแบบ read-only และเสนอ coverage/edge-case design แล้ว แต่ยังไม่พร้อมตรึงชุดประเมินหรือเริ่ม annotation ใช้ [แผนสำรวจร่าง](../docs/AUDIT_PROTOCOL_DRAFT_TH.md) และ [DEC/คำถามถึงผู้ใช้](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md) เป็นจุดเริ่ม ไม่ต้องรัน full-package hash/decode ซ้ำเพียงเพื่อปรับเอกสาร

## คงประวัติและแยกข้อมูลสาธารณะ

รายงานตั้ง workspace อยู่ที่ work_root ตาม local config รายงานส่งกลับและทะเบียนไฟล์เดิมอยู่ใน `work_root/legacy/cctv_dataset/` ฉบับ public ปัจจุบันคือ [ทะเบียนไฟล์](../docs/FILE_REGISTER_TH.md) รายงาน foundation review ภายในบันทึก paths จริง วิธีตรวจ checksums และข้อจำกัด โดยไม่แก้รายงานประวัติย้อนหลัง

ภาพ/preview, metadata/notes, รายชื่อไซต์/กล้อง/บุคคล, per-image manifests และหลักฐานบริษัทอยู่ภายนอก Git เอกสารสาธารณะเผยแพร่เฉพาะวิธีการ/ทางเลือกและสถานะที่จำเป็น การตรวจไฟล์และ synthetic tests ไม่พิสูจน์ annotation ถูกต้อง

## ภาคเพิ่มหลัง eafe703 — เตรียม exploration ตาม requirements ล่าสุด

ส่วนรายงาน foundation ด้านบนคงข้อความเดิมตามเวลาที่ตรวจ ไม่แก้ OPEN ในรอบก่อนให้ดูเหมือนได้รับคำตอบแล้ว ข้อกำหนดใหม่/การเปลี่ยนสถานะดู [requirements](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md) และ PLAN-002/003 ใน [decision log](../docs/DECISION_LOG_TH.md)

- USER CONFIRMED: End-to-End หลัก, Oracle แยก; person/upper/lower/footwear masks + ownership; สีบน–ล่างเมื่อภาพเอื้อ; structured output/คำบรรยาย Attributes เพิ่มไม่ mandatory; จำนวน/กำหนดส่ง/กำลังคน/เวลา OPEN วิธี taxonomy/annotation/metrics/QA ยัง PROPOSED
- เชื่อม records ใน manifest 12 ภาพเดิมกับ CSV ปัจจุบันได้ และตรวจ hash ของ manifest/report/metadata กับ receipt และ inventory เดิม โดยไม่เปิดภาพหรืออ่าน archive payload ใหม่ ประวัติ assistant exposure ไม่ใช่ independent human review หรือ curation result
- เตรียม [แผน 24+8](../docs/AUDIT_PROTOCOL_DRAFT_TH.md) พร้อม proposed manifest ภายใน: coverage เดิม 12 + ใหม่ 12, discovery ใหม่ 8 รวม distinct filenames 32; unique image content ยังไม่ทราบ ใหม่หมายถึงไม่ปรากฏใน exposure log ที่ตรวจ ไม่ใช่รับรองว่าไม่เคยมีใครดู
- discovery อ้างอิงเพียงบริบทของรายงานเคสเดิมและ raw grouping/record time; ยังไม่รู้ว่า candidate มีเคสนั้นจริง บางรายการห่างกันหลายนาที กลุ่มที่ยังไม่ครอบคลุมบันทึกใน private coverage matrix ไม่อ้างเป็นตัวแทนทางสถิติ
- เตรียม [แบบบันทึก](../docs/CASE_REGISTER_DRAFT_TH.md) ที่แยก observed/inference/human-review และเวลา exploration/recording จาก annotation; ทุก observation ใหม่ยังไม่เริ่ม ผู้สำรวจ/ผู้ทบทวนยังไม่ระบุ ไม่มี independent review ใหม่
- ตรวจแล้ว config phase เป็น descriptive metadata ไม่ใช่ permission gate เปลี่ยน local phase ให้ตรงงานโดยคง read-only/image/model flags และไม่เพิ่มความสามารถ annotation/inference; ค้น curation/dictionary เพิ่มเฉพาะ repo/legacy/พื้นที่ source ที่เกี่ยวข้อง ยังไม่พบต้นฉบับที่ปิดช่องว่างได้ ไม่ค้นทั้งเครื่องซ้ำ

รายงาน/manifest/reproduction receipt และ paths จริงอยู่ใน fresh external work_root/runs ของรอบ exploration preparation ส่วนรายงาน foundation ภายในเดิมไม่แก้ ไม่มีการเปิดภาพ คัด final annotation หรือ model run ในรอบนี้

## ภาคเพิ่ม 23 ตุลาคม 2026 — bounded visual exploration หลัง b8bb9ed

รายงานก่อนหน้าด้านบนคงตามเวลา ภายหลังผู้ใช้อนุญาตให้เปิดรายการเดิมครบ รวม historical reopens จึงดำเนิน visual exploration และเพิ่ม fresh run แยกจาก draft/รายงานเดิม

| สิ่งที่ตรวจ | ผล / หน่วยและขอบเขต |
| --- | --- |
| เปิดตาม manifest | 32/32 records สำเร็จ: 20 new filenames ต่อ log ที่ตรวจ และ 12 historical reopens; ไม่เปิดภาพนอก manifest |
| Payload integrity/decode | CRC/SHA256/strict full decode ผ่าน 32/32, อ่านไม่ได้ 0; เป็นการตรวจไฟล์ ไม่ใช่ annotation correctness |
| Exact duplicates | 32 filenames มี 31 unique encoded payloads หนึ่งคู่ bytes ตรงกัน; คงทั้งสอง records และ curation เดิม ไม่ถือชื่อใหม่เป็นเนื้อหาใหม่เสมอ |
| หลักฐานภาพ | มี observed/inference/needs-human-review และ locator ตามความแตกต่างรายคน; ผลรายภาพ/ภาพ/crops/แหล่งข้อมูลจริงอยู่ภายนอก Git |
| ขอบเขตผล | เห็น person/region/color support ได้บางกรณี แต่ยังไม่มี masks/GT/independent human review หรือผล End-to-End/Oracle |
| Discovery | มีทั้งเคสพบ/ไม่พบ และองค์ประกอบ uncertain; record ที่ duplicate ไม่เพิ่มหลักฐานภาพอิสระ ไม่ตีความเป็น success rate/prevalence |
| ประวัติและเวลา | exposure ใช้พัฒนา protocol; Final Test ยัง UNASSIGNED; เวลา active visual/annotation ที่ไม่วัดคง null และรายงาน timestamp gaps หลังหยุดข้าม turn |
| Source และระบบ | metadata/proposal hashes และ source stat ไม่เปลี่ยน หลังจบปิด inspect_images/visual phase; models/annotation/training/benchmark ปิดตลอด |

สิ่งที่ร่างเป็นข้อเสนอได้คือ visible-support/unknown, owner/accessory/outer-layer questions, crop provenance, color observability และการไม่เติมคำบรรยายเกินหลักฐาน ต้องให้มนุษย์ทบทวนก่อนใช้สร้าง GT ยังต้องสำรวจเพิ่มเติมภายหลังเรื่อง one-piece ที่เห็นเต็มตัว รองเท้า/เท้าเปล่าชัดเจน หลายสภาพแสง/known modality และ coverage ที่ไม่อยู่ใน sample รอบนี้ไม่เพิ่มสมาชิกและไม่ตรึง taxonomy จำนวนสี QA หรือขนาด final dataset

[Protocol](../docs/AUDIT_PROTOCOL_DRAFT_TH.md) และ [case form](../docs/CASE_REGISTER_DRAFT_TH.md) อธิบายวิธี ส่วน [guard](../scripts/workspace_paths.py)/[synthetic tests](../tests/test_visual_scope.py) ตรวจ permission boundaries รวม tests ปัจจุบัน 14 รายการผ่าน ไม่มีการติดตั้งแพ็กเกจหรือแก้ environment โมเดล การดูภาพใช้ Pillow ที่มีอยู่เดิมและไม่รันโมเดล

## ภาคเพิ่ม 23 ตุลาคม 2026 — คู่มือทดลองและชุดทบทวนหลัง c5139f4

ขยาย [คู่มือเดิมเป็น v0.1](../templates/annotation_guideline.template.md) พร้อม R01–R12 ที่มีคำถาม หลักฐานอ้างภายใน ทางเลือก ข้อเสนอ/เหตุผล ผลต่อ evaluation และสถานะ PROPOSED จัด [ตารางตัดสินใจก่อน pilot/แผน QA](../templates/quality_review.template.md) และ [schema ร่าง](../docs/DATA_DICTIONARY_TH.md) แล้ว ไม่ถือว่าอนุมัติกฎหรือเริ่ม annotation

ชุด static HTML ภายในมี 10 unique cached payloads พร้อม full frames/display crops/locators/ทางเลือกและ decision sheet ยัง PENDING_HUMAN_REVIEW ใช้เฉพาะข้อมูลใน 32 records เดิม ไม่เปิดภาพใหม่จาก ZIP ไม่วาด masks จริงและไม่มี blinded/independent human review ประวัติเปิดจริงแยกไว้ใน run ใหม่ ไม่แก้ observations/curation เดิม

Synthetic-only checks ตรวจ PNG dimensions/IDs/owner-state preservation/point inverse และแยก display palette จากสีเสื้อ ใช้ Pillow/JSON ที่มีอยู่ ชุด tests รวม 17 รายการผ่าน ไม่มีเครื่องมือ annotation GUI ที่ยืนยันใช้งานได้ใน scope ที่สำรวจ จึงยังไม่มี GUI/COCO/RLE roundtrip หรือ human annotation reliability ผลทดสอบนี้ไม่พิสูจน์ annotation quality

แผน pilot เสนอ 8 unique images แยก calibration/first pass ตามกฎที่ต้องทดสอบ จำนวนยังไม่อนุมัติ คน/ผู้ตรวจ/เวลา/กำหนดส่ง OPEN ไม่มี agreement threshold หรือ Final Dataset count/Final Test ที่กำหนดแล้ว One-piece ชัด รองเท้า/เท้าเปล่าหลายมุมและ known modality ยังเป็นช่องว่างเพื่อเสนอสำรวจเฉพาะจุดภายหลัง

ตรวจเนื้อหาต่อหลัง c6f28c4: ปรับทางเลือก A/B/C ของ R01–R12 เป็นวิธีเก็บข้อมูล/แบ่งขั้นงานที่ใช้ได้ภายใต้ constraints พร้อมผลกระทบของแต่ละทางเลือก ข้อเสนอหลักยังเดิมและ PROPOSED ไม่ให้วิธีที่ขัดข้อกำหนดกลายเป็นตัวเลือกอนุมัติ ชุดทบทวนภายในปรับข้อความตามกันและเก็บฉบับก่อนแก้ ไม่มีภาพใหม่หรือ annotation เพิ่ม


## Whole-export review และ Dataset Design v0.1 — 27 ตุลาคม 2026

คำสั่งใหม่จากผู้ใช้ขยาย read-only file/visual review จาก manifest เดิมไปยัง current export ทั้งชุด พร้อมขอข้อเสนอ class/schema และแผนคัดสองพันกว่าไม่เกินสามพันภาพ ขอบเขตนี้ไม่เปิด annotation/pilot/model/training/benchmark และไม่กำหนด Final Test รายงาน foundation/preparation/visual/guideline ข้างต้นคงเป็นหลักฐานตามเวลาของตน

CONFIRMED เฉพาะไฟล์: ตรวจ metadata exports/linkage และ CRC/decode/dimensions/byte-vs-pixel duplicates ทั้ง population ที่เข้าถึงได้ เก็บผลแยก strict failures กับ alternate-decoder diagnostics ไม่แก้ต้นฉบับหรือ curation statuses ข้ออ้างย้อนหลังบางส่วนยังไม่มีข้อมูลต้นทางรองรับ และพบว่าข้ออ้าง dimensions แบบเดียวทั้งชุดไม่ตรงกับไฟล์จริง

**Visual screening ยังไม่ครบ** มี actual display events, overview notes และ targeted native observations เพิ่มจากชุดเดิม พร้อมสถานะทุก record/duplicate alias และ checkpoint ภายใน การสร้าง sheets หรือมี coverage บางภาพทุก metadata group ไม่เท่ากับตรวจภาพทั้งหมด ไม่เผยแพร่ actual IDs, metadata, paths, ภาพ/crops หรือหลักฐานบริษัท

[Dataset Design v0.1](../docs/DATASET_DESIGN_V0_1_TH.md) ส่งมอบตาราง 6 core classes + auxiliary object, person/region/owner/validity/geometry contract, สีเป็น attribute และการเชื่อม structured output เสนอ cross-zone garment ที่ไม่สร้างเส้นแบ่งเอวสมมติ เก็บชิ้นสวมนอก core และ unknown ต่างจาก background ทุกข้อยัง PROPOSED พร้อม private native evidence binding ไม่ใช่ GT/ข้ออนุมัติผู้ใช้

แผน 2,400 unique image groups เป็น operating target ในกรอบผู้ใช้ ใช้ metadata coverage กับ visually confirmed diversity และ review ความใกล้ซ้ำ ไม่ใช่ Final Test หรือ membership ที่เลือกแล้ว [คำสั่ง resume](../docs/SCOPE_AND_OWNERSHIP_TH.md) ใช้ inventory เดิมต่อได้ ไม่ต้อง decode ทั้งชุดใหม่ สถานะจำนวนเปิดจริง/เหลือและเหตุผลการเลือก native cases อยู่ใน private report/pointer

Annotation agreement และ human annotation time ยัง NOT_MEASURED; source timestamp/modality/curation dictionary, production tool compatibility, กำลังคน/กำหนดส่ง/สิทธิ์ข้อมูลจริง OPEN การตรวจสังเคราะห์พิสูจน์พฤติกรรมเครื่องมือเฉพาะที่ทดสอบ ไม่พิสูจน์ annotation quality
