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
