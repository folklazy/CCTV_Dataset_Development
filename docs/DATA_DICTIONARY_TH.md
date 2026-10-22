# Data dictionary — schema ที่นำมาจาก export เดิม

นำกติกาและ field meanings จาก data dictionary เดิมมาใช้ต่อ สถิติและค่าจริงอยู่ใน private archive ไม่ได้ตรวจเนื้อหา export ใหม่ในรอบตั้ง workspace

| Field | ประเภท | ความหมายและข้อจำกัด |
| --- | --- | --- |
| filename | string | join key ที่ต้องตรวจค่าว่าง/uniqueness กับ archive ทุกครั้ง ไม่ใช้ row order หรือ content hash แทน identity |
| site | string | ข้อมูลสถานที่ตาม record; แยก unknown literal ออกจากสถานที่จริงโดยเก็บ raw |
| camera_name | string | ข้อมูลมุมกล้อง; ใช้ร่วมกับ site และตรวจ uniqueness |
| category | string | ข้อมูลกำกับ record ตามต้นทาง ไม่ใช่ person-instance ownership หรือ parsing GT |
| incident_timestamp | string | เก็บ raw/explicit UTC offset และ parse แยก ไม่เดา named timezone |
| curate_status | string | คง raw status; pending ไม่ลบล้างประวัติ selected/rejected/flagged และไม่ map เป็น unreviewed โดยไม่มีนิยาม |
| curate_note | string/null | คง notes เดิม; ช่องว่างใน export ไม่พิสูจน์ว่า notes ต้นทางไม่มีหรือถูกลบ |
| remark | string/null | ข้อความประกอบที่อาจละเอียดอ่อน เก็บภายนอก Git ไม่แปลงเป็น label โดยอัตโนมัติ |

เทียบ CSV/JSON/XLSX ทุก field และจำนวนซ้ำ ใช้ null→empty normalization เฉพาะ comparison โดยไม่เขียนกลับต้นทาง CSV row locator ใช้ trace ภายใน snapshot ไม่ใช่ stable event/person ID

Identity, byte SHA256, ZIP CRC header, decoded image validity และ person geometry เป็นคนละข้อมูล CRC header ไม่เท่ากับ payload verification คนหลายคนในภาพต้องมี binding ที่พิสูจน์ได้ ไม่ถ่ายทอด category ให้ทุกคนเอง
