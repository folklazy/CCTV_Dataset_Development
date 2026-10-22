# CCTV Human Parsing Evaluation Dataset

โครงการวิจัยเพื่อพัฒนาชุดภาพ CCTV พร้อมคำตอบอ้างอิงสำหรับประเมิน **Human Parsing ระดับบุคคล** โดยเชื่อมส่วนร่างกายและเสื้อผ้าที่มองเห็นกับเจ้าของในภาพ และบันทึกที่มาข้อมูล กติกา annotation การตรวจทาน และรุ่นของชุดประเมินให้ตรวจย้อนกลับได้

**สถานะ ณ 22 ตุลาคม 2026: ตรวจฐานงานและหลักฐานแล้ว มีแผนสำรวจข้อมูลฉบับร่าง ยังไม่เริ่มสำรวจภาพรอบใหม่หรือ annotation pilot** ยังไม่มีชุด annotation หรือ dataset release ที่ยืนยันในพื้นที่งานที่ตรวจ และยังไม่มีผลตรวจคุณภาพ annotation รายงานนี้ไม่ประกาศผลประเมินโมเดล

รอบปัจจุบันยืนยันเฉพาะฐานงานและข้อจำกัดตาม [รายงานสถานะห้าระดับ](reports/README.md) เริ่มอ่าน [ประเด็นตัดสินใจ/คำถาม](docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md) → [แผนสำรวจร่าง](docs/AUDIT_PROTOCOL_DRAFT_TH.md) → [การตรวจแหล่งต้นฉบับห้างาน](docs/EVIDENCE_AND_HYPOTHESES_TH.md) รายละเอียดในร่างเดิมยังแก้ไขได้ ไม่ถือว่าผู้ใช้อนุมัติทั้งหมด

## ที่มาและวัตถุประสงค์

ภาพ CCTV ในการใช้งานจริงอาจมีหลายคนอยู่ใกล้กัน รายละเอียดคนเล็ก ส่วนที่ถูกบัง หรือเสื้อผ้าที่ตัดสินได้เพียงบางคุณลักษณะ การจะวัด Human Parsing ให้ตีความได้จึงต้องกำหนดทั้งสิ่งที่ต้องการประเมิน สิ่งที่ผู้ทำ annotation มองเห็นได้ และกติกาสำหรับส่วนที่ไม่แน่ใจ

เป้าหมายของโครงการคือ:

1. สร้างกรอบข้อมูลที่เชื่อมภาพกับ source record และประวัติการคัดเลือก โดยแยกจำนวน records ภาพ และบุคคลออกจากกัน
2. ออกแบบคลาสและ attributes จากคำถามวิจัย แหล่งอ้างอิง และหลักฐานภาพจริง พร้อมบันทึกเหตุผลของทางเลือกแต่ละแบบ
3. พัฒนาคำตอบอ้างอิงที่ผ่านกระบวนการ annotation/review/QA ที่ระบุได้ และรายงาน coverage กับความไม่แน่นอน
4. เตรียมชุดประเมินเป็นรุ่นที่ผูกกับคู่มือ annotation revision และ code commit เพื่อให้การประเมินในอนาคตทำซ้ำได้

งานนี้รับผิดชอบ **การพัฒนา dataset** ส่วนการคัดเลือกและรันโมเดลเป็นอีก workstream เมื่อ reference data และ protocol พร้อมจึงนำไปใช้ประเมินแบบจำลองที่เลือกไว้ ผลจาก public benchmark ไม่ได้ยืนยันผลบน CCTV โดยอัตโนมัติ

## ขอบเขตและคำถามการออกแบบ

หน่วยที่เสนอคือภาพเต็ม → person instance ภายในภาพ → semantic region ที่มีเจ้าของ ส่วนสี ความยาว และลวดลายเป็น attributes ที่ต้องพิจารณา applicability/observability แยกกัน ความละเอียดของส่วนต่าง ๆ ซ้าย/ขวาของบุคคล และขอบเขตอุปกรณ์ยังเป็นคำถามเปิด

เริ่มอ่าน [ข้อกำหนดและหน่วยประเมินร่าง](docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md) กับ [หลักฐานและสมมติฐาน H-01–H-06](docs/EVIDENCE_AND_HYPOTHESES_TH.md) ซึ่งเชื่อมความต้องการ → source/locator → candidate → กรณีทดสอบ → วิธีตัดสิน ตัวเลือกเหล่านี้ยังไม่ใช่ class list, class IDs, palette หรือเกณฑ์คุณภาพที่ตรึงแล้ว

## สถานะปัจจุบันและระดับหลักฐาน

| ส่วนงาน | สถานะ | หลักฐานและขอบเขตที่อ้างได้ |
| --- | --- | --- |
| Repository และเครื่องมือสำรวจ | มีแล้ว ตรวจจากไฟล์ปัจจุบันได้ | [scripts/](scripts/), [tests/](tests/), [config example](config/audit.example.json); การทดสอบสังเคราะห์ตรวจพฤติกรรมเครื่องมือ |
| ข้อกำหนด เคส และแบบฟอร์ม | มีแล้วในสถานะ DRAFT | [ดัชนีเอกสาร](docs/FOUNDATION_INDEX_TH.md), [templates/](templates/); การมีไฟล์ไม่ได้ยืนยันว่ากติกาใช้ annotate ได้จริง |
| Metadata/หลักฐาน audit เดิม | ตรวจ metadata แบบจำกัดและเทียบ hash แล้ว | [รายงานฐานงาน](reports/README.md); filename ตรง inventory เดิม แต่ไม่อ่าน ZIP payload ใหม่หรือยืนยันคุณภาพภาพ/annotation |
| การดูภาพแบบจำกัดก่อนแยก workspace | มีรายงานเดิม เก็บภายใน | รอบนี้ตรวจไฟล์ manifest/receipt ไม่เปิดภาพซ้ำ และไม่อ้าง prevalence จาก sample |
| คู่มือฉบับใช้งานและ annotation pilot | ยังไม่เริ่ม ต้องผ่าน exploration/ตัดสิน scope ก่อน | [guideline template](templates/annotation_guideline.template.md), [case register](docs/CASE_REGISTER_DRAFT_TH.md); ยังไม่มีผล pilot/independent agreement ให้รายงาน |
| Annotation ที่ผ่าน QA และ dataset release | ยังไม่มีในพื้นที่งานที่ตรวจ | [QA template](templates/quality_review.template.md), [release manifest template](templates/release_manifest.example.json); ยังไม่มี manifest รุ่นจริงหรือผลรับรองคุณภาพ |

Checksum ที่ตรงกัน การจับคู่ชื่อไฟล์ หรือ synthetic tests ที่ผ่าน เป็นหลักฐานด้านไฟล์และการทำงานของเครื่องมือ การยืนยันความถูกต้องของ annotation ต้องได้ผลตรวจจากกระบวนการที่กำหนดต่างหาก ตัวเลขจากรายงานเก่าและข้อสังเกตใน sample ไม่ใช้แทนจำนวนล่าสุดหรือ prevalence ของทั้งชุด

## กระบวนการพัฒนา dataset

ขั้นต่อไปนี้เป็นแผนดำเนินงาน ไม่มีขั้น annotation/QA/release ที่ถือว่าสำเร็จจากการมี template เพียงอย่างเดียว

| ขั้น | สิ่งที่จะดำเนินการ | หลักฐานที่ต้องเก็บ |
| --- | --- | --- |
| 1. ระบุที่มาและสำรวจข้อมูล | ตรึง snapshot ที่อ่านจริง ตรวจ schema, filename linkage, missing/ambiguous records และภายหลังตรวจ decode/hash รายภาพ | source version, inventory, snapshot time, joins, duplicate candidates และ denominator |
| 2. ออกแบบ ontology และคู่มือ | พิจารณาคลาส/attributes ตามงานและสิ่งที่สังเกตได้ เลือก coverage sample แยกจาก edge-case discovery | rationale, source locator, case records, inclusion/exclusion และข้อที่ยัง OPEN |
| 3. ทดลอง annotation pilot | ให้ผู้ทำใช้คู่มือร่าง บันทึกเวลา ความไม่แน่ใจ และผลอิสระก่อน adjudication | guideline version, annotation revision, independent results และ disagreement log |
| 4. ตรวจและแก้คุณภาพ | ตรวจโครงสร้าง/geometry/ownership รวมกับความสม่ำเสมอของคำตอบและ coverage แล้วแก้กติกาอย่างมีประวัติ | QA policy, review/adjudication records, unresolved cases และเหตุผลการแก้ |
| 5. เตรียมชุดประเมินเป็นรุ่น | กำหนด membership และการแยกกลุ่มข้อมูลตาม policy ที่อนุมัติ พร้อมข้อจำกัดการใช้ | release manifest, hashes, source/annotation/guideline versions และ code commit |

รายละเอียดวิธี snapshot หน่วยวัด และข้อจำกัดอยู่ใน [audit protocol ร่าง](docs/AUDIT_PROTOCOL_DRAFT_TH.md) ยังไม่สร้าง train/validation/test split หรือเปลี่ยนสถานะคัดภาพในรอบนี้

## หลักการสร้างคำตอบอ้างอิงและตรวจทาน

- เสนอให้ annotate พื้นที่ที่มองเห็นจริง พร้อม person ownership ไม่วาดเติมส่วนที่ถูกบังโดยไม่มี protocol งาน amodal แยก
- แยก absent, not applicable, unobservable/unknown และ unannotated ไม่ตีความ unknown เป็น background อัตโนมัติ และไม่เดาสีวัตถุจากภาพที่ตัดสินสีไม่ได้
- เก็บผล annotation อิสระก่อนตัดสินร่วม รายงาน agreement ให้ตรงชนิดข้อมูล ควบคู่ coverage, unknown rate และภาระเวลา หากมีผู้ทำคนเดียวให้ระบุเป็น intra-annotator consistency
- ส่งกรณีกำกวมเข้าทะเบียนเคสและ adjudication พร้อมเก็บ disagreement เดิม การเปลี่ยนกติกาต้องระบุว่ากระทบ annotation รุ่นใดและต้องทบทวนอะไร
- สร้าง reference ตามคู่มือและกระบวนการทบทวนที่ระบุ หากใช้เครื่องมือช่วยในอนาคตต้องบันทึกวิธีและการตรวจโดยคน ไม่ถือ prediction เป็นคำตอบอ้างอิงที่ผ่าน QA โดยอัตโนมัติ

ใช้ [annotation guideline template](templates/annotation_guideline.template.md), [QA template](templates/quality_review.template.md) และ [decision log](docs/DECISION_LOG_TH.md) เป็นจุดเริ่ม ยังไม่กำหนดผู้ตรวจจริงหรือ threshold ผ่าน/ไม่ผ่าน

## เอกสารและเครื่องมือใน repository

| ตำแหน่ง | หน้าที่และจุดเริ่มอ่าน |
| --- | --- |
| [docs/FOUNDATION_INDEX_TH.md](docs/FOUNDATION_INDEX_TH.md) | ลำดับอ่านข้อกำหนด หลักฐาน สมมติฐาน และเคส |
| [docs/DATA_DICTIONARY_TH.md](docs/DATA_DICTIONARY_TH.md) | ความหมาย metadata fields และข้อจำกัด record/person binding |
| [docs/DECISION_LOG_TH.md](docs/DECISION_LOG_TH.md) | ผู้ตัดสิน เหตุผล และผลกระทบของการเปลี่ยนแปลง |
| [scripts/](scripts/) | metadata/ZIP directory audit, document provenance และ path validation |
| [tests/](tests/) | ข้อมูลสังเคราะห์สำหรับ split archive, XLSX, เวลา และการแยก source/work/repository |
| [templates/](templates/) | แบบฟอร์ม source version, class/attribute rationale, annotation/QA และ release manifest ที่ยังไม่มีข้อมูลจริง |
| [reports/README.md](reports/README.md) | ระดับหลักฐานและวิธีตีความรายงานภายในตามลำดับเวลา |
| [config/audit.example.json](config/audit.example.json) | config ตัวอย่าง; paths จริงอยู่ใน local config ที่ไม่ commit |
| [docs/SCOPE_AND_OWNERSHIP_TH.md](docs/SCOPE_AND_OWNERSHIP_TH.md) | ขอบเขตพื้นที่งาน วิธีตั้งค่าเครื่อง เปิด VS Code และคำสั่งใช้งาน |
| [docs/FILE_REGISTER_TH.md](docs/FILE_REGISTER_TH.md) | หน้าที่รายไฟล์ การย้าย และการสำรอง/กู้คืน |

### ตรวจเครื่องมือที่มีอยู่

ใช้ Python 3.10+ และ standard library จาก repository root การทดสอบนี้สร้างข้อมูลสังเคราะห์เองและไม่ต้องเข้าถึงภาพบริษัท:

```bash
python3 -B -m unittest discover -s tests -v
```

หลังตั้ง local config ตาม [วิธีใช้งาน](docs/SCOPE_AND_OWNERSHIP_TH.md) จึงตรวจ path โดยไม่อ่านเนื้อหาแพ็กเกจ และบันทึก provenance ของเอกสารได้:

```bash
python3 -B scripts/audit_package.py --check-config
python3 -B scripts/prepare_handoff.py
```

`audit_package.py` แบบไม่ใส่ `--check-config` ใช้ตรวจ metadata exports กับ ZIP directory และ hash ไฟล์แพ็กเกจ เขียน run ใหม่ใต้ external `work_root/runs/` โดยไม่ decode ภาพ ยังไม่มี annotation runner, QA adjudication system หรือ release builder อัตโนมัติ

## การเชื่อมรุ่นข้อมูล คู่มือ annotation และ code

แนวทางที่เสนอต้องทำให้ release หนึ่งชี้กลับไปยัง input และการตัดสินที่ใช้สร้างได้ โดยไม่ทำให้ code commit กลายเป็น dataset release โดยปริยาย

| สิ่งที่เชื่อม | มีแล้ว | สิ่งที่ยังต้องทำก่อน release จริง |
| --- | --- | --- |
| ที่มาและรุ่นข้อมูล | [source version template](templates/source_version.example.json) | ระบุ population, snapshot/provenance และความต่างจากรุ่นก่อน |
| คำตอบอ้างอิงและการแก้ไข | ช่อง `annotation_revision` และ `annotation_manifest_ref` ใน release template | กำหนด revision จริง เก็บไฟล์/hash และประวัติ review ของ revision นั้น |
| นิยามและกติกา | ช่อง `ontology_version`, `guideline_version`, `qa_policy_version` และ [decision log](docs/DECISION_LOG_TH.md) | กำหนดรุ่นที่อนุมัติและผลกระทบเมื่อเปลี่ยนคลาส/กติกา |
| Code ที่สร้าง artifact | `script_sha256` ในผล audit; ช่อง `code_commit`/`code_repository` ใน release template | บันทึก commit SHA ที่ใช้จริง พร้อม config และ inputs ของการสร้างรุ่น |
| ชุดประเมินที่ออกรุ่น | [release manifest template](templates/release_manifest.example.json) มี references, membership hash และ `supersedes` | สร้างและตรวจ manifest จริง เชื่อมรุ่นทั้งหมด รวมสิทธิ์/ขอบเขตการเข้าถึงก่อนอนุมัติ |

ช่องใน template ยังเป็น `null` ไม่ใช่เลขรุ่นที่ใช้งานแล้ว สคริปต์ปัจจุบันไม่ได้สร้าง release manifest หรือเติม annotation revision/code commit ให้อัตโนมัติ ต้องกำหนดขั้นตอนตรวจความสอดคล้องและนโยบาย revision ก่อนออกรุ่น รายละเอียด membership และ annotation manifests จริงเก็บภายนอก Git

## สิ่งที่เผยแพร่และข้อมูลที่เก็บภายนอก

Repository public นี้เผยแพร่โค้ด เครื่องมือ แบบฟอร์มที่ว่าง และเอกสารวิธีวิจัยที่ตรวจแล้ว ภาพ CCTV/preview, metadata/notes จริง, annotation จริง, รายชื่อไซต์/กล้อง/บุคคล, local config, generated runs และรายงานภายในอยู่ภายนอก repository ตาม [ขอบเขตพื้นที่งาน](docs/SCOPE_AND_OWNERSHIP_TH.md)

การเปิด repository ไม่ได้ประกาศสิทธิ์เผยแพร่ภาพหรือ dataset ในรอบนี้ยังไม่เพิ่ม license หรือกำหนดสิทธิ์ dataset การอ้าง source/private evidence ใช้เพื่อ provenance ภายใน ไม่เป็นลิงก์ดาวน์โหลดข้อมูลบริษัท

## ข้อจำกัดและขั้นตอนถัดไป

ยังไม่ยืนยัน taxonomy ที่เหมาะกับภาพจริงทั้งชุด ความสอดคล้องระหว่างผู้ทำ annotation ค่า coverage/unknown ที่ยอมรับได้ หรือคุณภาพ reference annotations การดูภาพแบบจำกัดในประวัติไม่ตอบคำถามเหล่านี้ทั้งหมด และยังไม่มีผลประเมินโมเดลบน dataset รุ่นที่พร้อมใช้

ต้องรักษา raw curation statuses และ notes ตามต้นฉบับ `pending` ใน export ปัจจุบันไม่ลบล้าง selected/rejected/flagged เดิม ส่วน event `category` ไม่ผูกบทบาทให้ทุกคนในภาพโดยอัตโนมัติ

ขั้นต่อไปคือปิดคำถามด้าน population/สิทธิ์/ที่มา ตรวจ coverage และกรณีกำกวมตามขอบเขตที่อนุญาต แล้วเตรียมคู่มือกับผู้ทำ pilot ก่อนเริ่ม annotation จริง รอบปรับเอกสารนี้ไม่เริ่ม annotation, inference, training หรือ benchmark และไม่แก้ภาพ/metadata/ผลทดลองเดิม

## แหล่งอ้างอิงที่ใช้ตั้งโจทย์

- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010): เสนอการบันทึกแรงจูงใจ องค์ประกอบ วิธีรวบรวม และการใช้ dataset ใช้เป็นแนวคิดจัดเอกสาร ไม่ใช่การรับรองคุณภาพ annotation
- [Instance-level Human Parsing via Part Grouping Network](https://arxiv.org/abs/1808.00157): อธิบาย semantic parts และการจัดส่วนให้เป็นคนละ person instance ใช้ช่วยอธิบายหน่วยงาน ไม่ได้บังคับคลาสหรือ pipeline ของโครงการนี้

คำอธิบายหน้าโครงการตรวจจากบทคัดย่อ และรอบตรวจฐานงานอ่านหัวข้อที่เกี่ยวข้องใน PDF ต้นฉบับ CIHP, MHP v2, Cityscapes, Datasheets และ CCIHP เพิ่มเมื่อ 22 ตุลาคม 2026 ดู source/version/section/page และขอบเขตการประยุกต์ใน [ทะเบียนหลักฐาน](docs/EVIDENCE_AND_HYPOTHESES_TH.md) การทดสอบ H-01–H-06 และกติกา QA เป็นข้อเสนอของโครงการที่ยังต้องพิสูจน์กับข้อมูลและผู้ทำจริง
