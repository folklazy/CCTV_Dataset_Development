# เอกสารตั้งต้น

เนื้อหากระบวนการ/ร่างจาก handoff เดิมนำมาใช้ต่อ โดยแยกข้อมูลเฉพาะบริษัทกับ historical reports ออกไปยัง private legacy archive ฉบับใน repository ที่ปรับแล้วมี migration mapping และ SHA256 ของฉบับก่อนแก้เก็บภายนอก Git การคัดข้อความไม่ใช่การอนุมัติ taxonomy หรือการตรวจ paper/มาตรฐานซ้ำในรอบย้ายงาน

| เอกสาร | ใช้เพื่อ | สถานะ |
| --- | --- | --- |
| [AGENTS.md](../AGENTS.md) | กฎงาน repository อิสระ | ปัจจุบัน |
| [ข้อกำหนด](BENCHMARK_REQUIREMENTS_DRAFT_TH.md) | REQ/DEC และหน่วยประเมินที่เสนอ | DRAFT |
| [หลักฐานและสมมติฐาน](EVIDENCE_AND_HYPOTHESES_TH.md) | source/locator → candidate → hypothesis → pilot | inherited draft; ไม่มีผล pilot ใหม่ |
| [ทะเบียนเคส](CASE_REGISTER_DRAFT_TH.md) | K/X tags, วิธีเลือกภาพและแบบบันทึก | draft; status เดิมไม่ใช่ผลตรวจรอบนี้ |
| [Protocol](AUDIT_PROTOCOL_DRAFT_TH.md) | snapshot, linkage, inventory, sampling, QA | draft |
| [Data dictionary](DATA_DICTIONARY_TH.md) | ความหมาย fields และข้อจำกัด record/person | schema-only |
| [Decision log](DECISION_LOG_TH.md) | การเปลี่ยนแปลงตั้งแต่แยก repository | append-only |

Handoff เต็ม รายงานเก่า รายละเอียดบริษัท และภาพตัวอย่างเดิมอยู่ใน work_root/legacy ตาม local config ไม่ใช่ dependency ที่ต้อง commit หรือ fetch เพื่อรันทดสอบสังเคราะห์
