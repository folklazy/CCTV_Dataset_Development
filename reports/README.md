> **12 พฤศจิกายน 2026 — B4_TRAINING / SOLIDER_PENDING / SAM31_PENDING** หยุด SAM3.1 รอบเก่าตามผู้ใช้ เก็บ best epoch9 และผล B4 เดิมครบ เปิด detached batchตามลำดับ B4 → SOLIDER → SAM3.1 ยืนยัน B4ผ่านtraining20/157batchesแล้ว CPU10 tests/3 preflightsผ่าน อ่าน [สถานะ, วิธีติดตาม และ recipe](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#helper-training-revision2)

> **เป้าหมายhelperล่าสุด12พฤศจิกายน2026** เลือกตัวช่วยที่ทำให้แก้GTน้อยลงจากร่างจริง ใช้วิธีที่เหมาะกับแต่ละโมเดลและเลือกตามส่วนได้ Metricsเป็นข้อมูลประกอบ Fine-tuningทำเมื่อช่วยลดข้อผิดพลาดที่เสียเวลา อ่าน [คำชี้แจงและกติกาที่ปรับ](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#helper-purpose-correction) คำแนะนำbenchmark-styleก่อนหน้าด้านล่างเป็นประวัติ

> **12 พฤศจิกายน2026 — ผลตรวจเงื่อนไขretrain** B4checkpointเดิมนำไปประเมินต่อได้ CPUloss/VOID/globalconfusionchecksผ่านบนกรณีที่เกี่ยวข้อง ส่วนSAM3.1sourceปัจจุบันควรแก้objectiveและvalidationก่อนfreshtrainingattempt อ่าน [รายละเอียดและกรณีall-VOIDของB4](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#helper-retrain-decision) สถานะก่อนหน้าด้านล่างเป็นประวัติ

> **12 พฤศจิกายน2026 — REVIEW_COMPLETE / TRAINING_ACTIVE / METRIC_REVISION_REQUIRED**
> ผู้ใช้รับรองSeed300แล้ว ตรวจ313train/77valcropsจาก213/56ภาพ roles/timegroupsถูกต้อง savedmasks390ตรงannotationปัจจุบัน SegFormer25epochsจบ SAM3.1กำลังtrainบนT4 อ่าน [สถานะจริงและประเด็นก่อนเลือกhelper](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#training-review-20261112) source-at-launch/cache/loss/metric/launcherมีงานที่ต้องปิดตามรายงาน สถานะก่อนหน้าด้านล่างเป็นประวัติ

> **10 พฤศจิกายน2026 — ยืนยันภาระGTตามscopeเดิม** ผู้ตรวจแก้bbox/personID/4partsและสีเมื่อประเมินได้ Person maskเป็นhelperที่เก็บอัตโนมัติ ค่าoutside-personเป็นwarning การรับGTไม่เพิ่มงานเกลาขอบคนทั้งตัว อ่าน [รายละเอียด](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#person-mask-workload) สถานะก่อนหน้าด้านล่างเป็นประวัติ

> **ข้อ4.1 Auto-Triageผ่านการreviewข้อกำหนด — 10 พฤศจิกายน2026**
> TRIAGE_SPEC_REVIEW_1_PROPOSED / IMPLEMENTATION_PENDING อ่าน [สิ่งที่ปรับและหลักฐานcode](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#auto-triage-review) ใช้คนยืนยันsmall candidatesก่อนGTignore แยกperson/part scoresและrawdiagnostics ทุกภาพมีhumanreceipt คิว/size gating/part-edit roundtripยังรอimplementation Membershipรุ่นbalancedที่ตรวจแล้วใช้ตามเดิม สถานะก่อนหน้าด้านล่างเป็นประวัติ

> **10 พฤศจิกายน 2026 — BALANCED_MEMBERSHIP_VERIFIED / GT_AND_EVENT_REVIEW_PENDING**
> ปรับรายชื่อครบ2,200IDs Test440จาก106กลุ่มเวลา/46กล้อง มี19.23–20.14%ต่อSiteที่แบ่งได้ จัดtrain240/val60/Boost550/reserve910ครบพร้อมpilot24ในtrain อ่าน [ผลรายSiteและข้อจำกัด](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#balanced-split-complete) ขั้นถัดไปevent-context/coverage/schema/ignore/toolroundtripและGTacceptance สถานะก่อนหน้าด้านล่างเป็นประวัติ

> **ตรวจละเอียด10พฤศจิกายน2026 — REBALANCE_REQUIRED_BEFORE_FINAL_TEST_FREEZE**
> พบtest440จาก27กลุ่มเวลากระจุกบางสถานที่ (สัดส่วนtestรายสถานที่4.08–71.69%) อ่าน [ข้อค้นพบและโครงสร้างtrain240/val60/Boost550](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#split-detail-review) รายชื่อเดิมเก็บเป็นparentcandidate ขั้นถัดไปปรับallocationตามสถานที่/เวลาแล้วตรวจgroupisolationและcoverageใหม่ ข้อความก่อนหน้าด้านล่างเป็นประวัติ

> **10 พฤศจิกายน 2026 — SPLIT_MATERIALIZED / EVENT_REVIEW_PENDING**
> Development1,760ภาพ และheldoutcandidate440ภาพครบ2,200IDs; seed300รวมpilot24อยู่ในdevelopmentแล้ว ตรวจmembership/sourcebinding/parentpilotผ่าน อ่าน [ผลแบ่งและข้อจำกัด](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#time-block-split) รอบนี้ใช้metadataและCPU ขั้นถัดไปตรวจevent-context/coverage/toolroundtripก่อนpilot สถานะก่อนหน้าด้านล่างเป็นประวัติ

> **สถานะล่าสุด 8 พฤศจิกายน 2026: PLAN_ACCEPTED / EXECUTION_NOT_FROZEN — revision2.2**
> ผู้ใช้รับรองข้อปรับและกฎเริ่มต้นในแผนแล้ว อ่าน [ขอบเขตที่รับรองกับสิ่งที่ยังต้องตรวจจริง](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#plan-accepted) ไม่ถามscopeเดิมซ้ำ; คง2,200ภาพ/คน≥50px/pilot24ในseedเป้าหมาย300 ไม่เพิ่มงานเอง ขั้นถัดไปปิดschema/ignore/toolroundtripและgroupingเพื่อpilot; ไม่มีinference/training/downloadเพิ่ม สถานะก่อนหน้าด้านล่างเป็นประวัติตามวันที่

> **ขอบเขตล่าสุด 8 พฤศจิกายน 2026: PRIMARY_PERSON_50PX_ACCEPTED / REVISION_2_1_NOT_FROZEN**
> งานหลักเฉพาะคนที่ด้านยาว visible GT bbox ≥50px ในพิกเซลต้นฉบับ; คน<50pxไม่ทำ4parts/สี/GTmaskทั้งตัว เก็บข้อมูลยกเว้นขั้นต่ำ ไม่เพิ่มงานไล่ขอบละเอียด อ่าน [ขอบเขต/สิ่งที่ไม่ทำ/จุดหยุด](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md#bounded-scope-50px) คงpool2,200/pilot24ภายในseed300 และscopeเดิม; schema/ignore/scorer readinessยังpending ไม่มีmodel callsหรือtrainingเพิ่ม ข้อความถัดไปเก็บประวัติตามวันที่

> **อัปเดตแผน 8 พฤศจิกายน 2026: REVISION_2_REVIEWABLE_NOT_FROZEN**
> ปรับแผนหลักprivateไฟล์เดิมพร้อมbackupแล้ว อ่าน [ตารางสิ่งที่เปลี่ยนและเหตุผล](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md) คงGTbbox+4parts, primary≥50pxพร้อมเก็บคนเล็ก, plannedhelperFT, separatedetectorstudy และsame-cameraheld-out-events. รอบนี้ตรวจเอกสารเท่านั้น ไม่เปิดinference/training/downloadหรือแก้benchmarkเก่า ข้อความถัดไปเป็นประวัติตามวันที่

> **Master plan review — 6 พฤศจิกายน 2026: REVIEW_COMPLETE / FOUR_SCOPE_DECISIONS_ACCEPTED / NOT_EXECUTION_READY**
> [รายงานตรวจแผนหลัก](PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md): ยืนยัน helper fine-tuning หลัง seed, primary person longside≥50pxพร้อมเก็บคนเล็ก, detector benchmark4familiesเป็นงานแยก และ same-camera held-out events/timeblocks. ยังมี MUST_FIX เรื่อง bias/IDs/model bindings/ignore/geometry/สีและsplitmembership ต้นฉบับ privateยังไม่แก้ ไม่เริ่ม training/inference/download หรือbenchmarkใหม่

> **ข้อตกลงล่าสุด 6 พฤศจิกายน 2026: GT_SCOPE_ACCEPTED / PILOT_NOT_STARTED**
> GT ที่บังคับคือ **bbox คน + person ID + masks 4 คลาส/validity** ไม่บังคับ GT mask คนทั้งตัว ดู [ข้อกำหนดที่รับรองแล้ว](../docs/ANNOTATION_GUIDELINE_V0_2_TH.md#accepted-gt-scope) คง baseline pipeline ใช้ RGB crops และ predicted YOLO masks จัดเจ้าของ; evaluation ใหม่ต้องใช้ bbox-based matching ตามนิยามที่ยังต้อง freeze ไม่เปลี่ยน scorer/ผลเก่า การรับรอง scope ไม่ใช่ GT acceptance หรือ GPU readiness งานนี้ปรับเอกสาร/queue metadata ไม่มี model calls เพิ่ม

> **สถานะล่าสุด 6 พฤศจิกายน 2026: เตรียม script pseudo-label person + 4 parts แล้ว; CPU checks ผ่าน14กรณี; GPU inference0ครั้ง**
> [คู่มือหลักและเหตุผลเลือก helper/ขนาดขั้นต่ำ](../docs/ANNOTATION_GUIDELINE_V0_2_TH.md#person-part-pseudolabel) · candidate queue24จาก2,200เตรียมแล้ว แยก6calibration/6human-first/12workflow แต่ยังไม่รับรองvisualcoverageหรือGT Precheckจริงผ่านimports/input/checkpointbindings; ยังไม่ได้โหลดSAM3บนGPU/วัดความแม่น4parts ต้องcalibrationจริงก่อนpilot; งานSapiensเดิมไม่ถูกแก้ ไม่มีGUIใหม่ ข้อความถัดไปเป็นประวัติตามวันที่

> **สถานะล่าสุด: ทบทวนหลักฐานและคู่มือ 0.2-R1-PROPOSED — 5 พฤศจิกายน 2026**
> ใช้ผู้ทำตอบ 4 เรื่อง พร้อมกฎ Face/cross-zone, validity และ QA ที่ตรวจได้ อ่าน [คู่มือปัจจุบัน](../docs/ANNOTATION_GUIDELINE_V0_2_TH.md) และ [แหล่งอ้างอิง/การดัดแปลง](../docs/EVIDENCE_AND_HYPOTHESES_TH.md#targeted-review-20261105) งานรอบนี้เป็นเอกสาร ไม่ได้เริ่ม pilot/model inference หรือยืนยัน coverage ครบชุด ยังต้องปิด lossless export/desktop roundtrip และทดลองกฎกับ pilot24 ไม่ทำเว็บเพิ่ม ข้อความถัดไปเป็นประวัติตามวันที่

# สถานะฐานงานและหลักฐาน — 22 ตุลาคม 2026

รอบนี้ตรวจฐานงานและเตรียมแผนสำรวจ ไม่สร้าง specification ฉบับสุดท้าย เอกสารเดิมทุกส่วนยังแก้ไขได้ การมี REQ, template หรือข้อความใน README ไม่ใช่การยืนยันรายละเอียดวิจัยโดยผู้ใช้

## ขอบเขตการตรวจและแหล่งหลักฐาน

อ่าน Git/config/code/docs ปัจจุบัน รายงานตั้ง workspace รายงาน package audit และ bounded visual review เดิม ตรวจ schema/ชื่อไฟล์/เวลาใน CSV ปัจจุบันและ hash ของ metadata exports พร้อม stat ต้นทางก่อน–หลัง ไม่เปิดภาพ ไม่เลือกตัวอย่างจริง ไม่ทำ annotation หรือรันโมเดล

| รหัส | หลักฐานที่ตรวจ / ตำแหน่งภายใน | ขอบเขตและข้อจำกัด |
| --- | --- | --- |
| F01 | Git checkout, [AGENTS](../AGENTS.md), [README](../README.md), scripts/config/templates ปัจจุบัน | repo อิสระ; ตรวจ branch/remote และเทียบ remote ก่อนแก้; paths จริงอยู่ใน ignored local config |
| F02 | `WORKSPACE_SETUP_REPORT_TH.md` ใต้ external work_root และ migration provenance | พบไฟล์จริง; ใช้สำรอง/path map/checksums เดิม ไม่ใช่ผล QA ของ dataset |
| F03 | `CCTV_RETURN_TO_CHAT_TH.md`, `FILE_REGISTER_TH.md` และ package run ใน private legacy archive | อ่าน report และ machine-readable audit/inventory/linkage/format comparison ที่อ้างถึง; เป็น snapshot ประวัติ |
| F04 | metadata ปัจจุบัน + source stat + F03 | hash ของ CSV/JSON/XLSX ตรง audit เดิม; อ่าน CSV ใหม่เพื่อตรวจ fields/status/time และเทียบ filename กับ linkage/inventory เดิม; ไม่ตรวจเนื้อหา JSON/XLSX ซ้ำเพราะ bytes ตรง |
| F05 | bounded visual report, sample manifest และ validation receipt ใน private legacy archive | hash ของ manifest ตรง receipt และ hash metadata ใน manifest ตรง CSV ปัจจุบัน; ไม่เปิด preview หรือตรวจข้อสังเกตภาพซ้ำ |
| F06 | พื้นที่ annotation/release ภายนอกตาม local config | ตรวจแบบจำกัดไม่พบไฟล์จริงในสองพื้นที่นี้; ไม่ใช่คำยืนยันว่าทุกที่ไม่มี annotation |
| F07 | [แหล่งต้นฉบับห้างาน](../docs/EVIDENCE_AND_HYPOTHESES_TH.md) | ตรวจ PDF เฉพาะหัวข้อที่เกี่ยวข้อง; ไม่ตรวจ release assets/label IDs หรืออ้างมาตรฐานบังคับ |

หลักฐาน F04 และ paths/hash/สถิติ/รายการค้นหาที่ละเอียดอ่อนอยู่ใน `work_root/provenance/` ของรอบ foundation review ผู้ใช้เข้าถึงตำแหน่งจริงจากรายงานภายในได้ ไม่มี raw evidence หรือสำเนา metadata ใน Git

## สถานะแยกตามระดับหลักฐาน

| ประเด็น | ระดับสถานะ | ผลตรวจและสิ่งที่ยังกล่าวอ้างไม่ได้ |
| --- | --- | --- |
| ที่มาของ bytes ที่กำลังใช้งาน | **ตรวจยืนยันจากไฟล์จริงแล้ว** — F01/F04 | local config ชี้แพ็กเกจที่มีอยู่จริง; metadata bytes ตรง snapshot audit เดิมและ stat ของไฟล์แพ็กเกจตรง setup; ยังไม่ใช่ dataset release version ที่อนุมัติ |
| ภาพ ↔ metadata ↔ manifest | **ตรวจยืนยันจากไฟล์จริงแล้ว เฉพาะ metadata/หลักฐาน** — F03/F04 | filename ใน CSV ไม่ซ้ำและตรง linkage/inventory เดิม; checksum metadata และ byte/stat ของไฟล์หลักฐานตรวจได้วันนี้ แต่ไม่ได้อ่าน ZIP directory/payload ใหม่ |
| ความครบถ้วน archive และเทียบสาม export | **มีรายงานเดิมแต่ยังยืนยันกับข้อมูลปัจจุบันไม่ได้ทั้งหมด** — F03/F04 | ใช้ผล directory/join/format comparison เดิมเพราะ metadata hash ตรงและ archive stat ไม่เปลี่ยน; ไม่ rehash archive ขนาดใหญ่ ไม่ตรวจ CRC/decode ทั้งชุด; stat ไม่ใช่หลักฐานว่า archive bytes ตรงแน่นอน |
| สถานะ export ปัจจุบัน | **ตรวจยืนยันจากไฟล์จริงแล้ว** — F04 | raw status เป็น pending และ note ใน export ว่าง; ไม่ได้พิสูจน์ว่าผู้ใช้ยังไม่เคยคัดหรือไม่มี notes เดิม |
| selected/rejected/flagged เดิม | **มีรายงานเดิมแต่ยังยืนยันกับข้อมูลปัจจุบันไม่ได้** — F03 | พบยอดตามรายงานเดิม แต่ยังไม่พบ original curation export/notes ที่ใช้ join รายภาพ; ห้ามนำ pending มาทับผลเดิมหรือรวมยอดต่าง snapshot |
| ข้อมูลกล้อง/เวลา/เหตุการณ์ | **ตรวจยืนยันจากไฟล์จริงแล้ว เฉพาะ schema** — F04 | มี site, camera_name, incident_timestamp พร้อม explicit offset; ไม่มี event/track/person ID หรือ sequence field; category เป็นค่าระดับ record ยังไม่มี person binding |
| ความหมาย category และเวลาในระบบต้นทาง | **ยังไม่มีข้อมูลเพียงพอ** — F03/F04 | ต้องมี source dictionary/event export ยืนยันว่า label ผูกเหตุการณ์หรือคนใด และเวลาเป็น capture/event/export time อย่างไร; ไม่เดาจากชื่อไฟล์หรือ mtime |
| ประวัติดูภาพและคุณภาพ annotation | **มีรายงานเดิมแต่ยังยืนยันกับภาพปัจจุบันไม่ได้** — F05/F06 | รายงานเก่ามี assistant review ตัวอย่างแบบจำกัด ไม่มี independent human review; รอบนี้ยืนยันเพียงไฟล์หลักฐาน ไม่ใช่ visual findings/coverage/agreement ใหม่ |
| สถานะงานตามเอกสาร | **พบหลักฐานขัดแย้งในคำอธิบาย** — F01/F03/F05 | phase ใน config/กฎ setup เก่า และถ้อยคำเตรียม pilot ใน README เดิมไม่ตรงขอบเขตรอบนี้; แก้เอกสารให้เป็น audit/แผนร่าง เก็บ phase config เดิมพร้อมข้อจำกัด; รายงาน “ยังไม่ดูภาพ” เก่ากับ visual report ที่ใหม่กว่าคือคนละเวลา ไม่ใช่หลักฐานลบล้างกัน |
| การตีความ label ระดับเหตุการณ์ | **พบข้ออ้างเกินหลักฐาน** — F03/F04 | เอกสาร inherited เรียก Category_EN ว่าระดับเหตุการณ์ แต่ export ปัจจุบันมี category และยังไม่มีนิยามระบบยืนยัน; แก้ทะเบียนหลักฐานให้แยกคำบอกเล่าจากสิ่งตรวจได้ ไม่สรุปเป็น label ของทุกคน |
| ขอบเขต task/คลาส/สี/QA/split | **ข้อเสนอที่ยังไม่ตัดสินใจ** | ดู [ตารางขอบเขตและ DEC](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md); ผู้ใช้ยืนยันงานพัฒนา dataset และข้อห้ามรอบนี้ ไม่ได้อนุมัติรายละเอียดทั้งหมด |
| source-system revision/สิทธิ์/final release | **ยังไม่มีข้อมูล** | ยังขาด provenance ต้นทางที่ผูก curation snapshot กับแพ็กเกจ และหลักฐานขอบเขตสิทธิ์ใช้งานจริง; template ที่ว่างไม่แทนข้อมูลเหล่านี้ |

ยังไม่พบหลักฐานว่าประชากรและเวอร์ชันเดียวกันมีผลคัดเลือกขัดกันจริง ความต่างของ pending กับรายงานคัดเก่าจึงเป็นช่องว่างในการเชื่อมประวัติ ไม่ใช่เหตุให้เปลี่ยนสถานะ

## สิ่งที่พร้อมทำต่อและสิ่งที่ต้องรู้ก่อน

มีฐานสำหรับสำรวจ metadata ต่อแบบ read-only และเสนอ coverage/edge-case design แล้ว แต่ยังไม่พร้อมตรึงชุดประเมินหรือเริ่ม annotation ใช้ [แผนสำรวจร่าง](../docs/AUDIT_PROTOCOL_DRAFT_TH.md) และ [DEC/คำถามถึงผู้ใช้](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md) เป็นจุดเริ่ม ไม่ต้องรัน full-package hash/decode ซ้ำเพียงเพื่อปรับเอกสาร

## คงประวัติและแยกข้อมูลสาธารณะ

รายงานตั้ง workspace อยู่ที่ work_root ตาม local config รายงานส่งกลับและทะเบียนไฟล์เดิมอยู่ใน `work_root/legacy/cctv_dataset/` ฉบับ public ปัจจุบันคือ [ทะเบียนไฟล์](../docs/FILE_REGISTER_TH.md) รายงาน foundation review ภายในบันทึก paths จริง วิธีตรวจ checksums และข้อจำกัด โดยไม่แก้รายงานประวัติย้อนหลัง

ภาพ/preview, metadata/notes, รายชื่อไซต์/กล้อง/บุคคล, per-image manifests และหลักฐานบริษัทอยู่ภายนอก Git เอกสารสาธารณะเผยแพร่เฉพาะวิธีการ/ทางเลือกและสถานะที่จำเป็น การตรวจไฟล์และ synthetic tests ไม่พิสูจน์ annotation ถูกต้อง

## ภาคเพิ่มหลัง eafe703 — เตรียม exploration ตาม requirements ล่าสุด

ส่วนรายงาน foundation ด้านบนคงข้อความเดิมตามเวลาที่ตรวจ ไม่แก้ OPEN ในรอบก่อนให้ดูเหมือนได้รับคำตอบแล้ว ข้อกำหนดใหม่/การเปลี่ยนสถานะดู [requirements](../docs/BENCHMARK_REQUIREMENTS_DRAFT_TH.md) และ PLAN-002/003 ใน [decision log](../docs/DECISION_LOG_TH.md)

- USER CONFIRMED: End-to-End หลัก, Oracle แยก; person/upper/lower/footwear masks + ownership; สีบน–ล่างเมื่อภาพเอื้อ; structured output/คำบรรยาย Attributes เพิ่มไม่ mandatory; จำนวน/กำหนดส่ง/กำลังคน/เวลา OPEN วิธี taxonomy/annotation/metrics/QA ยัง PROPOSED
- เชื่อม records ใน manifest 12 ภาพเดิมกับ CSV ปัจจุบันได้ และตรวจ hash ของ manifest/report/metadata กับ receipt และ inventory เดิม โดยไม่เปิดภาพหรืออ่าน archive payload ใหม่ ประวัติ assistant exposure ไม่ใช่ independent human review หรือ curation result
- เตรียม [แผน 24+8](../docs/AUDIT_PROTOCOL_DRAFT_TH.md) พร้อม proposed manifest ภายใน: coverage เดิม 12 + ใหม่ 12, discovery ใหม่ 8 รวม distinct filenames 32; unique image content ยังไม่ทราบ ใหม่หมายถึงไม่ปรากฏใน exposure log ที่ตรวจ ไม่ใช่รับรองว่าไม่เคยมีใครดู
- discovery อ้างอิงเพียงบริบทของรายงานเคสเดิมและ raw grouping/record time; ยังไม่รู้ว่า candidate มีเคสนั้นจริง บางรายการห่างกันหลายนาที กลุ่มที่ยังไม่ครอบคลุมบันทึกใน private coverage matrix ไม่อ้างเป็นตัวแทนทางสถิติ
- เตรียม [แบบบันทึก](../docs/CASE_REGISTER_DRAFT_TH.md) ที่แยก observed/inference/human-review และเวลา exploration/recording จาก annotation; ทุก observation ใหม่ยังไม่เริ่ม ผู้สำรวจ/ผู้ทบทวนยังไม่ระบุ ไม่มี independent review ใหม่
- ตรวจแล้ว config phase เป็น descriptive metadata ไม่ใช่ permission gate เปลี่ยน local phase ให้ตรงงานโดยคง read-only/image/model flags และไม่เพิ่มความสามารถ annotation/inference; ค้น curation/dictionary เพิ่มเฉพาะ repo/legacy/พื้นที่ source ที่เกี่ยวข้อง ยังไม่พบต้นฉบับที่ปิดช่องว่างได้ ไม่ค้นทั้งเครื่องซ้ำ

รายงาน/manifest/reproduction receipt และ paths จริงอยู่ใน fresh external work_root/runs ของรอบ exploration preparation ส่วนรายงาน foundation ภายในเดิมไม่แก้ ไม่มีการเปิดภาพ คัด final annotation หรือ model run ในรอบนี้

## ภาคเพิ่ม 23 ตุลาคม 2026 — bounded visual exploration หลัง b8bb9ed

รายงานก่อนหน้าด้านบนคงตามเวลา ภายหลังผู้ใช้อนุญาตให้เปิดรายการเดิมครบ รวม historical reopens จึงดำเนิน visual exploration และเพิ่ม fresh run แยกจาก draft/รายงานเดิม

| สิ่งที่ตรวจ | ผล / หน่วยและขอบเขต |
| --- | --- |
| เปิดตาม manifest | 32/32 records สำเร็จ: 20 new filenames ต่อ log ที่ตรวจ และ 12 historical reopens; ไม่เปิดภาพนอก manifest |
| Payload integrity/decode | CRC/SHA256/strict full decode ผ่าน 32/32, อ่านไม่ได้ 0; เป็นการตรวจไฟล์ ไม่ใช่ annotation correctness |
| Exact duplicates | 32 filenames มี 31 unique encoded payloads หนึ่งคู่ bytes ตรงกัน; คงทั้งสอง records และ curation เดิม ไม่ถือชื่อใหม่เป็นเนื้อหาใหม่เสมอ |
| หลักฐานภาพ | มี observed/inference/needs-human-review และ locator ตามความแตกต่างรายคน; ผลรายภาพ/ภาพ/crops/แหล่งข้อมูลจริงอยู่ภายนอก Git |
| ขอบเขตผล | เห็น person/region/color support ได้บางกรณี แต่ยังไม่มี masks/GT/independent human review หรือผล End-to-End/Oracle |
| Discovery | มีทั้งเคสพบ/ไม่พบ และองค์ประกอบ uncertain; record ที่ duplicate ไม่เพิ่มหลักฐานภาพอิสระ ไม่ตีความเป็น success rate/prevalence |
| ประวัติและเวลา | exposure ใช้พัฒนา protocol; Final Test ยัง UNASSIGNED; เวลา active visual/annotation ที่ไม่วัดคง null และรายงาน timestamp gaps หลังหยุดข้าม turn |
| Source และระบบ | metadata/proposal hashes และ source stat ไม่เปลี่ยน หลังจบปิด inspect_images/visual phase; models/annotation/training/benchmark ปิดตลอด |

สิ่งที่ร่างเป็นข้อเสนอได้คือ visible-support/unknown, owner/accessory/outer-layer questions, crop provenance, color observability และการไม่เติมคำบรรยายเกินหลักฐาน ต้องให้มนุษย์ทบทวนก่อนใช้สร้าง GT ยังต้องสำรวจเพิ่มเติมภายหลังเรื่อง one-piece ที่เห็นเต็มตัว รองเท้า/เท้าเปล่าชัดเจน หลายสภาพแสง/known modality และ coverage ที่ไม่อยู่ใน sample รอบนี้ไม่เพิ่มสมาชิกและไม่ตรึง taxonomy จำนวนสี QA หรือขนาด final dataset

[Protocol](../docs/AUDIT_PROTOCOL_DRAFT_TH.md) และ [case form](../docs/CASE_REGISTER_DRAFT_TH.md) อธิบายวิธี ส่วน [guard](../scripts/workspace_paths.py)/[synthetic tests](../tests/test_visual_scope.py) ตรวจ permission boundaries รวม tests ปัจจุบัน 14 รายการผ่าน ไม่มีการติดตั้งแพ็กเกจหรือแก้ environment โมเดล การดูภาพใช้ Pillow ที่มีอยู่เดิมและไม่รันโมเดล

## ภาคเพิ่ม 23 ตุลาคม 2026 — คู่มือทดลองและชุดทบทวนหลัง c5139f4

ขยาย [คู่มือเดิมเป็น v0.1](../templates/annotation_guideline.template.md) พร้อม R01–R12 ที่มีคำถาม หลักฐานอ้างภายใน ทางเลือก ข้อเสนอ/เหตุผล ผลต่อ evaluation และสถานะ PROPOSED จัด [ตารางตัดสินใจก่อน pilot/แผน QA](../templates/quality_review.template.md) และ [schema ร่าง](../docs/DATA_DICTIONARY_TH.md) แล้ว ไม่ถือว่าอนุมัติกฎหรือเริ่ม annotation

ชุด static HTML ภายในมี 10 unique cached payloads พร้อม full frames/display crops/locators/ทางเลือกและ decision sheet ยัง PENDING_HUMAN_REVIEW ใช้เฉพาะข้อมูลใน 32 records เดิม ไม่เปิดภาพใหม่จาก ZIP ไม่วาด masks จริงและไม่มี blinded/independent human review ประวัติเปิดจริงแยกไว้ใน run ใหม่ ไม่แก้ observations/curation เดิม

Synthetic-only checks ตรวจ PNG dimensions/IDs/owner-state preservation/point inverse และแยก display palette จากสีเสื้อ ใช้ Pillow/JSON ที่มีอยู่ ชุด tests รวม 17 รายการผ่าน ไม่มีเครื่องมือ annotation GUI ที่ยืนยันใช้งานได้ใน scope ที่สำรวจ จึงยังไม่มี GUI/COCO/RLE roundtrip หรือ human annotation reliability ผลทดสอบนี้ไม่พิสูจน์ annotation quality

แผน pilot เสนอ 8 unique images แยก calibration/first pass ตามกฎที่ต้องทดสอบ จำนวนยังไม่อนุมัติ คน/ผู้ตรวจ/เวลา/กำหนดส่ง OPEN ไม่มี agreement threshold หรือ Final Dataset count/Final Test ที่กำหนดแล้ว One-piece ชัด รองเท้า/เท้าเปล่าหลายมุมและ known modality ยังเป็นช่องว่างเพื่อเสนอสำรวจเฉพาะจุดภายหลัง

ตรวจเนื้อหาต่อหลัง c6f28c4: ปรับทางเลือก A/B/C ของ R01–R12 เป็นวิธีเก็บข้อมูล/แบ่งขั้นงานที่ใช้ได้ภายใต้ constraints พร้อมผลกระทบของแต่ละทางเลือก ข้อเสนอหลักยังเดิมและ PROPOSED ไม่ให้วิธีที่ขัดข้อกำหนดกลายเป็นตัวเลือกอนุมัติ ชุดทบทวนภายในปรับข้อความตามกันและเก็บฉบับก่อนแก้ ไม่มีภาพใหม่หรือ annotation เพิ่ม


## Whole-export review และ Dataset Design v0.1 — 27 ตุลาคม 2026

คำสั่งใหม่จากผู้ใช้ขยาย read-only file/visual review จาก manifest เดิมไปยัง current export ทั้งชุด พร้อมขอข้อเสนอ class/schema และแผนคัดสองพันกว่าไม่เกินสามพันภาพ ขอบเขตนี้ไม่เปิด annotation/pilot/model/training/benchmark และไม่กำหนด Final Test รายงาน foundation/preparation/visual/guideline ข้างต้นคงเป็นหลักฐานตามเวลาของตน

CONFIRMED เฉพาะไฟล์: ตรวจ metadata exports/linkage และ CRC/decode/dimensions/byte-vs-pixel duplicates ทั้ง population ที่เข้าถึงได้ เก็บผลแยก strict failures กับ alternate-decoder diagnostics ไม่แก้ต้นฉบับหรือ curation statuses ข้ออ้างย้อนหลังบางส่วนยังไม่มีข้อมูลต้นทางรองรับ และพบว่าข้ออ้าง dimensions แบบเดียวทั้งชุดไม่ตรงกับไฟล์จริง

**Visual screening ยังไม่ครบ** มี actual display events, overview notes และ targeted native observations เพิ่มจากชุดเดิม พร้อมสถานะทุก record/duplicate alias และ checkpoint ภายใน การสร้าง sheets หรือมี coverage บางภาพทุก metadata group ไม่เท่ากับตรวจภาพทั้งหมด ไม่เผยแพร่ actual IDs, metadata, paths, ภาพ/crops หรือหลักฐานบริษัท

[Dataset Design v0.1](../docs/DATASET_DESIGN_V0_1_TH.md) ส่งมอบตาราง 6 core classes + auxiliary object, person/region/owner/validity/geometry contract, สีเป็น attribute และการเชื่อม structured output เสนอ cross-zone garment ที่ไม่สร้างเส้นแบ่งเอวสมมติ เก็บชิ้นสวมนอก core และ unknown ต่างจาก background ทุกข้อยัง PROPOSED พร้อม private native evidence binding ไม่ใช่ GT/ข้ออนุมัติผู้ใช้

แผน 2,400 unique image groups เป็น operating target ในกรอบผู้ใช้ ใช้ metadata coverage กับ visually confirmed diversity และ review ความใกล้ซ้ำ ไม่ใช่ Final Test หรือ membership ที่เลือกแล้ว [คำสั่ง resume](../docs/SCOPE_AND_OWNERSHIP_TH.md) ใช้ inventory เดิมต่อได้ ไม่ต้อง decode ทั้งชุดใหม่ สถานะจำนวนเปิดจริง/เหลือและเหตุผลการเลือก native cases อยู่ใน private report/pointer

Annotation agreement และ human annotation time ยัง NOT_MEASURED; source timestamp/modality/curation dictionary, production tool compatibility, กำลังคน/กำหนดส่ง/สิทธิ์ข้อมูลจริง OPEN การตรวจสังเคราะห์พิสูจน์พฤติกรรมเครื่องมือเฉพาะที่ทดสอบ ไม่พิสูจน์ annotation quality


## Intake ต่อจาก checkpoint — 4 พฤศจิกายน 2026

**ตรวจปิด work unit เวลา 2026-11-04T17:13:55.991614+07:00 (Asia/Bangkok): INTAKE_IN_PROGRESS / PILOT_MEMBERSHIP_NOT_SELECTED / ANNOTATION_NOT_STARTED** ไม่มี dataset-review worker อื่นใน process snapshot ตอนเริ่ม จึงต่อ ledger เดิม ไม่เปิด controller หรือ GPU job และไม่แตะงาน benchmark ที่อาจกำลังทำงานอยู่

| รายการ | ค่าจาก canonical review DB/checkpoint | ขอบเขตคำอ้าง |
| --- | --- | --- |
| Source metadata records | 9,328 | ไม่ใช่จำนวนภาพไม่ซ้ำหรือคน |
| Strict readable / unreadable | 9,322 / 6 | ใช้ file audit เดิม ไม่ retry ตัวเสียหรือ decode ทั้งชุดซ้ำ |
| Readable byte-unique / pixel-unique | 9,254 / 9,221 | คนละนิยาม ไม่รวม alternate-decoder diagnostics เป็น canonical |
| รวมเปิดดูจริงก่อนรอบนี้ | 1,048 pixel groups | รวมประวัติเดิมที่ reconciliation ผ่านแล้ว |
| เปิด overview เพิ่มรอบนี้ | 64 pixel groups | S0065–S0068 เปิดผ่าน viewer จริง มี notes ครบทุก record |
| รวมเปิดดูจริงล่าสุด | 1,112 pixel groups | ไม่เท่ากับตรวจขอบ mask ทุกภาพ |
| Native full-frame detail เพิ่ม / รวม detail | 4 / 58 pixel groups | สี่ภาพอยู่ใน overview ชุดนี้ ไม่บวกซ้ำเป็นภาพเปิดใหม่อีกสี่ภาพ |
| ยังไม่เปิดดู | 8,109 pixel groups | visual screening ทั้งชุดยังไม่จบ |
| Sheets generated / reviewed | 577 / 68 | generated ไม่ใช่ reviewed |
| ชุด candidate 2,400 / pilot24 / release300 | ยังไม่มี membership ที่ freeze | ไม่อ้างว่าเลือกหรือ annotate ครบจากจำนวนเป้าหมาย |

ตรวจ source scope ด้วย loader เดิม: private manifest SHA256, metadata CSV hash และ archive-piece size/mtime bindings ผ่าน; ตรวจ hash ของ 4 contact sheets และ 4 cached full frames ที่เปิดเทียบ ledger ผ่าน ไม่ full rehash ZIP ทั้งชุด source read-only ไม่มีการติดตั้ง/ดาวน์โหลด/เปลี่ยน environment

ข้อสังเกตจาก native full frames: ผมบังบางส่วนของใบหน้า, พืชและราวบังส่วนคน, คนขี่รถที่รายละเอียดพร่า และปื้นพร่าบนภาพ ต้องบันทึก visibility/uncertainty เป็นรายส่วน ไม่ถือว่า missing part เป็น background หรือวาดเติม การเห็นปื้นพร่าไม่ยืนยันสาเหตุทางกายภาพ ภาพตัวอย่างเหล่านี้ไม่ยืนยันสัดส่วนหรือความยากของทั้ง export และยังไม่เป็น GT

หลักฐาน private work unit: `pilot-preparation-intake-20261104T100937Z` มี DB backup ก่อนทำงาน, checkpoint before/after, session และ native review evidence; parent `dataset-design-full-review-20261027T022912320042Z` เก็บ canonical SQLite, display logs, observations และ checkpoint history ต่อเนื่อง ข้อมูลจริง/IDs/ภาพไม่ขึ้น Git รายงาน private เก่าที่เป็น snapshot ไม่ถูกเขียนทับให้ดูเป็นสถานะใหม่

อัปเดต [design ฉบับเดิม](../docs/DATASET_DESIGN_V0_1_TH.md#revision-งานปัจจุบัน--4-พฤศจิกายน-2026), requirements, dictionary, guideline และ QA ให้แยกเป้าหมาย 4 targets + clothing color ออกจากข้อเสนอ 6 คลาส/pilot8 เดิม กติกาละเอียดยัง PROPOSED_NOT_FROZEN ขนาด workflow24→300/ผู้ใช้ตรวจทุกภาพยืนยันตามบทสนทนา ไม่ใช่การรับรอง schema/annotation quality

**Next action:** ต่อ overview S0069 ตาม sheet order เดิม เก็บ coverage ของ small person/occlusion/blur/light/viewpoint และ targeted native observations แล้วจัด private candidate/pilot membership จากภาพที่ตรวจต้นฉบับจริง ก่อน annotation ต้องปิด label/unknown/color/export contract และตรวจเครื่องมือจริง ไม่เริ่ม SAM3/annotation ใน work unit นี้ ไม่มี background screening ที่จะเดินต่อเองหลังจบ turn


## Visual review รอบต่อ — 4 พฤศจิกายน 2026

**สถานะตรวจปิด work unit 2026-11-04T17:37:31.497141+07:00 (Asia/Bangkok): INTAKE_IN_PROGRESS / ANNOTATION_NOT_STARTED** ต่อจาก commit31668ac และ checkpoint เดิม; ไม่พบ dataset-review Python worker ใน process snapshot ก่อนเริ่ม ไม่เปิด GPU/controller/model/annotation และไม่เปลี่ยนข้อมูลต้นฉบับ

| รายการ | ผลตรวจจริง |
| --- | --- |
| Source records / readable / unreadable | 9,328 / 9,322 / 6 — reuse audit เดิมหลัง source guard ผ่าน |
| Pixel-unique groups | 9,221 |
| Overview ที่เปิดรอบนี้ | S0069–S0076 รวม128 records มี display events/notes ครบ |
| เพิ่มภาพที่ยังไม่เคยเปิดจริง | 126 groups; อีก2 groups เคยเปิดผ่าน prior/detail review แล้ว ไม่บวกซ้ำ |
| รวมเปิดดูจริง | 1,238 groups จาก1,112ก่อนรอบนี้ |
| Native full-frame detail | เพิ่ม6ภาพ รวม64 unique groups; อยู่ใน overview ชุดนี้ ไม่บวกเป็นภาพใหม่อีก6 |
| ยังไม่เปิดดู | 7,983 groups |
| Sheets generated / reviewed | 577 / 76 |
| Candidate2400 / pilot24 / release300 | ยังไม่มี membership ที่ freeze หรือ GT ใหม่ |
| จุดทำต่อ | S0077 ตาม order/seed เดิม; ไม่มี background screening ที่เดินเองหลัง turn |

ตรวจ private source-manifest hash/metadata CSV hash/archive-piece signatures ด้วย guard เดิม และ hashes ของ8contact sheets+6cached native full frames ที่เปิด ไม่ decode/full rehash source ทั้งชุดซ้ำ ตรวจ128 unique record IDs กับ notes, ภาพที่ซ้ำกับ review เดิม2groups, checkpoint arithmetic และ prefix ของ observations/notesเก่าไม่เปลี่ยน ผล PASS เป็นความสอดคล้องของ intake ไม่ใช่ annotation/execution acceptance

ผล native detail และข้อเสนอการจัดการอยู่ใน [ทะเบียนเคส N01–N06](../docs/CASE_REGISTER_DRAFT_TH.md#ข้อสังเกตภาพจริงรอบต่อ--4-พฤศจิกายน-2026): near-monochromeพร้อมoverlay, โครงเหล็กบังคน, reflection, blur/partial person, คนสัมผัสกัน และ uncertain presence ไม่ยืนยัน IR/สีแท้/ขอบส่วนซ่อนหรือ absence จากภาพไม่ชัด

Private work unit `visual-review-continuation-20261104T103212Z` เก็บ BEFORE.sqlite3, checkpoint before/after, SESSION, overview/native observations และ RECONCILIATION เชื่อม parent review run เดิม ไม่เผยแพร่ภาพ IDs บริษัท หรือ metadata บน public Git รายงานรอบก่อนด้านบนเป็น historical snapshot ตามเวลา

**Next action:** ต่อ S0077 พร้อม coverage/uncertainty notes; ภายหลังจัด shortlist pilot24จากภาพที่เปิดต้นฉบับครบและเหตุผลจาก coverage ไม่ใช่คะแนนโมเดล กติกาใหม่ยัง PROPOSED_NOT_FROZEN ไม่มี SAM3 calls, masks หรือการตรวจรับโดยผู้ใช้ในรอบนี้


## Review S0077-S0088

ตรวจปิด work unit **2026-11-04T17:47:07.140920+07:00 (Asia/Bangkok)** จาก HEAD681d455 และ checkpoint เดิม: **INTAKE_IN_PROGRESS / ANNOTATION_NOT_STARTED** ตารางรอบก่อนด้านบนคงเป็น historical snapshots ไม่ใช่จำนวนปัจจุบัน

| รายการ | ผลจริง |
| --- | --- |
| Source records / readable / unreadable | 9,328 / 9,322 / 6 ใช้ file audit เดิมหลัง source guard ผ่าน |
| Readable pixel-unique | 9,221 |
| Overview รอบนี้ | 192 records ใน S0077–S0088 เปิดจริงและมี notes ครบ |
| ใหม่ / เคยเปิดมาก่อน | 191 / 1 pixel groups; ไม่นับประวัติซ้ำ |
| รวมตรวจภาพจริง | 1,429 groups จาก1,238ก่อนรอบนี้ |
| Native detail รอบนี้ / รวม detail | 2 / 66 unique groups; สองภาพอยู่ใน overview ชุดนี้ ไม่บวกจำนวนซ้ำ |
| ยังไม่เปิดดู | 7,792 groups |
| Generated / reviewed sheets | 577 / 88 |
| จุดทำต่อ | S0089 ไม่มี background screening หลังจบ turn |
| Candidate2400 / pilot24 / release300 | membershipยังไม่freeze ไม่มี GT หรือ model calls ใหม่ |

ไม่พบ dataset-review worker ใน process snapshot ก่อนเริ่ม จึงต่อ ledger เดิม ตรวจ source-manifest SHA/metadata CSV hash/archive-piece signatures ผ่าน ใช้ cached images ที่ตรวจ hash ตรงกับ inventory: 12sheets+2native full frames ไม่ decode/full rehash source ทั้งชุด ตรวจ192unique IDs/notes, overlapกับประวัติ1group, arithmetic และ observations/notesเก่าไม่เปลี่ยน ผ่านทั้งหมด นี่เป็น intake consistency ไม่ใช่ execution/annotation acceptance

[เคส N07–N08](../docs/CASE_REGISTER_DRAFT_TH.md#native-detail-เพิ่มจาก-s0077-s0088) เพิ่ม coverage เรื่องมุมก้ม/หมวก/พืชบังและปื้นสว่างทับศีรษะ แยกคนที่เห็นจริงจากความสามารถอ่านทุก target ไม่บังคับ unknown เป็น absent หรือ BG ไม่ยืนยันสาเหตุปื้นหรือความเท่ากันของ boundary จากภาพตัวอย่าง

Private work unit `visual-review-continuation-20261104T104316Z` เก็บ BEFORE.sqlite3, checkpoint before/after, SESSION, overview/native notes, RECONCILIATION และ publication receipt เชื่อม parent run เดิม ภาพ/IDs/metadataไม่ขึ้น Git ไม่มี inference/annotation/training/ติดตั้งหรือดาวน์โหลด และไม่แตะ benchmark ที่กำลังรันอยู่

**Next action:** ต่อ S0089 ตาม order/seed เดิมและเก็บ coverage ที่ตรวจจริง เมื่อเตรียม pilot ต้องเปิดต้นฉบับครบตามสมาชิกที่เสนอและบันทึกเหตุผล ไม่ใช้ชุดตัวอย่างรอบนี้แทน membership24หรือ sample ที่เป็นตัวแทนประชากรทั้งหมด


## Review S0089-S0104

ตรวจปิดwork unit **2026-11-04T19:09:20.636353+07:00 (Asia/Bangkok)**: INTAKE_IN_PROGRESS / ANNOTATION_NOT_STARTED ผู้ใช้ชี้แจงให้Codexตรวจเร็วขึ้น จึงคงขอบเขตเดิมและปรับเป็น16sheetsพร้อมบันทึกสั้นรายภาพ ไม่เปลี่ยนไปทำpilotแทนส่วนที่ยังไม่ตรวจ

| รายการ | ผลจริง |
| --- | --- |
| เปิดoverviewรอบนี้ / ใหม่ / เคยเปิดแล้ว | 256 records / 254 / 2 pixel groups |
| รวมเปิดดูจริง / uniqueทั้งชุด / คงเหลือ | 1,683 / 9,221 / 7,538 groups |
| Native detailเพิ่ม / รวมdetail | 1 / 67 groups; ภาพnativeอยู่ในoverviewจึงไม่บวกซ้ำ |
| Generated / reviewed sheets | 577 / 104 |
| จุดทำต่อ | S0105; ไม่มี background screening หลังจบturn |

ไม่พบdataset-review workerก่อนเริ่ม Source manifest/metadata CSV hash/archive signaturesผ่าน ใช้auditเดิม ตรวจhash16sheets+1native frame, 256IDs/notesครบ, overlapกับประวัติ2groups, old observations/notesไม่เปลี่ยน และarithmeticผ่าน เป็นintake consistency ไม่ใช่annotation acceptance

Private work unit `visual-review-fast-batch-20261104T120354Z` เก็บSESSION/BEFORE.sqlite3/checkpoint before-after/compact codesพร้อมlegend/display events/RECONCILIATION ระดับfine boundariesและสีที่ไม่ได้ตรวจต้นฉบับยังNOT_ASSESSED; uncertainไม่ใช่confirmed negative ภาพnativeหนึ่งเคสยังไม่ยืนยันว่าเสื้อผ้าเป็นชิ้นเดียวหรือแยกชิ้น จึงไม่ใช้สีต่อเนื่องเป็นหลักฐานcross-zone

ไม่มีinference/annotation/ติดตั้ง/ดาวน์โหลดหรือแก้raw data/benchmark เก็บcandidate2400/pilot24/release300เป็นเป้าหมายที่ยังไม่มีmembershipfreeze รหัสบันทึกสั้นไม่ใช่GT; สรุป/commitครั้งเดียวต่อwork unit ไม่อ้างspeedupหรือETAที่ไม่ได้วัดแบบควบคุม


## Data selection handoff

จัดเตรียมส่งต่อ **2026-11-04T21:31:24.943016+07:00 (Asia/Bangkok)** ตามคำขอผู้ใช้ให้อีกแชทรับงานคัดเลือกข้อมูล รอบนี้ไม่เปิดภาพเพิ่ม/ไม่ inference และไม่เปิดcontroller ส่วนการคัดกรองทั้งชุดยังไม่เสร็จ: ตรวจแล้ว1,683จาก9,221pixel groups เหลือ7,538 จุดเดิมS0105

ผลส่งมอบหลักเป็น private `DATA_SELECTION_HANDOFF_TH.md` ในwork unit `dataset-selection-handoff-20261104T143007Z` ซึ่งresolveจาก`work_root/runs`ในignored local config มีpathsจริงของrepo/source/metadata/cache/DB/checkpoint, นิยาม8metadata fields, วิธีอ่านDBแบบread-only, ข้อจำกัดduplicates/event/time, coverageและวิธีคัดร่างcandidate2400, ความต่างจากpilot24/release300, outputsและข้อห้ามครบ ไฟล์นี้ไม่เผยแพร่publicเพราะมีinternal paths ผู้ใช้ส่งเอกสารให้อีกแชทเอง ไม่มีการส่งข้อความหรือสร้างtaskอื่นอัตโนมัติ

ตรวจsource guard/checkpoint binding, existenceของเอกสาร/metadataที่อ้าง, syntaxของPythonตัวอย่าง และquerystrict readable pixel representativesได้9,221 ตรงcanonical ผลเป็นdocument/intake consistency ไม่ใช่selection membership/annotation/execution acceptance

สถานะ HANDOFF_PREPARED / SELECTION_NOT_FROZEN / ANNOTATION_NOT_STARTED ข้อเสนอจากsqrt(camera count)/seedหรือการเริ่มcandidateก่อนvisualทั้งชุดจบต้องเปิดเผยวิธีและส่วนยังไม่ตรวจ ไม่ยกระดับเป็นaccepted/unseen testโดยไม่มีหลักฐาน แชทรับงานต้องตรวจHEAD/treeและrecordsล่าสุดก่อนทำ หลีกเลี่ยงเขียนsharedledgerพร้อมกัน เก็บสมาชิก/ภาพ/metadataจริงprivate และบันทึกงานใหม่แยกจากhistorical runs


### Selection-only clarification

ผู้ใช้ชี้แจง 2026-11-04T21:37:46.781766+07:00 (Asia/Bangkok): อีกแชทคัดเลือกภาพเท่านั้น ส่งcandidateประมาณ2,400พร้อมmanifest/metadata/reasons/duplicateและcoverage แล้วหยุด ไม่ทำpilot24/release300/annotation/pseudo-label/inference/training/split/GTschemaหรือพัฒนาระบบannotation การเปิดดูภาพและสคริปต์ที่ไม่รันโมเดลใช้เท่าที่จำเป็นต่อselection; ไม่อ้างvisual reviewครบสำหรับภาพที่ไม่ได้เปิดดู

ไฟล์privateฉบับปรับขอบเขต `DATA_SELECTION_ONLY_HANDOFF_TH.md` ในwork unit `selection-only-handoff-20261104T143746Z` แทนscopeของhandoffเดิม เก็บต้นฉบับและhashprovenanceครบ ไม่มีภาพ/โมเดลหรือการคัดเลือกจริงเพิ่มจากรอบนี้


## Selected 2200 intake — 5 พฤศจิกายน 2026

ตรวจ 2026-11-05T01:15:34.066091+07:00: ผู้ใช้เปลี่ยนcandidate targetเป็น2,200และอัปโหลดชุดคัด รับ2,200files/CSV/JSONครบ, hashes+metadataตรงsourceเดิม, strictอ่านผ่าน2,198ไม่ผ่าน2 ไม่ลบหรือแทนผลเดิม สถานะ NEEDS_CORRECTION / ANNOTATION_NOT_STARTED อ่าน [รายงานตรวจรับฉบับหลัก](SELECTED_2200_INTAKE_REVIEW_TH.md) สำหรับหลักฐาน การแก้สองภาพ และข้อจำกัดvisual/dHash/pixelhash claims Private run `selected-2200-intake-20261104T180758Z` เก็บไฟล์ตรวจและรายการแก้ไขจริง ไม่เปิดinference/annotation/pilot และไม่ตรวจsourceทั้งชุดซ้ำ


## Selected 2200 revision2 reconciliation

ตรวจ 2026-11-05T11:33:29.201123+07:00: active2,200ผ่านfile checks,archive3แยกจากactive; reuse2197SHAเดิม+decode3เปลี่ยน สร้างderived manifestแก้MD5/pixelhash/Thai remarks5fieldsโดยเก็บincomingเดิมครบ อ่าน [รายงานหลักฉบับอัปเดต](SELECTED_2200_INTAKE_REVIEW_TH.md#revision2-intake) สถานะFILE_INTEGRITY_VERIFIED / VISUAL_COVERAGE_PENDING ไม่ใช่GTready พบcoverage snapshotเก่ายังอ้างภาพoverlayที่ถูกแทนหนึ่งรายการ จัดprivatehandoffให้rebindตามhashโดยไม่แก้config/DBของงานนั้น ไม่มีinference/annotationเพิ่ม


## Assisted coverage

ตรวจปิด work unit เมื่อ 2026-11-05T16:35:47.104221+07:00 (Asia/Bangkok) ผู้ใช้เลือกใช้สคริปต์วัดสถิติและจัดคิว แล้วตรวจ coverage รายละเอียดพร้อมตรวจ annotation โดย Codex ช่วยเคสยาก แทนการเปิดทุกภาพแล้วเขียนรายละเอียดล่วงหน้าซ้ำ เริ่มอ่าน [คู่มือใช้งานและขอบเขต](../docs/ASSISTED_COVERAGE_WORKFLOW_TH.md)

| ส่วนงาน | ผลที่ตรวจจริง |
| --- | --- |
| Intake/source version | ใช้ derived manifest ของ revision2 และ ledger ที่ pin hashes แล้ว ไม่เปลี่ยนสมาชิก/ภาพ/metadata ต้นฉบับ |
| CPU measurements | 2,200/2,200; missing0, failure0; 67site-camera groups; อ่าน SHA256 พร้อมรอบวัดสถิติ ไม่รัน audit ต้นทางซ้ำ |
| Semantic coverage ของเครื่องมือใหม่ | operator records0; targets ยังไม่ประเมิน; ไม่ยกยอดงานเก่าเป็นการเปิดดูรอบนี้ |
| GT / model calls | accepted GT0; model inference0; ไม่ใช้ GPU ไม่เริ่ม pilot/SAM3 |
| Checks | 7 targeted fixture tests ผ่าน; JS syntax ผ่าน; synthetic browser โหลด/กรอก14ช่อง/บันทึก/refresh ผ่าน ไม่มี JS errors; actual-source browser โหลด/zoom/refresh ผ่านและ data API ปฏิเสธ request ที่ไม่มี token |
| กระบวนการ | วัดด้วย CPU process เดียวแล้วเปิด loopback viewer ใน tmux; artifacts/private token อยู่ภายนอก Git; process logs/launch receipt ใน private run |
| UI revision | พบและแก้การคง token เมื่อ refresh ก่อนส่งมอบ สร้าง child run ที่ reuse2200 measurements ตาม source/measurement bindings เดิม ไม่วัดซ้ำ ไม่แก้ config/DB รุ่น parent; มี explicit reuse receipt |
| ข้อจำกัด | สถิติไม่ยืนยันเบลอ/คนเล็ก/บดบัง/targets/กรอบฝังทั้งหมด; server headless ไม่มี Thai fonts จึงมี glyph ขาดใน screenshot แต่ Unicode/controls ตรวจผ่าน; browser ผู้ใช้ต้องมี Thai font |

สถานะ **MEASUREMENTS_COMPLETE_HUMAN_REVIEW_PENDING** ไม่ใช่ annotation-ready/GT-ready และไม่ใช่การรับรองว่าชุดสะอาดทั้งหมด หน้าเว็บเก็บ coverage แยกจาก X-AnyLabeling ยังไม่ได้รับรอง bridge/import annotation ระดับ lossless

Private run ปัจจุบัน `assisted-coverage-20261105T093306Z` เก็บ CONFIG, REUSE_COMPATIBILITY_PRIVATE, STATUS, MEASUREMENT_SUMMARY_PRIVATE, SQLite, browser receipts และ private handoff Parent `assisted-coverage-20261105T092753Z` คง measurements/logs เดิม ภาพจริงและรายชื่อไม่เผยแพร่บน Git

**Next action:** ผู้ใช้เปิดหน้าตรวจได้แล้ว → ตรวจเคสจำเป็นต่อกฎและปิด bridge readiness → pilot24 เมื่อขอบเขตขั้นนั้นพร้อม → ยืนยัน coverage พร้อมตรวจ annotation เป็น batches ก่อนรับรองรุ่น ไม่ต้องให้ Codex เปิดทุกรูปล่วงหน้า การเลือก High/Extra High เป็นการตั้งค่าของ client ซึ่งงานนี้ไม่ได้เปลี่ยนให้


## Local web sync

อัปเดต 2026-11-05T17:07:37.546025+07:00 (Asia/Bangkok): ผู้ใช้ต้องการเปิดผ่านเว็บโดยข้อมูลยังอยู่localและซิงค์กัน ใช้browserผ่านSSHเข้าบริการloopbackบนserver ไม่มีcloudหรือฐานข้อมูลสำเนาบนแต่ละเครื่อง อ่าน [คู่มือ](../docs/ASSISTED_COVERAGE_WORKFLOW_TH.md#ใช้ผ่านเว็บและซิงค์ข้อมูลในระบบ-local)

- **IMPLEMENTED:** incremental syncทุก5วินาทีจากSQLiteชุดเดียว; optimistic concurrencyด้วยbase_revisionและwrite transaction; stale saveตอบ409และไม่ทับร่าง; offline/connected status; เตือนก่อนทิ้งร่างที่ยังไม่บันทึก
- **VERIFIED:** targeted CPU tests9กรณีผ่าน; two-browser synthetic sync, dirty draft preservation,409,explicit reconciliation,refresh,viewerrestart,disconnect/reconnectผ่าน ไม่มีJS exception; หลักฐานสังเคราะห์อยู่privateไม่เพิ่มsemantic reviewของชุดจริง
- **REUSED:** measurements2,200/2,200,failure0 จากparentตามintakeและsourcebindingsเดิม; ASTของmeasure/analyze/source_pathเหมือนเดิม ไม่อ่านประมวลผลทั้งชุดใหม่ ไม่ใช้GPU/model; review/attempt historyเก็บครบ
- **CURRENT:** เว็บเปิดในtmux `cctv-coverage-assisted` port8041; privatepointerชี้run `assisted-coverage-web-sync-20261105T100528Z` parent `assisted-coverage-20261105T093306Z` คงไว้; operator reviews0,acceptedGT0
- **LIMITS:** กดบันทึกจึงส่งเข้าserver ไม่ใช่autosave/offlinequeue; clientต้องเชื่อมserverจึงอ่านภาพ/บันทึก; ไม่ซิงค์polygonกับX-AnyLabeling; tokenเปลี่ยนเมื่อเปิดviewerprocessใหม่ ต้องใช้URLส่วนตัวล่าสุด

Checkpointในหัวข้อAssisted coverageข้างบนเป็นประวัติ เครื่องมือใหม่นี้ไม่รับรองว่าดู/annotateครบทั้งชุด **Next:** เปิดURLผ่านtunnelและตรวจได้จากหลายหน้าต่างบนฐานเดียว ปิดกติกาและbridge readinessก่อนpilotตามworkflowเดิม


## Annotation scale and practical pilot — 2026-11-05T17:49:05.455322+07:00

ผู้ใช้ขอให้ครอบคลุมระยะ/คนเล็ก ใช้pseudo-labelsที่แยกจากผู้เข้าสอบได้ และกติกาสั้นใช้งานจริงได้ ปรับ [คู่มือหลัก](../docs/ANNOTATION_GUIDELINE_V0_2_TH.md) เป็น6ข้อ+ตารางcoverage โดยเก็บรายละเอียดเดิมเป็นภาคผนวก

ตรวจพบ: datasetยังไม่มีขนาดคน/targetsที่รับรองครบชุด; ภาพเล็กไม่ใช่หลักฐานระยะเมตร. เสนอSAM3ที่มีอยู่เป็นdraft helper ไม่รับรองarchitecture/training independenceหรือautoGT. Localadapterยังlargest-contourและglobalBF16/fallback ต้องปิดก่อนpilot. Pilot24ต้องได้masks/owners/validity/colors/revisionsที่ใช้ต่อได้ใน2,200/300 พร้อมdevelopment exposure

IMPLEMENTED: annotation_scale.py คำนวณvisible bboxสองแกน,mask area,normalized extentsจากbinarymask โดยdistance=nullเมื่อไม่calibrate. Tests4กรณีผ่าน: disjoint,holes,empty,invalidgeometry/labels; ไม่ใช่ผลannotationจริง. ไม่มีnewinference/weights/downloadหรือเว็บเพิ่ม. Next:ปิดกติกาขอบFaceที่ค้างและlosslessbridgeก่อนสร้างpilot; ไม่แอบใช้polygonlossyเป็นGT
