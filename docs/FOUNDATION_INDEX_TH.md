# เอกสารตั้งต้น

เนื้อหากระบวนการ/ร่างจาก handoff เดิมนำมาใช้ต่อ โดยแยกข้อมูลเฉพาะบริษัทกับ historical reports ออกไปยัง private legacy archive ฉบับใน repository ที่ปรับแล้วมี migration mapping และ SHA256 ของฉบับก่อนแก้เก็บภายนอก Git การคัดข้อความไม่ใช่การอนุมัติ taxonomy หรือการตรวจ paper/มาตรฐานซ้ำในรอบย้ายงาน

เริ่มจาก [หน้าโครงการ](../README.md) เพื่ออ่านโจทย์ สถานะและกระบวนการ แล้วอ่านข้อกำหนด → หลักฐาน/สมมติฐาน → ทะเบียนเคส → protocol ตามงานที่จะทำ การตั้งค่าเครื่องและคำสั่งอยู่ใน [วิธีใช้งาน](SCOPE_AND_OWNERSHIP_TH.md) ส่วน [ดัชนีหลักฐาน](../reports/README.md) อธิบายว่าข้อความใดยืนยันจากไฟล์ปัจจุบันหรือมีเพียงรายงานประวัติ

| เอกสาร | ใช้เพื่อ | สถานะ |
| --- | --- | --- |
| [AGENTS.md](../AGENTS.md) | กฎงาน repository อิสระ | ปัจจุบัน |
| [ข้อกำหนด](BENCHMARK_REQUIREMENTS_DRAFT_TH.md) | USER CONFIRMED objectives หลัง eafe703 แยกจาก REQ/DEC วิธีการ | เป้าหมายยืนยันแล้ว; taxonomy/annotation/metrics/QA PROPOSED |
| [หลักฐานและสมมติฐาน](EVIDENCE_AND_HYPOTHESES_TH.md) | source/locator → การปรับใช้ → สิ่งต้องพิสูจน์ → hypothesis | ทบทวนห้าแหล่งแบบเจาะจงแล้ว; ไม่มีผล pilot |
| [ทะเบียนเคส](CASE_REGISTER_DRAFT_TH.md) | K/X tags, วิธีเลือกภาพและแบบบันทึก | draft; status เดิมไม่ใช่ผลตรวจรอบนี้ |
| [Protocol/แผนสำรวจ](AUDIT_PROTOCOL_DRAFT_TH.md) | preparation 24+8 และ bounded visual guard/วิธีบันทึกผล | สำรวจรายการเดิมแล้ว; ไม่มี annotation/final split |
| [Data dictionary](DATA_DICTIONARY_TH.md) | fields ที่ตรวจใน export ปัจจุบันและข้อจำกัด record/person/time | ตรวจ schema/hash แล้ว; ความหมายระบบยังมีช่องว่าง |
| [Decision log](DECISION_LOG_TH.md) | การเปลี่ยนแปลงตั้งแต่แยก repository | append-only |
| [Dataset Design v0.1](DATASET_DESIGN_V0_1_TH.md) | core/auxiliary classes, owner/geometry/validity, attributes และแผนคัดสองพันกว่าไม่เกินสามพัน | PROPOSED; whole-export visual review ยังไม่ครบ |
| [คู่มือทดลอง v0.1](../templates/annotation_guideline.template.md) | R01–R12 → ทางเลือก/เหตุผล/ผลกระทบ; evidence binding และภาพอยู่ภายใน | PROPOSED รอมนุษย์ทบทวน |
| [แผน pilot/QA](../templates/quality_review.template.md) | decision priorities, ขนาดเริ่มที่เสนอ, timing/review/revision และข้อจำกัดเมื่อทำคนเดียว | PROPOSED; ยังไม่เริ่ม |
| [Contract example](../templates/annotation_contract_v0_1.example.json) | schema placeholder แยก ID/owner/states/geometry/display/provenance | ไม่ใช่ annotation จริงหรือ schema ที่อนุมัติแล้ว |
| [Release manifest template](../templates/release_manifest.example.json) | source/annotation/guideline/code references ที่จะผูกต่อรุ่น | template-only; ยังไม่มีค่ารุ่นจริง |

Handoff เต็ม รายงานเก่า รายละเอียดบริษัท และภาพตัวอย่างเดิมอยู่ใน work_root/legacy ตาม local config ไม่ใช่ dependency ที่ต้อง commit หรือ fetch เพื่อรันทดสอบสังเคราะห์
