# รายงาน

รายงานตั้ง workspace ฉบับ local คือ `WORKSPACE_SETUP_REPORT_TH.md` ใต้ work_root ตาม ignored config/local.json มี path จริง, Git commit, copy manifest และผลตรวจ ไม่ commit absolute local paths หรือ raw staged-review evidence

รายงานก่อนย้ายทั้งหมดอยู่ใน work_root/legacy/cctv_dataset/reports/ รวม bounded visual review ที่ใหม่กว่ารายงานส่งกลับเดิม ประวัติ run records และ preview เดิมอยู่ใน archive เดียวกัน ห้ามนำข้อความ “ยังไม่ตรวจภาพ” ในรายงานเก่ามาใช้ลบล้างประวัติใหม่

รายงานที่จะเก็บใน Git ต้องใช้ข้อมูลกระบวนการ/ผลรวมที่จำเป็น ไม่ใส่ source record IDs, site/camera names, notes, credentials หรือ raw metadata โดยไม่มีเหตุจำเป็นและการอนุมัติ
