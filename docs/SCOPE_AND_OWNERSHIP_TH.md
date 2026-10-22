# ขอบเขตและเจ้าของไฟล์

Repository นี้เป็นงานสร้าง CCTV Human Parsing Evaluation Dataset แยกจากงานทดลองโมเดล พื้นที่งานเดิมและผลทดลองเดิมยังคงอยู่ ไม่มี Git repository ซ้อนอยู่ใน workspace เดิม

| พื้นที่ | บทบาท | การจัดการ |
| --- | --- | --- |
| repository | source, config example, docs, tests, templates, reports index, VS Code workspace | local Git; ตรวจ staged ก่อน commit |
| dataset_root จาก local config | ต้นทางภาพ/metadata ที่อยู่เดิม | read-only ในเครื่องมือ; ไม่เปลี่ยน permissions หรือสถานะคัดภาพ |
| work_root จาก local config | generated runs, annotation working files, outputs และ real release manifests | นอก repository; ยังไม่มี annotation/release จริง |
| work_root/legacy | สำเนาเดิมแบบ byte-identical รวมรายงาน/หลักฐานส่วนตัว | เก็บ provenance; ไม่แก้ path ใน historical run records |
| work_root/provenance | mapping old→new, SHA256, validation และ staged review receipt | local/private |

Absolute paths อยู่เฉพาะ ignored local config และ external report; code resolve root จากตำแหน่งตัวเอง เครื่องมือปฏิเสธ source/work/repository ที่ทับซ้อนกัน ไม่มี symlink data ภายใน repository

ขั้นถัดไปต้องระบุว่ากำลังออกแบบคู่มือ สำรวจภาพ หรือ annotate และใช้หลักฐาน/decision ตามขั้นนั้น การย้าย workspace ไม่อนุมัติ annotation, inference, training หรือ benchmark และไม่ตรึง class/color/QA policy

รายงานเดิมที่ขัดกันด้านเวลาเก็บเป็นประวัติทั้งหมด: package-only report เกิดก่อน bounded visual review คงความต่างระหว่าง observed/measured/reported และไม่ย้ายข้อสรุปใน sample ไปเป็น prevalence ทั้งชุด
