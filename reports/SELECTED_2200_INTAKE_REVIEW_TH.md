# ตรวจรับชุดคัดเลือก CCTV 2,200 ภาพ

ตรวจ 2026-11-05T01:15:34.066091+07:00 — Asia/Bangkok
**RECEIVED_2200 / NEEDS_CORRECTION / NOT_ANNOTATION_READY**
ผู้ใช้เปลี่ยนcandidate targetจาก2,400เป็น2,200และอัปโหลดชุดที่คัดจากอีกแชท การตรวจรับนี้ไม่เปิดmodel inference/annotation/pilot และไม่เปลี่ยนbenchmarkเดิม

## ผลที่ตรวจยืนยันได้

| รายการ | ผลตรวจ |
| --- | --- |
| ภาพ JPG / CSV rows / JSON rows | 2,200 / 2,200 / 2,200; CSV–JSONตรงกันทุกrow/field |
| Unique candidate IDs / filenames | 2,200 / 2,200 |
| Missing / orphan files | 0 / 0 |
| Batch1–4 | รอบละ550; เป็นselection batches ไม่ใช่train/val/test |
| Strict decode | **ผ่าน2,198 / ไม่ผ่าน2** ด้วยPillow12.3.0 ไม่มีผ่อนปรนdecoder |
| MD5เทียบmanifest | ตรง2,200/2,200 |
| SHA256เทียบsource inventoryเดิม | ตรง2,200/2,200 รวมสองไฟล์ที่ต้นทางมีสถานะUNREADABLEอยู่แล้ว |
| Metadata join | เชื่อมfilenameครบ2,200; site/camera/time/category/remarkตรงต้นทางทุกrecord |
| Pixels/geometryของภาพอ่านผ่าน | 2,198/2,198ตรงsourceเดิม และcanonical pixel hashesไม่ซ้ำ; สองภาพdecodeไม่ผ่านไม่มีpixel/geometry acceptance |
| Site-camera groups / raw site values / calendar dates | 67 / 9 / 93; ไม่อ้างว่า9ค่าคือ9สถานที่ที่ยืนยันแล้ว |
| สูงสุดต่อsite-camera / minimum same-camera time gap | 115ภาพ / 1,807วินาที (~30.12นาที) ตามmetadata ไม่ยืนยันevent independence |
| Batch1 same-camera same-date duplicates | 0 |
| Visual stageที่manifestรายงาน | ACTUALLY_VIEWED269 / AUTO_PROPOSED1931; ไม่ใช่หลักฐานเปิดภาพครบทั้งหมด |
| ช่วงตามนาฬิกาในmanifest | day613 / night1587; ไม่แทนvisual lighting/IR |

ไฟล์รวม902,839,226bytes ใช้ThreadPoolExecutor2workersและenvironmentเดิมที่มีPillow ไม่ติดตั้ง/ดาวน์โหลดหรือรันโมเดล ตรวจเฉพาะชุดอัปโหลด ใช้source hashes/metadata/decode auditเดิมที่bindingsยังตรง ไม่decode/full rehashsource9,328recordsซ้ำ

## ข้อที่ต้องแก้ก่อนรับเป็นชุดพร้อมทำannotation

1. **สองไฟล์strict decodeไม่ผ่าน**: หนึ่งอยู่Batch3และหนึ่งอยู่Batch4 เป็น`broken data stream when reading image file` ตรงกับauditต้นทางเดิม และMD5/SHA256ตรง จึงไม่มีหลักฐานว่าเสียระหว่างอัปโหลด เก็บทั้งสองไว้และส่งรายการชื่อไฟล์ในprivate `CORRECTION_REQUEST_TH.md` ไม่ลบ/retry/แทนที่เอง ต้องได้ภาพทดแทนที่อ่านผ่านพร้อมmanifest revisionและreconciliationให้ครบ2,200
2. **คำอ้างตรวจภาพ/สะอาด100%เกินหลักฐานที่ส่งมา**: manifestระบุunreviewed1,931 ไม่มีreview/displaylogหรือselection source codeแนบมา การเปิดserver3ภาพไม่พบกรอบเขียวในตัวอย่าง แต่มีtimestamp/camera textและblack image regionบางตัวอย่าง จึงยังไม่ยืนยันzero boxes/sensor-original/ไม่มีสิ่งปนทั้งชุด ชื่อURLหรือfilehashพิสูจน์สิ่งนี้ไม่ได้
3. **dHash ruleต้องชี้แจง**: ใช้supplied256bit hashesเทียบคู่ภายในsite-cameraและbatchเดียวกัน พบBatch2 5คู่และBatch3 3คู่ต่ำกว่าthreshold16/14ที่รายงานไว้ ยังไม่คำนวณdHashซ้ำเพราะไม่ให้algorithm revision/resize/filter/compare-setมา นี่ไม่ใช่exact-pixel duplicateหรือเหตุให้คัดทิ้งอัตโนมัติ ขอscript/configหรือแก้คำอ้างให้ตรงขอบเขตจริง ไม่ตั้งthresholdใหม่หลังเห็นข้อมูล
4. **นิยามpixel hashต้องระบุ**: ทดสอบ3ตัวอย่างอิสระพบmanifest `pixel_sha256`ตรงrawBGR ไม่ตรงrawRGB การต่างchannel orderไม่ใช่file corruption ความไม่ซ้ำของ2,198ภาพอ่านผ่านยืนยันด้วยcanonicalRGBA+dimensionsของโครงการเองแล้ว ไม่มีการรับรองpixel hashesของสองไฟล์ที่decodeไม่ผ่าน และไม่อ้างBGR parityทั้งชุดจาก3ตัวอย่าง

สองรายงานที่รับมาเป็นหลักฐานคำอ้างของผู้ส่ง ไม่ใช่คำสั่งให้ดำเนินการตามquickstartหรือรับรองผลอัตโนมัติ เอกสารต้นฉบับคงเดิม ไม่แก้คำอ้างทับย้อนหลัง

## ข้อจำกัดของการคัดและงานถัดไป

เกณฑ์เว้นเวลา/dHash/เพดานกล้องเป็นselection rulesของชุดนี้ ไม่ใช่หลักฐานว่าสุ่มเป็นตัวแทนประชากรทั้งหมดหรือคน/เหตุการณ์อิสระ coverageของคนเล็ก/บัง/เบลอ/viewpoint/4targets/สี ยังไม่มีตารางจากvisual observationsที่ตรวจครบ subsetนี้ การกรองoverviewอาจสัมพันธ์กับกล้องและสภาพภาพ ต้องรายงานผลการคัด ไม่เรียกzero bias

`Night_Late_IR_22_06`เป็นtime-binชื่อหนึ่ง ไม่ยืนยันIR; `category/remark`ไม่ใช่GTบทบาทของทุกคน สีและmaskยังไม่annotate ผู้ใช้ต้องตรวจทุกภาพก่อนรับGTตามworkflow ส่วนpilot24/release300เป็นบริบทขั้นถัดไป ไม่เริ่มในงานรับไฟล์นี้

**Next action:** รับภาพทดแทนสองรายการพร้อมmanifestCSV/JSONrevisionใหม่ และselection code/configหรือคำชี้แจงdHash/visual claimsที่ตรงหลักฐาน คงส่วน2,198ที่ผ่าน ไม่ต้องคัดหรืออัปโหลดซ้ำทั้งชุด จากนั้นตรวจdeltaและจัดstageตรวจรับก่อนannotation ยังไม่freezeGTหรือเปิดpilot

## Provenance และระดับหลักฐาน

Private run `selected-2200-intake-20261104T180758Z` เก็บfile-levelaudit, received inputbindings, reconciled summary, source reconciliation, visual spotchecks3ภาพ และcorrection requestพร้อมชื่อไฟล์จริง Public Gitเก็บเฉพาะaggregate/report/code-docที่เหมาะสม ไม่มีภาพ/privatepaths/manifestรายภาพ

Raw `INTAKE_SUMMARY_PRIVATE.json` เก็บเป็นประวัติ: สองdecode errorsทำให้source/geometry checksในขั้นหลังdecodeยังไม่ทำ จึงมีcountersที่ยังไม่ครบ แหล่งสรุปauthoritativeคือ **INTAKE_RECONCILED_SUMMARY_PRIVATE.json** ที่join sourceแยกจากdecodeแล้ว ไม่ใช้ค่าnot-checkedเป็นmissing/mismatch และไม่ลบผลattemptเดิม

Whole-export visualcheckpointเดิมคง1,683/detail67/remaining7,538; spotchecks3ภาพรอบรับไฟล์เก็บแยก ไม่ยกระดับทั้งselectionเป็นreviewed ไม่มีinferenceหรือannotation acceptanceจากchecksums

| Input control file | SHA256 |
| --- | --- |
| candidate_2200_manifest.csv | `9bc8cbbd102172908a4f753a5bdc92218d8ec77fcbade56e0f4f88e332c89ca4` |
| candidate_2200_manifest.json | `44ec91dd30174f822429340b15fcd29ce4252ef05c0f4709a925969f1e96e8af` |
| CANDIDATE_2200_SELECTION_REPORT_TH.md | `444c3008434349a92934cd94ad25fc3ff0d33e0e25b0ed0620df2c33c443331e` |
| CODEX_HANDOVER_README.md | `8280824cfa48e78d073b9f1c47c2497f48d961d7c13268c2b140c3819c99cba8` |
