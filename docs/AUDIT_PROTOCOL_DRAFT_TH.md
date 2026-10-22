# Protocol dataset audit — DRAFT

เนื้อหาหลักนำมาจาก protocol เดิม ขั้นตั้ง workspace รอบนี้ตรวจ config/path และข้อมูลสังเคราะห์เท่านั้น ประวัติ audit บริษัทเก็บภายนอก Git ทุก run ใหม่อยู่ใต้ work_root/runs และต้องไม่ทับ source/repository

## ลำดับการทำงานภายหลัง

1. อ่าน schema CSV/JSON/notes และ data dictionary จริง บันทึก encoding, row counts, ID uniqueness และ join keys ที่พิสูจน์ได้ ห้าม join ด้วย row order หรือ basename ที่กำกวม
2. อ่าน snapshot แบบ read-only ตรวจ file stat ก่อน/หลังอ่าน พร้อม hash ของ bytes ที่ใช้ หากเปลี่ยนให้ retry ไม่เกิน 3 ครั้ง; ถ้ายังไม่นิ่งให้รายงาน unstable และไม่อ้าง snapshot เดียว ห้าม lock/หยุดแอป
3. สร้าง run ใหม่ใต้ `work_root/runs/` และยืนยันว่า output ไม่อยู่ใต้ source root ไม่ตาม directory symlink โดยอัตโนมัติ ระบุสิ่งที่ข้ามและอ่านไม่ได้
4. Inventory CPU แบบจำกัดภาระ เริ่ม 1 worker เป็น operational proposal; checkpoint เป็นช่วง บันทึก source ID และ audit ID แยกจาก content hash เก็บ path สัมพัทธ์ size SHA256 decode format dimensions และสถานะที่มีหลักฐาน
5. สรุป records, existing files, readable images, unique byte hashes และ exact duplicate groups แยกกัน metadata hash ไม่ใช่ image hash; similarity ถ้าทำเป็น candidate near-duplicate เท่านั้น
6. ตรวจ orphan rows/files, ambiguous joins, raw/normalized status, missing/unknown; ใช้ unreviewed เฉพาะเมื่อ schema รองรับ สรุป site/camera/time/status พร้อม denominator และ timezone ที่รู้จริง
7. เทียบ baseline โดยเก็บประวัติ แยกการเปลี่ยนจากเวลา snapshot กับความต่างของนิยามประชากรและวิธีนับ ถ้าข้อมูลขาดให้ null ไม่แทนด้วย 0
8. เลือก coverage sample และ edge-case sample หลังทราบ strata; บันทึก seed วิธีเลือก membership probabilities เมื่อมี และ inspected status ห้ามรวมสองกลุ่มเพื่อประมาณ prevalence โดยไม่มีวิธีรองรับ
9. ดูภาพเต็ม/ต้นฉบับเมื่อผู้ใช้พร้อม บันทึก observation/measurement และ uncertainty จริงตาม K/X; ไม่อนุมาน IR จากขาวดำหรือคนจาก event category
10. เชื่อม REQ → E/C → ภาพจริง → H → ผล pilot → DEC; ทำรายงานก่อนเริ่ม annotation/benchmark ขั้นใหญ่

## หน่วยและแบบฟอร์ม

ไฟล์ใน `templates/` เป็นโครงคอลัมน์ร่าง ไม่มีแถวตัวอย่างที่นับเป็นผลตรวจ ให้เพิ่ม data dictionary หลังเห็น schema จริง CSV headers ไม่ใช่ annotation ontology และไม่มี numeric class IDs

| Artifact ใน run จริง | หน่วย / กติกา |
| --- | --- |
| source_inventory.csv | หนึ่งแถวต่อไฟล์ต้นทาง; audit ID คงที่ใน run; metadata หลายแถวต่อไฟล์ใช้ join table แยก |
| metadata_linkage.csv | หนึ่งแถวต่อ source record/match candidate; unmatched/ambiguous ระบุชัด |
| metadata_audit.json | snapshot + นิยาม denominator + counts/join issues; ใช้ null เมื่อยังไม่วัด |
| duplicate_groups.csv | หนึ่งแถวต่อสมาชิก exact SHA256 group; ไม่ลบ source |
| visual_sample_manifest.csv | membership แยกกลุ่ม coverage/edge_case; ภาพเดียวอยู่สองกลุ่มได้ |
| visual_case_register.csv | หนึ่งแถวต่อ case observation; ภาพหนึ่งมีหลายเคสได้; review status แยก evidence status |
| contact sheets | local เท่านั้น; derived และใช้ย้อนกลับ original ได้ |

measurement ที่จะใช้ต้องระบุ geometry: bbox height เป็น px; bbox area ratio = bbox area / frame area; visible mask area ratio = visible mask pixels / frame area เมื่อมี mask จริง ไม่แทนกัน ไม่คำนวณขนาดคนจาก frame dimensions อย่างเดียว

## เรื่องที่ยังต้องตัดสิน

H-01 coarse/fine, H-02 anatomical side, H-03 type/length, H-04 color, H-05 pattern และ H-06 validity ยังเป็นแผนทดสอบจาก foundation ต้องได้ภาพ ผู้ทำจริง และกติกาก่อนวัด ยังไม่เลือก threshold หรือจำนวน pilot ล่วงหน้า กรณีมีผู้ทำคนเดียวให้รายงาน intra-annotator consistency ตามจริง

ไม่เริ่ม full benchmark, training, model inference บน CCTV, annotation ทั้งชุด, split หรือ mapping ที่ตรึงถาวรจาก protocol ร่างนี้
