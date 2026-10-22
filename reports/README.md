# รายงาน

## อ่านสถานะให้ตรงกับระดับหลักฐาน

[หน้าโครงการ](../README.md) สรุปสิ่งที่พัฒนาและสิ่งที่ยังไม่เริ่ม ตารางนี้ระบุขอบเขตที่ผู้อ่านตรวจได้ โดยไม่เผยแพร่ข้อมูลบริษัทหรือทำสำเนารายงานภายในออกมาใน Git

| แหล่ง | ระดับหลักฐาน | ใช้ยืนยันอะไร / ยังยืนยันอะไรไม่ได้ |
| --- | --- | --- |
| [scripts](../scripts/), [tests](../tests/), [config example](../config/audit.example.json) และ Git history | ไฟล์ปัจจุบันที่ตรวจได้สาธารณะ | การมีเครื่องมือและพฤติกรรมที่ทดสอบด้วย synthetic inputs ไม่ใช่ความถูกต้องของ annotation |
| [ข้อกำหนด](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md), [เคส](../docs/CASE_REGISTER_DRAFT_TH.md), [templates](../templates/) | DRAFT / PROPOSED | ทางเลือกและสิ่งที่วางแผนจะตรวจ ไม่ใช่ class policy/QA หรือ release ที่อนุมัติแล้ว |
| WORKSPACE_SETUP_REPORT_TH.md ภายใน work_root | รายงานการตั้ง workspace และเชื่อม GitHub | migration/paths/checksums/Git receipts ณ เวลาบันทึก ไม่ใช่การตรวจคุณภาพภาพหรือ reference GT |
| CCTV_RETURN_TO_CHAT_TH.md ใน private legacy archive | รายงาน package/metadata audit เดิม | จำนวนและสถานะตาม export/snapshot เก่า ไม่ใช่ยอดปัจจุบันหรือหลักฐานการเปิดดูภาพภายหลัง |
| CCTV_BOUNDED_VISUAL_SCOPE_REVIEW_TH_20261020.md ใน private legacy archive | รายงานการดูภาพแบบจำกัดที่ใหม่กว่า package report | มีประวัติการสำรวจตัวอย่าง ไม่ใช่ full image audit, prevalence, annotation agreement หรือ model score |

รอบปรับหน้าโครงการวันที่ 22 ตุลาคม 2026 ตรวจ source/config/templates/Git และอ่านรายงานเดิม ไม่ได้ตรวจภาพหรือวัดคุณภาพ annotation ใหม่ ในพื้นที่ `annotations/` และ `releases/` ภายนอกที่ตรวจยังไม่มีไฟล์ใช้งานจริง จึงไม่ประกาศ annotation/release หรือคะแนนคุณภาพจากการมีโครงสร้างโฟลเดอร์

## รายงานภายในและการคงประวัติ

รายงานตั้ง workspace ฉบับ local คือ `WORKSPACE_SETUP_REPORT_TH.md` ใต้ work_root ตาม ignored config/local.json มี path จริง, Git commit, copy manifest และผลตรวจ ไม่ commit absolute local paths หรือ raw staged-review evidence

รายงานก่อนย้ายทั้งหมดอยู่ใน work_root/legacy/cctv_dataset/reports/ รวม bounded visual review ที่ใหม่กว่ารายงานส่งกลับเดิม ประวัติ run records และ preview เดิมอยู่ใน archive เดียวกัน ห้ามนำข้อความ “ยังไม่ตรวจภาพ” ในรายงานเก่ามาใช้ลบล้างประวัติใหม่

รายงานที่จะเก็บใน Git ต้องใช้ข้อมูลกระบวนการ/ผลรวมที่จำเป็น ไม่ใส่ source record IDs, site/camera names, notes, credentials หรือ raw metadata โดยไม่มีเหตุจำเป็นและการอนุมัติ
