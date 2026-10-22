# Decision log

ประวัติก่อนแยก repository เก็บ verbatim ใน work_root/legacy/cctv_dataset/docs/DECISION_LOG_TH.md พร้อม SHA256/path map ภายนอก Git ไม่แก้ย้อนหลังให้ดูเหมือนงานใหม่มีหลักฐานมาก่อน

| ID / วัน | ผู้กำหนด / สถานะ | ข้อสรุปและเหตุผล | ผลกระทบ |
| --- | --- | --- | --- |
| WS-001 / 2026-10-22 | ผู้ใช้ / CONFIRMED | แยก dataset-development repository และเปิด VS Code ได้ | สร้าง Git อิสระระดับเดียวกับ workspace เดิม; ไม่มี remote |
| WS-002 / 2026-10-22 | Codex / IMPLEMENTED | แยก source/work/repository; absolute paths อยู่ใน local config | outputs/annotation/release manifests จริงอยู่นอก Git |
| WS-003 / 2026-10-22 | Codex / IMPLEMENTED | คัดลอกและตรวจ SHA256; archive ต้นฉบับก่อนปรับเอกสาร | legacy records ไม่ถูกเขียน path ใหม่; รายงานเฉพาะบริษัทอยู่นอก Git |
| WS-004 / 2026-10-22 | ผู้ใช้ / CONFIRMED | ยังไม่ annotate หรือทดสอบโมเดล ไม่ตรึง taxonomy/สี/QA | setup tests ใช้ synthetic data; ไม่เปิดภาพใหม่ |
| WS-005 / 2026-10-22 | Codex / IMPLEMENTED | ไม่มี Git author identity ตั้งไว้ในเครื่อง | initial local commit ใช้ชื่อ neutral `Dataset Workspace` และ `dataset-workspace@localhost` เฉพาะ repository นี้ |
| WS-006 / 2026-10-22 | ผู้ใช้ / CONFIRMED | เปลี่ยนเป้าหมายเผยแพร่เป็น public repository `folklazy/CCTV_Dataset_Development` แทนคำสั่ง private ก่อนหน้า | ตั้ง origin ตาม URL ที่ระบุ ตรวจประวัติทุก commit ก่อน push; รักษางานทั้งสองฝั่ง ไม่ force-push และคงข้อมูลจริง/รายงานภายในไว้นอก Git |
| DOC-001 / 2026-10-22 | ผู้ใช้ / CONFIRMED; Codex / IMPLEMENTED | ปรับ README เป็นหน้าโครงการวิจัย แยกคู่มือเครื่องไปเอกสารพื้นที่งาน ใช้การจัดเนื้อหา/ลิงก์หลักฐานของ repo ตัวอย่าง YOLO เป็นแนวทางโดยไม่ยกผลทดลองมาใช้ | แยกสถานะจากไฟล์ปัจจุบัน รายงานเก่า และแผนงาน เพิ่มช่อง annotation revision/code references ที่ยังว่างใน release template ไม่ตรึง ontology/QA ไม่เริ่ม annotation หรือรันโมเดล |
| PLAN-001 / 2026-10-22 | ผู้ใช้ / CONFIRMED เฉพาะขอบเขต; Codex / IMPLEMENTED การตรวจ/จัดแผน | ตรวจฐานงานด้วย config/metadata hashes/หลักฐานเดิมแบบจำกัดและ PDF ต้นฉบับห้าแหล่ง แยกข้อเท็จจริง/รายงานเก่า/ข้อเสนอ/ข้อขัดแย้ง/ข้อมูลขาด แทนการตรวจ archive/ภาพทั้งชุดซ้ำ; บันทึกวิธีและข้อจำกัดในรายงานภายในและ reports/README.md | แก้คำอ้าง category เกินหลักฐานและสถานะเตรียม pilot; DEC-01–09, งบ exploration และ H-01–06 ยัง OPEN/PROPOSED ไม่อนุมัติคลาส สี splits QA หรือ release ไม่มีผลต่อ source/status/annotation/model scores |

รายการใหม่ต้องมีวัน ผู้ตัดสิน สถานะ หลักฐาน/locator เหตุผล ทางเลือก และผลกระทบต่อรุ่นคู่มือ/ข้อมูล/คะแนน ถ้า supersede ให้ระบุรายการเดิมและเก็บประวัติ ไม่เปลี่ยน OPEN เป็น ACCEPTED โดยไม่มีการตัดสินจริง
