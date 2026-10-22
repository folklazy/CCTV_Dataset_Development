# Data dictionary — schema ที่นำมาจาก export เดิม

ทบทวน 22 ตุลาคม 2026: อ่าน CSV ปัจจุบันและ hash ของสาม metadata exports เทียบหลักฐานเดิมแล้ว ตารางด้านล่างแยกชื่อ field ที่ตรวจได้ออกจากความหมายระบบที่ยังขาด สถิติ/ค่า/path จริงเก็บภายนอก Git ตาม [รายงานฐานงาน](../reports/README.md) ไม่ใช้ schema inspection เป็นการตรวจภาพ

พบเพียงแปด fields ในตาราง ไม่มี explicit event ID, sequence/burst ID, track/person ID, bbox/mask หรือ modality field กลุ่ม site+camera+เวลาเป็น candidate สำหรับสำรวจ ไม่ใช่ลำดับเหตุการณ์ที่ยืนยันแล้ว ค่า unknown ที่เป็น literal ต้องแยกจากจำนวนสถานที่จริง

| Field | ประเภท | ความหมายและข้อจำกัด |
| --- | --- | --- |
| filename | string | join key ที่ต้องตรวจค่าว่าง/uniqueness กับ archive ทุกครั้ง ไม่ใช้ row order หรือ content hash แทน identity |
| site | string | ข้อมูลสถานที่ตาม record; แยก unknown literal ออกจากสถานที่จริงโดยเก็บ raw |
| camera_name | string | ข้อมูลมุมกล้อง; ใช้ร่วมกับ site และตรวจ uniqueness |
| category | string | ข้อมูลกำกับ record ตามต้นทาง ไม่ใช่ person-instance ownership หรือ parsing GT |
| incident_timestamp | string | เก็บ raw/explicit UTC offset และ parse แยก ไม่เดา named timezone; ยังต้องยืนยันความหมาย event/capture time กับ source dictionary ไม่แทนด้วย timestamp ในชื่อไฟล์หรือ filesystem mtime |
| curate_status | string | คง raw status; pending ไม่ลบล้างประวัติ selected/rejected/flagged และไม่ map เป็น unreviewed โดยไม่มีนิยาม |
| curate_note | string/null | คง notes เดิม; ช่องว่างใน export ไม่พิสูจน์ว่า notes ต้นทางไม่มีหรือถูกลบ |
| remark | string/null | ข้อความประกอบที่อาจละเอียดอ่อน เก็บภายนอก Git ไม่แปลงเป็น label โดยอัตโนมัติ |

เทียบ CSV/JSON/XLSX ทุก field และจำนวนซ้ำ ใช้ null→empty normalization เฉพาะ comparison โดยไม่เขียนกลับต้นทาง CSV row locator ใช้ trace ภายใน snapshot ไม่ใช่ stable event/person ID

Identity, byte SHA256, ZIP CRC header, decoded image validity และ person geometry เป็นคนละข้อมูล CRC header ไม่เท่ากับ payload verification คนหลายคนในภาพต้องมี binding ที่พิสูจน์ได้ ไม่ถ่ายทอด category ให้ทุกคนเอง
