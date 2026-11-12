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
| PLAN-002 / 2026-10-22 หลัง eafe703 | ผู้ใช้ / USER CONFIRMED เป้าหมาย; Codex / IMPLEMENTED การเตรียม | Research Objectives & Constraints ล่าสุดเปลี่ยน DEC-02/08 จาก OPEN เป็น End-to-End หลัก, Oracle แยก, person/upper/lower/footwear masks + ownership, สีบน–ล่างเมื่อภาพเอื้อ, structured output/คำบรรยาย; attributes อื่นไม่ mandatory | ไม่แก้ให้ดูเหมือนตอบแล้วใน PLAN-001: รายงาน foundation เดิมคงตามเวลา; taxonomy/annotation/metrics/QA เป็น PROPOSED และจำนวน/กำหนดส่ง/กำลังคน/เวลา OPEN |
| PLAN-003 / 2026-10-22 หลัง PLAN-002 | ผู้ใช้ / อนุญาต proposed manifest; Codex / IMPLEMENTED ภายในเท่านั้น | เตรียม 24+8 ด้วย seed/ลำดับและ hash inputs เชื่อมประวัติเปิดดูเดิม แยก exposure จาก curation; เปลี่ยน phase ของ ignored local config ให้ตรงงานหลังตรวจว่า phase ไม่ใช่ permission gate | ไม่มีการเปิดภาพ/annotation/model หรือ Final Test; manifest/form/coverage matrix/builder อยู่ภายนอก Git การเลือกเป็นข้อเสนอแก้ได้ ไม่ใช่คัด final; flags readonly/inspect_images/run_models คงเดิม |
| VIS-001 / 2026-10-22–23 หลัง b8bb9ed | ผู้ใช้ / AUTHORIZED เฉพาะ 32 records; Codex / COMPLETED visual exploration | ใช้ proposal เดิม ตรวจ snapshot/member แล้วอ่านเฉพาะ payload ที่อนุญาต ดูเต็มก่อน crop; review แบบบันทึกหลัง 8 รายการก่อนทำต่อครบ บันทึก fresh observations ก่อน explicit legacy comparison | ผลสำรวจ/ภาพ/locator/exposure อยู่ภายนอก Git ไม่เป็น GT/independent human review; ผล duplicate คงทุก record ไม่เปลี่ยน curation; final_test_membership=false หมายถึงยังไม่จัด Final Test ไม่ใช่ split ที่ตรึงแล้ว |
| VIS-002 / 2026-10-23 | Codex / IMPLEMENTED guard และปิด scope หลังจบ | เพิ่ม dedicated bounded-visual loader ที่ตรวจ phase/flags/private manifest path+hash/count/IDs และ metadata snapshot; metadata loader ยังปฏิเสธ image-enabled config ภายหลังปิด inspect_images และ visual phase | ไม่มี annotation/model/training/benchmark capability เพิ่ม; synthetic checks รวม 14 tests ผ่าน ไม่ใช้ decode/checksum เป็น annotation QA; เวลา active visual/แรงงานมนุษย์ที่ไม่วัดคง null ไม่เติมย้อนหลัง |
| GUI-001 / 2026-10-23 หลัง c5139f4 | ผู้ใช้ / AUTHORIZED preparation; Codex / IMPLEMENTED drafts | ขยาย template เดิมเป็นคู่มือ v0.1 R01–R12, decision priorities, schema และแผน pilot; สร้าง static review packet ภายในจาก cached subset ของ 32 เดิม โดยไม่ซ้ำ encoded payload | ทุกกฎ/เครื่องมือ/schema/pilot size ยัง PROPOSED ไม่มี annotation จริงหรือการอนุมัติด้วยการเขียนคู่มือ; human review NOT_PERFORMED รายงานเดิมไม่เขียนทับ |
| GUI-002 / 2026-10-23 | Codex / CHECKED เฉพาะสิ่งที่มี | สำรวจ tools แบบจำกัด ไม่พบ annotation GUI ใน paths/environments ที่ตรวจ ทดสอบ synthetic PNG/JSON/reference/state/geometry ด้วย Pillow เดิม; ไม่ติดตั้ง/ย้ายข้อมูลไประบบใหม่ | ไม่อ้าง GUI import/export compatibility หรือ annotation quality; unknown/ignore ไม่กลายเป็น background และ display palette แยกจากสีเสื้อใน fixture; คน/เวลา/กำหนดส่ง OPEN Final Test UNASSIGNED |
| GUI-003 / 2026-10-23 หลัง c6f28c4 | Codex / PROPOSED clarification | ปรับทางเลือก R01–R12 ให้เป็น representation/workflow ที่ทำได้ภายใต้ constraints พร้อมภาระและผลต่อ validity/export แทนตัวอย่างวิธีที่ขัดข้อกำหนด | ข้อเสนอหลัก/requirements คงเดิม ทุกกฎรอมนุษย์; ไม่เสนอการเดาส่วนซ่อน/owner หรือรวม unknown เป็น background เป็นตัวเลือก pilot; private packet เก็บ revision เดิมและไม่เพิ่มภาพ |
| DES-001 / 2026-10-27 หลัง e79773a | ผู้ใช้ / USER CONFIRMED scope | อนุญาตตรวจไฟล์/ภาพทั้ง current export เป็น batches/checkpoints แทน limit 32 เดิม และขอ Dataset Design v0.1 กับแผนสองพันกว่าไม่เกินสามพัน | เพิ่ม whole-export hash-pinned guard โดยคง legacy guard; source read-only และปิด annotation/pilot/model/training/benchmark ไม่กำหนด Final Test |
| DES-002 / 2026-10-27 | Codex / PROPOSED design; CHECKED files | เสนอ 6 core parsing classes และ auxiliary object scope แยก person mask/owner/validity/attributes จากหลักฐาน native/overview ที่ตรวจจริง พร้อม IDs binding ภายใน | ตรวจไฟล์ครบไม่ใช่ดูภาพครบ; masks/schemaยังไม่อนุมัติ ไม่มี annotation agreement/เวลาทำmaskที่วัดแล้ว ความหมายtimestamp/curationเดิมยังOPEN ไม่ใช้CCIHPเป็นtaxonomyบังคับ |
| DES-003 / 2026-10-27 | Codex / PROPOSED; supersedes earlier recommendations only | Design v0.1 เสนอ composite head, exposed skin, upper/lower/cross-zone/footwear กับ auxiliary associated objects; socks/gloves outside core vocabulary เมื่อทราบชนิด และ C05 ที่ขาด anatomical boundary คง upper/lower projection unresolved | ทางเลือกในคู่มือ R01–R12 เดิมคงเป็นประวัติ/ทางเลือก ไม่ถือว่าอนุมัติแล้ว ข้อเสนอใหม่เปลี่ยนคำแนะนำบางส่วนโดยไม่เปลี่ยน requirements ไม่มี universal waist cut/size cutoff/color palette และไม่มี class reassignment จริง |

รายการใหม่ต้องมีวัน ผู้ตัดสิน สถานะ หลักฐาน/locator เหตุผล ทางเลือก และผลกระทบต่อรุ่นคู่มือ/ข้อมูล/คะแนน ถ้า supersede ให้ระบุรายการเดิมและเก็บประวัติ ไม่เปลี่ยน OPEN เป็น ACCEPTED โดยไม่มีการตัดสินจริง


## Intake / workflow update — 2026-11-04T17:13:55.991614+07:00 (Asia/Bangkok)

| Work/decision ID | การกระทำ/เหตุผล | Inputs / outputs / verification | Blockers และ next action |
| --- | --- | --- | --- |
| INTAKE-20261104-01 / COMPLETED_WORK_UNIT | ต่อจาก HEAD71f9f21 ด้วย source read-only และ audit เดิมที่ bindings ตรง เปิด S0065–S0068 แล้วตรวจ native4 เพื่อแยก visibility/blur/occlusion จาก absent | Existing scope + DB/checkpoint; private work unit `pilot-preparation-intake-20261104T100937Z`; ตรวจ local source guard, hashes8 display artifacts, notes64, native4, counts/membership และ docs links; รวม overview1,112/detail58 เหลือ8,109 ไม่ใช้ generated577 sheets เป็น reviewed | Whole-export visual review ยังไม่ครบ; ต่อ S0069 ไม่มี model/annotation job |
| WF-20261104-01 / USER_CONFIRMED_WORKFLOW | บันทึกเป้าหมาย4 targets+clothing color, X-AnyLabeling, ผู้ใช้ตรวจทุกภาพ, pilot24→300 รวม pilot, หกภาพผู้ใช้ทำก่อนเห็น AI draft ตามคำตอบผู้ใช้ในบทสนทนา | Reuse design/guideline/QA เดิม; six-class proposal และ pilot8 คงเป็นประวัติ | Candidate2400/actual pilot membership ยังไม่ freeze; ข้อเสนอแบ่ง24dev+276eval ยังไม่ใช่ split ที่รับรอง |
| RULE-20261104-01 / PROPOSED_NOT_FROZEN | เสนอ auxiliary Neck/Cross-zone/Person-other, observed-color-only และ GT-only validity แทนการบังคับแบ่ง dress/คอหรือเดาขอบที่ซ่อน | Design current revision; attached guideline เป็น reference ที่ยังต้องแก้ ไม่มีการยกระดับจากชื่อคลาสหรือภาพ4ตัวอย่างเป็น equivalence | ตรวจ schema/GUI roundtrip และ pilot ภายหลังเมื่อกฎพร้อม; ไม่มี hard pixel/IoU/color threshold ที่รับรองในรอบนี้ |

เวลาที่วัดจากคนจริง/active annotation time ยัง null ไม่มี GT masks, agreement, model calls หรือ dataset release ใหม่ Git history เก็บ commit identity ไม่เติม hash ของ commit ตัวเองลงรายการนี้


## Work log — 2026-11-04T17:37:31.497141+07:00 (Asia/Bangkok)

| Work/decision ID | การกระทำและเหตุผล | Inputs / outputs / verification | Blockers และ next action |
| --- | --- | --- | --- |
| INTAKE-20261104-02 / COMPLETED_WORK_UNIT | ต่อ frozen sheet order S0069–S0076 หลังตรวจ actual HEAD/process/source guard ไม่ใช้จำนวนจากข้อความเก่า | Parent checkpoint/DB + commit31668ac; private `visual-review-continuation-20261104T103212Z`; overview128, ใหม่126และซ้ำกับ prior2, native6; hashes14display artifacts, membership, old-prefix immutability และ arithmeticผ่าน | เหลือ7,983pixel groups; ต่อS0077; candidate/pilot membershipยังไม่freeze ไม่มี background worker |
| CASE-20261104-02 / OBSERVED + PROPOSED_POLICY | เพิ่มN01–N06จากภาพต้นฉบับเพื่อแยก presence/semantic/color validity และ reflection/overlay | Reuse case register/design/QAเดิม; private locators/hashesเชื่อมเคส ไม่เผยแพร่ภาพหรือ IDs | ยังไม่มี masks/GUI export/ผู้ใช้ตรวจรับ; เสนอ fixed GT-derived scene/task validity ยังไม่ถือเป็น accepted labeling rule |

ไม่รัน inference/annotation/training/benchmark ไม่ติดตั้งหรือดาวน์โหลด ไม่เปลี่ยน environment/โมเดลของงานอื่น; เวลา annotation โดยคนและ model calls ของงานนี้ยังไม่ได้วัด/ไม่มีตามลำดับ การอัปเดตเอกสารไม่รับรอง GT หรือกำหนด Final Test Git history เก็บ commit identity


## Work log — 2026-11-04T17:47:07.140920+07:00 (Asia/Bangkok)

| Work/decision ID | การกระทำและเหตุผล | Inputs / outputs / verification | Blockers และ next action |
| --- | --- | --- | --- |
| INTAKE-20261104-03 / COMPLETED_WORK_UNIT | ตรวจ HEAD/tree/process/source scope แล้วต่อ S0077–S0088 ตาม frozen sheet order ไม่เปิด worker ซ้ำ | HEAD681d455 + parent review DB; private `visual-review-continuation-20261104T104316Z`; overview192 เพิ่ม191และซ้ำประวัติ1, native2; source guard, hashes14, membership/notes, old-prefix และ arithmeticผ่าน | รวม1,429/detail66 เหลือ7,792; ต่อS0089 ไม่มี background worker; candidate/pilotยังไม่freeze |
| CASE-20261104-03 / OBSERVED + PROPOSED_POLICY | เพิ่มN07–N08จากต้นฉบับ: มุมก้ม/หมวก/พืชบัง และปื้นสว่างทับศีรษะ เพื่อแยก presence จาก target observability | Reuse case/design/reportเดิม; privatehashes/locators ไม่เผยแพร่ข้อมูลจริง; ยังไม่มี masks/ผู้ใช้ตรวจรับ | policyยัง PROPOSED_NOT_FROZEN ต้องตรวจ tool/annotation contract ก่อน pilot ไม่เติมส่วนซ่อนหรือเดาสาเหตุปื้น |

ไม่มี inference/annotation/training/benchmark หรือการติดตั้ง/ดาวน์โหลด ไม่แก้ raw metadata/source curation และไม่จัด Final Test เวลาทำ annotation โดยคนยังไม่ได้วัด Git history เก็บ commit identity


## Work log — 2026-11-04T19:09:20.636353+07:00 (Asia/Bangkok)

| Work/decision ID | การกระทำและเหตุผล | Inputs / outputs / verification | Blockers / next action |
| --- | --- | --- | --- |
| SPEED-20261104-01 / USER_CLARIFIED + IMPLEMENTED_WORKFLOW | ผู้ใช้ต้องการให้Codexตรวจเร็วขึ้น คงwhole-export scope; ใช้16sheets/batch, compact notesรายภาพ และnativeเฉพาะเคสจำเป็น ลดการอธิบาย/แก้เอกสารซ้ำ | ไม่เปลี่ยนmodel/GT/ระดับหลักฐาน; codes+legend private; ไม่เปิดsubagents/SAM3 | ไม่มีการรับรองspeedupจากmodelหรือETA; ทำต่อS0105ด้วยวิธีนี้ |
| INTAKE-20261104-04 / COMPLETED_WORK_UNIT | ตรวจS0089–S0104จริงครบ256records มีใหม่254และซ้ำประวัติ2; native1ไม่เพิ่มภาพซ้ำ | HEAD38db43a + existing guard/DB; private `visual-review-fast-batch-20261104T120354Z`; hashes17, notes/membership, prior-prefix, arithmeticผ่าน; รวม1,683/detail67 เหลือ7,538 | Whole-exportยังไม่จบ ไม่มีbackground worker; source/annotation/inferenceเดิมไม่เปลี่ยน |


## Work log — 2026-11-04T21:31:24.943016+07:00 (Asia/Bangkok)

| Work/decision ID | การกระทำและเหตุผล | Inputs / outputs / verification | Next action |
| --- | --- | --- | --- |
| HANDOFF-20261104-01 / USER_REQUESTED + PREPARED | ผู้ใช้จะให้อีกแชทคัดเลือกdata จัดรายละเอียดส่งต่อแทนตรวจภาพเพิ่ม ไม่สร้างtaskหรือส่งข้อความแทนผู้ใช้ | HEAD3e80425 + current checkpoint/sourceguard/docs/DB; private `dataset-selection-handoff-20261104T143007Z/DATA_SELECTION_HANDOFF_TH.md`; ตรวจpaths/metadata fields/query9221/Python example/checkpointhashตรง ไม่มีภาพหรือinferenceเพิ่ม | ผู้ใช้ส่งไฟล์privateให้อีกแชท; แชทรับงานตรวจactualHEADและเลือกfresh selection run รักษาสถานะunreviewed/unknownและscope |

ยอดreviewคง1,683/detail67 เหลือ7,538; candidate2400/pilot24/release300ยังไม่freeze ไม่มีbackground screening. Internal pathsและmembershipไม่ขึ้นpublicGit; Git historyเก็บcommit identity


| HANDOFF-20261104-02 / USER_CLARIFIED | 2026-11-04T21:37:46.781766+07:00 (Asia/Bangkok): แชทรับงานทำselection only; ตัดpilot shortlistออกจากdeliverables ไม่มีannotation/inference/splitหรือGTschema/release work | private `selection-only-handoff-20261104T143746Z/DATA_SELECTION_ONLY_HANDOFF_TH.md` พร้อมparent hashes; เก็บhandoffเดิม ไม่เปลี่ยนreview counts | ผู้ใช้ส่งฉบับselection-onlyให้อีกแชท คัดเสร็จส่งmanifest/reasons/coverageแล้วหยุด |


## Work log — 2026-11-05T01:15:34.066091+07:00 (Asia/Bangkok)

| Work/decision ID | การกระทำและเหตุผล | Inputs / outputs / verification | Blockers / next action |
| --- | --- | --- | --- |
| TARGET-20261105-01 / USER_CONFIRMED | เปลี่ยนcandidate target2,400→2,200ตามผู้ใช้ ไม่เปลี่ยนGT/split/annotation protocol | Uploadedselectiononly package; เก็บรายงาน/manifestเดิมและsourcebindings | ยังไม่freezeหรือเริ่มpilot |
| INTAKE-20261105-01 / COMPLETED_CHECK_NEEDS_CORRECTION | ตรวจactualfiles2200,manifestCSV/JSON,hashes/metadata/sourcejoin/strictdecode; ใช้auditsourceเดิมหลังguardผ่าน | private `selected-2200-intake-20261104T180758Z`; uniqueIDs/filenames2200,missing/orphan0; allMD5+sourceSHA2200ตรง; strict2198pass/2failเดิม; canonicalpixels2198ไม่ซ้ำ; spotcheck3แยกจากwhole-exportledger | ขอreplacement2+manifestrevisionและselectionmethod/dHash/visualclaimclarification; ยังไม่มีinference/annotation |

รายงานหลัก reports/SELECTED_2200_INTAKE_REVIEW_TH.md; rawattempt summaryเก็บเดิมและใช้reconciledsummaryที่แยกsourcejoinจากdecodeเป็นauthoritative ไม่ถือnot-checkedเป็นmismatch ไม่แก้incoming/rawsource/curation. Git historyเก็บcommitidentity


## Work log — 2026-11-05T11:33:29.201123+07:00 (Asia/Bangkok)

| Work ID | การกระทำ/เหตุผล | Inputs / outputs / verification | Next action |
| --- | --- | --- | --- |
| INTAKE-20261105-02 / FILE_VERIFIED_DERIVED_MANIFEST | รับrevision2ตามผู้ใช้ ตรวจdeltaไม่ทำdecodeทั้งชุดซ้ำ; active2200+archive3,sourceSHAตรง2200,uniqueactualpixels2200; reuse2197+decode3 | private `selected-2200-revision2-delta-20261105T043032Z`; derivedCSV/JSON+5field correctionsจากsourcebytes/rawmetadata+inputbindings; spotcheck3แยกจากGT | ใช้derived inputversion ตรวจcoverageต่อ; snapshotก่อนหน้าต้องrebindภาพที่เปลี่ยนหนึ่งรายการ ไม่แก้workingfiles/coverageDBของอีกงาน |

ต้นฉบับอัปโหลด/legacy audit/workingchangesของงานอื่นคงอยู่ ไม่มีinference/annotation/pilot สถานะfile checksไม่ใช่visual/GT acceptance; checksums/reviewclaimsที่แก้มีprovenance ไม่overwriteรายงานจากผู้ส่ง


## ASSISTED-COVERAGE-20261105 — USER_ACCEPTED / IMPLEMENTED / CPU_MEASURED

- เวลา 2026-11-05T16:35:47.104221+07:00 (Asia/Bangkok); ผู้ใช้รับแนวทาง scripts + human review during annotation + Codex exceptions และให้เริ่มทำ ไม่ใช่คำสั่ง inference/pilot
- Inputs: revision2 SCIENTIFIC_INPUT_BINDING + derived manifest SHA256 `69d8cd2fd24f52a9d52c6e17b327cde2a46ae0bbc4def792d42a7666456b54b9` และ pinned intake ledger; source read-only,2200สมาชิก
- Actions: เพิ่ม standalone CPU measurement/queue/local reviewer; ten axes + four targets; source/SHA/geometry/path guards, persisted append-only review revisions, token-gated loopback data access; ไม่แก้ pending coverage files/DB หรือ active benchmark
- Outputs: assisted_coverage.py/html, targeted requirement fixtures, ASSISTED_COVERAGE_WORKFLOW_TH.md; private measurements2200/failure0, semantic reviews0/GT0; tmux viewer8041
- Verification: 7fixture tests, JS syntax, synthetic save+refresh, real-image load/zoom+refresh และ unauthenticated401; browser checksไม่ใช่ semantic coverage acceptance; headlessThai glyph limitationบันทึกไว้
- Recovery: UI session-token correctionมีchild-run compatibility record; reuse CPU measurements2200ตามsource+measurement bindingsเดิม ไม่เขียนทับparent ไม่ทำmodel calls
- Blockers/next: ยังต้อง rule-critical visual checks + lossless bridge readiness ก่อนpilot; full semantic coverageยืนยันระหว่างตรวจannotation ผู้ใช้ยังต้องตรวจทุกภาพก่อนacceptedGT
- Git scope: stageเฉพาะ source/tests/guide/report/log และ prefixREADME/AGENTSของรอบนี้ รักษาuncommittedงานเก่าที่เหลือครบ ไม่บันทึกprivateimages/metadata/tokens/DB


## LOCAL-WEB-SYNC-20261105 — USER_REQUESTED / IMPLEMENTED / VERIFIED

เวลา 2026-11-05T17:07:37.546025+07:00 (Asia/Bangkok); inputs: accepted revision2 manifest+ledger,assisted coverage parent runและDB; เหตุผล:เปิดบนbrowserได้โดยยังใช้local dataชุดเดียว

เพิ่มincremental API,client sync5s,revision-based409,dirty draft protectionและconnectionstatus; ไม่เปลี่ยนmembership/ภาพ/measurement/annotation policy ใช้childrunพร้อมhashes/AST reuse receiptและpreserveparentDB. Outputs:แก้source/UI/tests/guide/README/report; viewerเฉพาะloopbackในtmux; privatehandoffเก็บURL/token/logs. Verification:9 targeted tests + synthetic two-browser/restart/offline cases; realpopulation/API2,200,sourcebindingsตรง,review0. No model inference/GPU/newmeasurements. งานเก่าที่ค้างในworkingtreeคงเดิม ไม่stageร่วม

Next/blockers:เปิดผ่านSSH tunnelแล้วกดบันทึกเพื่อซิงค์; offlineworkingและpolygonbridgeยังไม่implemented; annotation/pilotยังต้องreadinessขั้นเดิม. Routinecommit/pushเฉพาะงานนี้และตรวจremotematchก่อนส่งมอบ


## SCALE-PSEUDOLABEL-20261105 / REVIEWED_PROPOSAL + CPU_HELPER_IMPLEMENTED

เวลา 2026-11-05T17:49:05.455322+07:00; inputs: current2200intake, existingguideline/contract/pilot24, localSAM3adapterrevision8330c45, officialCOCOevaluation/SAM3README. แยกvisiblepixelscaleจากmetricdistance,เลือกSAM3draft+humanreviewโดยไม่อ้างzero bias,คง6blindfirst-pass,คงpilot24reuseกับrelease300. Outputs:คู่มือเดิมฉบับอ่านสั้นพร้อมภาคผนวก,annotation_scale.py/tests,แก้population2400เก่าในcurrentpilotrow. Verification:4independentfixturesผ่าน; sourceoutputsไม่เปลี่ยน. Blockers:Faceboundaryworkingrules/exporttopology/desktopreadinessยังไม่ปิด; no actualpilot/inference. Backupdraftเดิมและsourcebindingsเก็บprivate. Commit/pushเฉพาะงานนี้; ไม่รวมpendingcoverage/webfiles


## ANNOTATION-EVIDENCE-20261105 / REVIEWED_PROPOSAL

เวลา 2026-11-05T18:02:49+07:00 (Asia/Bangkok). ผู้ใช้ขอค้น paper/แนวทางให้ละเอียดขึ้นและทำให้ขั้นทำจริงเรียบง่าย ใช้ HEAD08294ac, คู่มือเดิม, registry S03–S11, intake revision2 และ local SAM3 adapter เป็น inputs

- อ่าน CrowdHuman official, RAP §III-B, Cityscapes policy, COCO evaluation, SAM3 README และ Benenson2019 v2 §4–5; CVF403 ใช้ author arXiv แทน บันทึก locator/ข้อจำกัดและหยุดเมื่อพอตัดสิน workflow ไม่ทำ literature review ไม่สิ้นสุด
- Outputs: แก้คู่มือเดิมเป็น 4 คำถามพร้อมกติกา6ข้อ, factor/action table, proposed Face boundaries/cross-zone/valid domains, pilotQA และ reuse; เพิ่ม evidence section และสถานะบน reports/README เดิม ไม่มี master plan ใหม่
- Status: เอกสาร REVIEWED_PROPOSAL 0.2-R1 ไม่ใช่ accepted GT/annotation-ready; กฎ Face และ evaluator domains เป็นข้อเสนอ ไม่แก้ frozen benchmark; ภาพ2,200ไม่ได้ถูกตรวจ semantic ใหม่
- Verification: ตรวจ local Markdown links, table columns, diff/privacy และ appendix preservation ตาม receipt ภายนอก; ไม่รัน full tests เพราะเปลี่ยนเอกสาร ไม่มี inference/weights/environment/dataset changes
- Blockers/next: ทดสอบ lossless raw masks + desktop roundtrip และ effective SAM3 device/precision; ผูกตัวอย่างกับกฎก่อน pilot24 คง6human-first ไม่เปิด pilot ในรอบนี้
- Git: รักษา workingchanges เดิม; stageเฉพาะเอกสารรอบนี้ Git historyเป็นcommitidentity ไม่ใส่hashของcommitตัวเองลงlog


## PERSON-PARTS-PSEUDO-20261106 / SCRIPT_IMPLEMENTED_CPU_CHECKED

เวลา 2026-11-06T13:29:28+07:00 (Asia/Bangkok). ผู้ใช้ขอเกณฑ์คนเล็ก/จำนวนseedและscriptsทำbboxคน/personmask/4partsด้วยpseudo-labels ก่อนตรวจแก้ ยืนยันไม่ต้องการGUIใหม่ ไม่อ้างarchitectureที่ไม่มีส่วนร่วมกับผู้เข้าสอบทั้งหมดหรือปราศจากbias

- Inputs: HEAD49e9432, accepted2200revision2binding+manifest/ledger, คู่มือ0.2-R1, localSAM3checkout8330c45พร้อมweights3,450,062,241bytesและsource/environmenthashes; เพิ่มprimarysourcesCityPersons/SAM3paper/GroundingDINO/graphcutreadinessrationale
- Outputs: person_pseudolabel.py, sam3_person_draft.py, requirementfixtures; อัปเดตคู่มือ/evidence/QA/reportstatusเดิม ไม่มีเว็บ/แผนใหม่ Sourceimagesreadonly; queue24metadata-diverseจาก24camera groupsแต่coverageNOT_CONFIRMED มี6calib/6human-first/12workflow
- Behavior: nohardpixeldeletion; longestside20/50/100reviewtags; nativePNGplanesทุกcandidate/target+raw/ownedproposal/conflicts, exactmapback, prompt/box/source/modelprovenance, explicitone-IDexecution/callbudget/attemptlock/atomicpacket/readback, noautomaticGT/negative/ignore/fallback/retry
- Verification: CPU14requirementfixturesผ่าน + realinput/hash/env/SAM3CPUimportprecheckผ่าน, modelcalls0; syntheticpacket+previewเก็บprivate. systempythonไม่มีPillowจึงใช้existingvenvโดยตรง ไม่ติดตั้งแพ็กเกจ. พบmanifestpixelhashencodingต่างservercanonicalhash จึงแก้importerให้reuseacceptedfilename+byteMD5+ledgerbindingsและactualSHAที่readไม่แก้data/หลักฐานเดิม
- Limitations: SAM3person/partqualityและGPUpeakยังไม่ทดสอบ, queueยังไม่visualaccepted, มีSapiens1Bใช้T4อยู่จึงไม่แทรกGPUcallในงานสร้างscript/researchนี้ ไม่ประกาศว่าGPUรันไม่ได้เพียงเพราะexternalPID. PromptFace/garmentsไม่รับรองtaxonomyagreement; ownedintersectionไม่ใช่GT; ไม่มีautoaccept/exportevaluation
- Next: ยืนยันcoverage/6human-first; boundedcalibrationหนึ่งภาพด้วยactualresourcechecksและดูrawoutputsก่อนpilot24; ขยาย300ตามกฎที่freezeและreviewทุกภาพโดยไม่ใช้คะแนนผู้เข้าสอบตั้งGT
- Git: stageเฉพาะscripts/tests/docsรอบนี้ คงpendingworkเดิม; metadata/IDs/images/weights/rawrunอยู่นอกGit ไม่มีnativebenchmark/environment/sourceadapterchanges


## GT-SCOPE-20261106-USER-ACCEPTED

เวลา 2026-11-06T15:52:24+07:00 (Asia/Bangkok). ผู้ใช้ตอบ “ได้ งั้นตามนี้” หลังยืนยันหลักbenchmarkและข้อจำกัดของ GT bbox+personID+4parts

- Decision: GT บังคับคือpersonbbox/image-localpersonID/HairFaceUpperLowermasksพร้อมvalidity; full-personGTmaskoptional ไม่บังคับreview SAM3/YOLOpersonmaskให้เป็นเฉลย การจัดเจ้าของของbaselineยังใช้predictedYOLOmaskหลังRGBcrop parsing ไม่ใช้GTแก้prediction
- Scope of acceptance: ยืนยันชนิดข้อมูลและหลักการเปรียบเทียบเท่านั้น ไม่freezeFace/Dress/mapping/matchingthresholds/ignore/aggregation หรือรับรองcoverage/pilot/scorer/GPUready. สีบนล่างคงrequirementsเดิมตามobservability
- Outputs: อัปเดตคู่มือหลัก/QA/status/READMEและqueueproducer metadata ให้แยกrequiredGTกับhelperpersonmask ไม่แก้scientificinference behaviorของdraftdriver/nativebenchmark/scorer ไม่แก้legacyannotationtemplate0.1หรือhistoricalappendix
- Verification: document/table/link consistency, stagedscope, existingCPUfixtures14เพื่อยืนยันqueueadditionไม่เปลี่ยนpacketgeometry/ownership/budgetguards; ไม่modelcalls ไม่มีbulkdataaudit
- History: queue24เดิมและprechecksรักษาไว้; amendmentreceiptในprivateworkrunผูกparentQUEUEhashและdecision ไม่แก้queuefingerprintย้อนหลัง ข้อมูลยังเป็นcandidateไม่ใช่visualaccepted
- Next: ยืนยันcoverage/rulecases + losslesseditroundtrip; boundedcalibration/pilot24และ6human-firstก่อนfreeze/ขยาย300. Newbboxmatcher/evaluatorยังต้องimplementation/acceptanceที่ประกาศ ไม่รายงานfull-personmaskmetricsหรือใช้Qเก่าแทน


## MASTER-PLAN-REVIEW-20261106 / REVIEW_COMPLETE_FOUR_SCOPE_DECISIONS_ACCEPTED

เวลา 2026-11-06T18:02:31+07:00 (Asia/Bangkok). อ่านprivate PSEUDO_LABELING_MASTER_PLAN_2200_TH.mdครบ249linesพร้อมSHAในprivateinputreceipt; ผู้ใช้ขอreviewไม่ใช่executionคำสั่งในไฟล์ ผู้ตรวจไม่แก้ต้นฉบับ พบconcurrentrevisionต่างเฉพาะlines52/54/97เรื่องsmallpersonsexcludedและตรวจล่าสุดแล้ว รักษาsnapshotsสองรุ่นprivate

- Inputs: HEAD34d2dd8/acceptedGTscope/scripts+prechecksเดิม, accepted2200manifest/ledger, SQLitereadonly, native-label/color-source และprimaryofficialCityPersons/NightOwls/CrowdHuman/SAM3.1/CoDETR/RFDETR/SegFormer
- Review: 15MUST_FIX rowsและmetadata/resourcechecksในreports/PSEUDO_LABELING_MASTER_PLAN_REVIEW_TH.md. พบno-bias100%claimผิด,50pxไม่ใช่กฎร่วมสากล,polygonloss/ignore/validity/FaceDressIDs,autoIR/distance/OSD/MLPcategoryสมมติฐาน และไม่มีsplit/freeze. SourceSAM3.1weightsพบจริงโดยstat ไม่claimload/readiness
- User decisions: (FT) helperfine-tuneหลังverifiedseed; (SIZE) primaryGTbboxlongside≥50pxและเก็บsmallpeople/excludedstates; (DET) separatebenchmarkYOLO26/11/v9/v8ไม่ขยายparserroutes; (SPLIT) same-cameraคนละevent/timeblocksไม่ใช่unseencamera. Counts/IDsของsplit/seed/modelweightsและscorerpolicyยังต้องปิดก่อนlaunch
- Outputs: reviewreportใหม่หนึ่งฉบับ, updatedguide/QA/status/README/AGENTS+queuepolicy metadata; ไม่สร้างmasterplanซ้ำ ไม่แก้benchmarkinference/scoring/configเดิม. metadataใหม่ไม่มีผลfilterคนเล็กหรือรันtraining
- Verification: counts2200/67cameras/93dates/17fields;269suppliedvisualclaimsไม่เท่ากับhumanGTreceipt;remark16ไม่ใช่18;minsamecameragap1807sและ655adjacentgaps<14400s. Reusefileaudit ไม่newdecode/bulkhash. ExistingCPU14casesสำหรับqueueadditionและdoclinks/tables/inputimmutabilitychecksตามreceipt
- Blockers/next: ปรับmasterplanตามreviewโดยรักษาประวัติ; กันevent/timegroups+sourceidentityก่อนseed, ตรวจmodelcheckpoint/task/resourceและlosslesseditroundtrip, pilot24ภายในseedเป้าหมาย300ก่อนFT; GTfullpersonmaskยังoptionalและกฎละเอียดNOT_FROZEN
- Git/private: นำเฉพาะpublic-safereview/docs/codeขึ้นrepo; originalplan/metadata/รายชื่อกล้อง/DB/weights/rawevidenceอยู่นอกGit ไม่มีmodelcalls/training/download/installในรอบนี้


## MASTER-PLAN-REVISION2-20261108 / REVIEWABLE_NOT_FROZEN

วันที่ผู้ใช้ 8 พฤศจิกายน 2026 (Asia/Bangkok); audit recorded UTC 2026-11-07T19:40:16.121266+00:00. ผู้ใช้ขอให้สรุปสิ่งที่ต้องปรับและทำให้ดูพร้อมคำอธิบายง่าย จึงปรับแผนprivateไฟล์เดิมหลังสำรอง ไม่สร้างmasterplanคู่ขนาน

- Inputs: HEADd0eb110, private masterplan249lines SHAac52fba48f6aacba2601984ea7330598f4e3243b79b98210b703795a47a202ad, review15กลุ่มและสี่คำตัดสินผู้ใช้; ไม่มีข้อเท็จจริงmodel/readinessใหม่ที่อ้างจากการรัน
- Outputs: masterplanrevision2รวม154lines SHA07a221a9ab8439bfa60cb95d2d893f53dcf4b6e990ce104a982dc8387fd0ad23, beforebackup+revisionmanifestprivate; เพิ่มpublicfriendlysummaryในreviewเดิม, status/guide/READMElinks ไม่อัปโหลดprivateplan/metadata/weights/ภาพ
- Changes: แยกaccepted/proposed/pending; เก็บsmallpeopleและprimary50, losslessGT/editablecopy, event/timegroupก่อนseed/FT, pilot24ภายใน300, helpermodel/taskbindingsแทนAPwinnerclaim, sourceIDsถูก, per-taskvalidity/unknown/type/color/OSDที่ไม่เดา และseparatedetector/parser/colorclaims
- Verification: documenttables/links, backuphashและconcurrentwriteguard, acceptedscopetrace, historicalreviewpreserved; ไม่มีexecutionacceptanceหรือfulltestsเพราะเปลี่ยนเอกสารเท่านั้น
- State/next: REVIEWABLE_NOT_FROZEN ไม่เปลี่ยนacceptedGTscope ไม่เริ่มsplitassignment/inference/training/download/install. ถัดไปปิดschema/ignore/actualeditroundtripและเสนอevent/timegroupsเพื่อseed/pilotreadinessก่อนlaunch
- Git: เฉพาะrelateddocs; pendingworkingchangesเดิมรักษาไว้; Gitเก็บcommitidentityเอง ไม่ใส่selfhashในlog

## SCOPE-50PX-BOUNDED-20261108 / USER_SCOPE_CLARIFIED_NOT_FROZEN

เวลา 2026-11-08T15:20:20.842745+07:00 (Asia/Bangkok). ผู้ใช้ย้ำงานหลักคนตั้งแต่50pxและขอจำกัดงานให้อยู่ในรูปแบบเดียว ลดงานที่ขยายโดยไม่จำเป็น

- Inputs: HEADa36ae93, private masterplan revision2, ข้อตกลงเดิม primary visible GT bbox max(width,height)≥50 และคำชี้แจงผู้ใช้ล่าสุด; ใช้หลักฐานเดิม ไม่ตรวจภาพทั้งชุดใหม่
- Changes: ปรับแผนเดิมเป็นrevision2.1และคู่มือให้คน<50ทำเพียงข้อมูลยกเว้นขั้นต่ำ ไม่วาด4parts/สี/GTmaskทั้งตัวหรือไล่bboxละเอียดโดยไม่จำเป็น; คนคาบเส้น50วัดbboxก่อน; แก้ข้อความคู่มือที่ยังเปิดเกณฑ์ขั้นต่ำไว้กว้าง; เพิ่มตารางทำ/ไม่เพิ่มเอง/จุดหยุดและรูปแบบกลาง
- Outputs: masterplan172lines SHA256 40eec96ff94ce2e23f4a0d1ff62befa2477c2e67d7afdabaa9fe497f8cd55961; backupก่อนแก้และDOCUMENT_CHECKอยู่private work run scope-50px-bounded; อัปเดตreview/statusเดิม ไม่สร้างแผนหรือรายงานคู่ขนาน ไม่เผยแพร่ภาพ/metadata/privatepaths
- Verification: hashตรงรายงาน, relative links43รายการมีไฟล์จริง, historicalreviewและภาคผนวกguideคงเดิม, removed obsolete no-minimum wording; documentconsistencyเท่านั้น ไม่ใช่execution/scoreracceptance ไม่รันtestsuiteหรือmodelcalls
- Limits/blockers: pool2,200, pilot24ภายในseedเป้าหมาย300, helperFTหลังverifiedseedและdetector/parserแยกตามเดิม; exacttrainingbudget/schema/validity/exclusionmatching/sharedpixeldomain/desktoproundtripยังต้องปิด coarseexclusionไม่ใช่silhouetteและห้ามซ่อนpartsของคนeligible
- Next: ปิดข้อค้างเฉพาะschema/ignore/toolroundtripเพื่อpilot24; ไม่เพิ่มโมเดล/รอบฝึก/pilot/เว็บเอง ไม่เริ่มinference/training/download/splitassignmentหรือเปลี่ยนbenchmarkเก่า Gitเก็บcommitidentity; ตรวจstaged/pushและremoteก่อนแจ้งsync

## MASTER-PLAN-ACCEPTANCE-20261108 / PLAN_ACCEPTED_EXECUTION_NOT_FROZEN

เวลา 2026-11-08T15:25:07.862793+07:00 (Asia/Bangkok). ผู้ใช้ยืนยัน “ที่เหลือผมว่าโอเคแล้วปรับเลย” หลังตารางจำกัดscope/เกณฑ์50px จึงบันทึกรับรองแผนและกฎเริ่มต้นที่ระบุ ไม่ถามscopeเดิมซ้ำ

- Inputs: HEADe605366, masterplanrevision2.1 SHA256 40eec96ff94ce2e23f4a0d1ff62befa2477c2e67d7afdabaa9fe497f8cd55961, คู่มือ/review/ข้อตกลงเดิม และคำรับรองล่าสุด; ตรวจHEAD/workingtree/remoteก่อนแก้
- Changes: แผนไฟล์เดิมrevision2.2 แยกUSER_ACCEPTED planและstartingrulesออกจากpendingimplementation/readiness; รับscope≥50/ข้อมูลยกเว้นขั้นต่ำ, GT4parts/สี/validity, grouping-before-FT, pilot24ในseedเป้าหมาย300และข้อปรับที่เสนอไว้ ไม่เลือกhelperalternativesทั้งหมดหรือเติมtrainingbudgetที่ยังไม่มี
- Outputs: masterplan184lines SHA256 0b7e4d149a284ed51f5fa4075c907cb86faa86f0dec85224bc7fcc3a80b8fa4e, privatebeforebackups/provenance; อัปเดตreview/guide/status/README/AGENTSและQAtemplateเดิม ไม่สร้างmasterplanหรือรายงานเพิ่ม ไม่เผยแพร่privateplan/ข้อมูลจริง
- Verification: ตรวจhash/relative links/stateconsistency/historypreservationและstageddiff/privacy; แก้เอกสารเท่านั้น ไม่รันtestsuite/CPUacceptance/modelcalls ไม่มีผลGPU/GTใหม่
- Blockers/next: จัดทำschema/domain/ignorematching/toolroundtripและeventgroup/membershipก่อนpilot; exacthelper/checkpoint/environment/resourcebudgetยังต้องตรวจ ไม่ถือว่างานเหล่านี้ผ่านจากการรับรองแผน ไม่เปลี่ยนfrozenbenchmarksหรือsourceimages
- Git: stagedเฉพาะงานเกี่ยวข้อง; README/AGENTSใช้prefixบนHEADเพื่อรักษาunrelatedworkingedits ไม่รวมpendingworkอื่น ตรวจpush/remoteก่อนแจ้งsync ไม่ใส่selfcommithashในlog

## ANNOTATION-TIMEBLOCK-SPLIT-20261110 / MEMBERSHIP_MATERIALIZED_EVENT_REVIEW_PENDING

เวลา 2026-11-10T13:54:01.341739+07:00 (Asia/Bangkok). ผู้ใช้สั่งให้แบ่งdevelopment/heldoutและเลือกpilotก่อนannotation จึงจัดทำmembershipจากsourcebindingเดิม

- Inputs: HEAD1f7494d, hash-boundmanifest/ledger2,200, parentpilotqueue24และrolesเดิม; ตรวจworkingtreeก่อนทำ เก็บข้อมูลจริงprivate
- Method/assumptions: Codexเลือก80/20, site-localdateblocks, same-camera<4hเชื่อมข้ามวัน, supplied256bitdHash≤4เชื่อมกลุ่มก่อนแบ่ง; lockedpilotgroupsและกล้องที่มีเพียงกลุ่มเดียวอยู่development; deterministicseed20261110 ไม่ใช้ผลคะแนนหรือภาพจากโมเดลเลือกsplit
- Outputs: development1,760/heldoutcandidate440 รวม2,200uniqueIDs, 463groups; seed300ในdevelopmentครอบ67กล้องรวมpilot24/24กล้อง; heldout49กล้องและdevelopment-only18กล้อง รายชื่อ/summary/command/verification/privateรายงานอยู่run annotation-timeblock-split; ปรับแผนหลักไฟล์เดิมrevision2.3 SHA256 4856d9b34b6e168ba4f5794663838dc32c79552b52217d4a2568f387264a556d, เก็บbeforebackup ไม่ย้ายภาพต้นฉบับ
- Verification: CPUexpectedfixtures6กรณีผ่าน; exactID/sourcejoin/parentpilotและroles/subsets/กลุ่มsite-day/4hguard/nearhashข้ามฝั่ง/manifestledgerhashes/provenanceผ่าน; source/scriptSHAในrunตรวจตรงจริง ไม่มีmodelcalls
- Limits/next: TIME_BLOCKไม่พิสูจน์event/identityindependence ต้องตรวจclock/long-event/near-duplicatecontextก่อนfinaltestfreeze pilotvisualcoverage/rules/toolroundtripและGTacceptanceยังpending helpertrainvalidationจัดภายในdevelopmentหลังverifiedseed เก็บhuman-first6ตามแผนเดิม
- Git: ตรวจstaged/privacy/linksและpushเฉพาะsplitcode/tests/relateddocs; รักษางานค้างREADME/AGENTSและcoverageเดิม ใช้Gitเก็บcommitidentity

## SPLIT-DETAILED-REVIEW-20261110 / REBALANCE_REQUIRED

เวลา 2026-11-10T14:15:41.704659+07:00 (Asia/Bangkok). ผู้ใช้ขอแนะนำการแบ่งและตรวจละเอียด จึงตรวจmasterrevision2.4 SHA256 5dbd59af8a3b4096cd27c0e29da8d70acd6a2c7f683528057246d8c70cea3037 เทียบmanifest/summaryปัจจุบัน

- Inputs: HEADd1df444, parentmembership2200/463groups/seed300/pilot24; อ่านmetadataและbinding ไม่เปลี่ยนต้นฉบับแผนล่าสุดหรือmembership
- Findings: test440อยู่27groups, sitefractions6/147ถึง157/219; วิธีเดิมเน้นcamera/countทำให้บางสถานที่กระจุก ต้องปรับouterallocationก่อนfinalfreeze เก็บparentเดิม
- Proposal: outertargetdevelopment1760/heldout440แบบgroup-stratifiedsite/time; helpertrain240+fixedval60ในseed300 รวมpilottrain24; Boost550เฉพาะdevelopmentนอกvalgroups; รอบสองtrain790/val60 แล้วfreezeรุ่นที่ผ่านเกณฑ์จากvalidation
- Verification: metadatafeasibilityกันval60/8sites/47cams(22day38night)โดยtrain240ครอบ67camsและpilotอยู่train; valgroupsรวม159คือval60+nonseed99 มีeligibleBoostpool1361 ตัวเลขต้องตรวจใหม่หลังouterrebalance ไม่อ้างว่าเป็นรายชื่อที่materializeใหม่หรือvisualGT
- Outputs: อัปเดตreview/statusเดิมและprivateinputsnapshot ไม่มีnewmasterplan source/inference/trainingหรือscorechanges
- Next: แก้site/timeallocation เก็บrevisionและmembershipdiffก่อนhelperpartition/coverage/toolreadiness/GTacceptance ไม่มีfinaltestfreezeจากการตรวจนี้

## BALANCED-SPLIT-HELPER-20261110 / MEMBERSHIP_VERIFIED_EVENT_GT_PENDING

เวลา 2026-11-10T14:38:55.005661+07:00 (Asia/Bangkok). ผู้ใช้อนุมัติปรับสคริปต์และmembership Outer Split/helperตามข้อเสนอ

- Inputs: HEADac561e1, source manifest/ledger2200และparent/pilot bindings, master2.4 ตอนเริ่มSHA5dbd59af8a3b4096cd27c0e29da8d70acd6a2c7f683528057246d8c70cea3037 ระหว่างงานพบเปลี่ยนเป็นSHAdfb5a62da8c1f48aa6d9a5168f944a03c39087f74358f37c4c372df336448d7eโดยเพิ่มAuto-Triage/รายละเอียดแบ่ง เก็บรุ่นล่าสุดครบก่อนแก้และรักษาAuto-Triageพร้อมสถานะpending
- Method: per-siteเป้า20% DPเก็บsubsetสมดุลmetadataต่อcountแล้วรวมSite น้ำหนักcamera0.05/day-night0.1/groupcount0.02/overallcount4ในSUMMARYก่อนคะแนน; รักษาpilotและdevanchorsทุกกล้อง seed20261110; cross-site linkedblockหยุดทบทวน
- Outputs: development1760/test440; train240/val60/Boost550/reserve910 pilot24ในtrainครบ Test106blocks/46cams/8Sites มี19.23–20.14% เทียบparent27blocks/49camsและSite4.08–71.69% Siteเดียว2ภาพอยู่development
- Isolation: validation21groupsรวม206ภาพ(60val+146reserve)พ้นtrain/Boost; round1train240/val60 round2train790/val60; parent/source/pilotและmetadataตรง เก็บDIFF770rowsจากouter716IDs/seed212IDs พร้อมSITE_BALANCEจริงprivate
- Verification: CPUindependentexpected9casesผ่าน และactualcheckexact2200/no missing/no duplicates/timegroups/4hguard/dHashpair/groupisolation/pilot/roles/source-parenthashesผ่าน มีmodelcalls0 Script/source/env/launchcommitbindingsอยู่run
- Docs: ปรับmasterไฟล์เดิมrevision2.5 SHA256 b9520610edcc1ce88761ca1e30cec70588fad6bcebb08ef638bb776112329408 เก็บbeforebackup พร้อมpublicreview/status/guide/QA/README/AGENTSและlogเดิม ข้อมูลจริงprivate
- Limits/next: Testcamera49เป็น46แลกกับSitebalance รอsource-context/visualcoverage/schema/ignore/toolroundtripและGTacceptanceก่อนfinalfreeze helper/model/resourcebudgetตรวจตามขั้น Auto-Triageเป็นงานถัดไปตามข้อกำหนดที่เก็บไว้
- Git: ตรวจdiff/staged/privacy/linksและcommit/pushเฉพาะงานเกี่ยวข้อง รักษาREADME/AGENTSworkingchangesเดิมด้วยprefixบนHEAD Gitเก็บcommitidentity

## AUTO-TRIAGE-REVIEW-20261110 / SPEC_REVIEWED_IMPLEMENTATION_PENDING

เวลา 2026-11-10T14:53:28.528410+07:00 (Asia/Bangkok). ผู้ใช้ขอตรวจข้อ4.1ที่เพิ่ม จึงอ่านส่วนนี้กับcode referencesที่จำเป็นและแก้ข้อกำหนดให้ตรงGTscope/หลักฐานจริง

- Inputs: HEAD8f65f05, masterก่อนแก้SHAb9520610edcc1ce88761ca1e30cec70588fad6bcebb08ef638bb776112329408, person_pseudolabel/run_frame/mask_info/save_predictions, sam3driver และlocalSAM3processor revision8330c45f4d47f62588122e462ac3eb7e0a2e6f46
- Findings: finalignoreจากdraftboxเสี่ยงผิดGTeligibility, scoreเป็นperson/partpromptscoreไม่ใช่ผลตรวจGT, zerooverlapอาจยังพลาด/คลาสผิด, empty-all-passเสี่ยงfalse-negativeacceptance, existingbboxexportมีrectangleเท่านั้น, GPUcallbudgetsและattemptlocksต้องรองรับlinkedcorrections
- Outputs: เก็บbeforebackupprivateและปรับเฉพาะ4.1เป็นTRIAGE_SPEC_REVIEW_1_PROPOSED SHA256 851480e6b7526e9fd145a5106246a68486bb451ffc21934850df9648eda5415c; SMALL_CANDIDATEก่อนhuman-confirmedexclusion, proposed45–55/0.85triagethresholds, rawdiagnosticsก่อนclip, sharedrevisionviews/descriptiontags/receiptและexpectedacceptancecases; อัปเดตreview/statusเดิม
- Verification: ตรวจส่วนอื่นของmasterbyte-equivalentก่อน/หลัง, sourcefunctionreferences/scoreformula, links/hash/stagedprivacy ไม่มีcode/config/modelcalls/trainingหรือtestsuiteเพิ่มในreviewนี้
- Next: Implementtriage/sizegating/linkedcorrection/actual4parteditorbridgeและตรวจexpectedcasesตามbudgetเมื่อถึงขั้นที่อนุมัติ ค่า45–55/0.85ยังเป็นข้อเสนอเพื่อpilot ไม่ถือว่าGTignoreหรือautoacceptanceผ่านแล้ว
- Git: commit/pushเฉพาะreview/status/logที่เกี่ยวข้อง ข้อมูลจริง/source snapshotsprivate Gitเก็บcommitidentity

## PERSON-MASK-WORKLOAD-20261110 / GT_SCOPE_CLARIFIED

เวลา 2026-11-10T16:05:19.415805+07:00 (Asia/Bangkok). ผู้ใช้ถามว่าต้องแก้person maskเพิ่มหรือไม่ จึงตรวจถ้อยคำและพบคู่มือมีประโยคpersonmasksต้องแก้ที่ขัดscopeoptionalGT

- Inputs: HEAD3677f4b, masterSHA851480e6b7526e9fd145a5106246a68486bb451ffc21934850df9648eda5415c, guideและข้อ4.1 ปัจจุบัน พร้อมสถานะworkingtree
- Changes: masterเฉพาะ4.1และguideกำหนดbbox/personID/4parts/สีตามที่เห็นเป็นภาระตรวจรับ Person maskเป็นhelperwarning การรับGTผ่านได้แม้helpermaskผิด/outside-personยังมี ปรับqueuewordingให้นอกmaskเป็นwarningแยกและraw4partsเป็นฐานแก้
- Outputs: masterSHAe66ee428e7d32aa7c53275778bb6bde8f02c59b5b76c8364caa1915308f090caพร้อมbeforebackup, publicreview/status/logเดิม เก็บuntrackedtriageimplementation/testsและงานค้างอื่นครบ
- Verification: ตรวจmasterนอก4.1ตรงbefore, guideแก้เฉพาะข้อความที่เกี่ยวข้อง, hashes/links/stagedprivacy ไม่มีmodelcallsหรือcodechanges
- Next: implementation/editorreadbackต้องยึดhumanreceiptสำหรับbbox/4partsและคงhelperwarningแยกจากGTacceptance ไม่เพิ่มงานpersonmaskให้ผู้ใช้

## TRAINING-REVIEW-20261112 / REVIEW_COMPLETE_TRAINING_ACTIVE

เวลา 2026-11-12T13:57:52.275542+07:00 (Asia/Bangkok). ผู้ใช้ขอตรวจคู่มือใหม่และงานที่เริ่มฝึก จึงตรวจboundedsource/config/metadata/process/log/checkpointsและpreviewจริงสองคู่ ผู้ใช้ตอบโดยตรงว่าSeed300ตรวจแก้และรับรองครบแล้ว

- Inputs: HEADa8cf640, masterล่าสุดและtraininghelperprivatecode/logs/MANIFEST/sourceannotations, balancedmembershipเดิมและsourceintakebindings เก็บsnapshot/hashesก่อนแก้
- Actual: SAM3.1PID4111696บนT415epochs logที่auditถึง6/15 trainable32,745,270 frozen820,811,264 SegFormer25epochsจบbest21/globalmIoU4=0.6454162071434428 RuntimeSAMsourcefilemtimeหลังprocessstartจึงไม่อ้างcurrentondiskhashเป็นlaunchbinding
- GT/source: directuserconfirmationผูก300JSONhashes; actual313train/77valcropsจาก213/56ภาพ อีก31เป็น13ignore-only+18empty; IDs/timegroupsข้ามsplit0 rolesผิด0 actualusedbboxต่ำสุด52/51px Savedmask390ตรงcurrentannotationทุกpixel sourceimagecopiesตรงintakebytes
- Findings: currentSAMsourceใช้sample-IoUempty/empty1 ต่างSegglobalconfusion, absenttargetsไม่ส่งmasklossและpred_scoresunused, cacheidเป็นsamplefilename, launcherkill-session/logoverwrite และruntimeprovenanceขาดแยกsource-at-launch พบหลายcode/readinessstatusในmasterยังเป็นhistory
- Verification: CPUlossfixtureยืนยันabsentloss0/scoregradientNone; val77GTabsentHair16Face40Upper4Lower9และอิสระcounterexamplesample0.5/global0 รันexistingtriageCPU9casesผ่าน ไม่มีmodelinferenceหรือtrainingprocessใหม่
- Outputs: อัปเดตexistingreview/status/masterlatestsectionและcanonicalignore4.1 ส่วนข้อมูลจริง/snapshots/hashes/confirmation/freshnessauditprivate Masterหลังแก้SHA256 d400c1265c1802877e58a9aaec2051ee19ef963f359752f4990669faf1259c0c
- Next: commonhelpervalidation/provenance/cache/loss/launcherrevisionsก่อนเลือกhelperและBoost550 รักษาactiveattempt/outputs/sourceและworkingchangesอื่นไว้ Gitเก็บcommitidentity ตรวจstaged/push/remoteตามworkflow
