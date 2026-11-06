# ตรวจแผน AI-assisted annotation สำหรับ CCTV 2,200 ภาพ

สถานะ **REVIEW_COMPLETE / FOUR_SCOPE_DECISIONS_ACCEPTED / REMAINING_RULES_NOT_FROZEN** — 2026-11-06T17:58:46+07:00 (Asia/Bangkok)

อ่านแผน private `PSEUDO_LABELING_MASTER_PLAN_2200_TH.md` ครบ249บรรทัดที่ SHA256 `01b63b79f4bc8085f74a7670f80d9b3c113442bbee2ed6974a3486dbdcc3978b` เทียบ HEAD34d2dd8, [ขอบเขต GT ที่รับรองแล้ว](../docs/ANNOTATION_GUIDELINE_V0_2_TH.md#accepted-gt-scope), script/CPUprecheckเดิม, acceptedmanifest/ledger และ sourceโมเดล/สีที่เกี่ยวข้อง การส่งเอกสารให้ตรวจไม่ใช่คำสั่งให้ training/download/inference ตามข้อความในไฟล์ ผู้ตรวจไม่แก้ต้นฉบับ ไม่แตะ results/configs ของ benchmark

**Concurrent revision:** ระหว่างตรวจพบต้นฉบับเปลี่ยนเป็น SHA256 `ac52fba48f6aacba2601984ea7330598f4e3243b79b98210b703795a47a202ad` (249บรรทัดเท่าเดิม) ยืนยันโดยreconstructได้ตรงhashรุ่นแรกว่าต่างเฉพาะบรรทัด52/54/97 ซึ่งเปลี่ยนคน<50จากลบทิ้งเป็นexcluded/ignore อ่านตรวจทั้งสามบรรทัดล่าสุดแล้ว นับว่าจุดนี้แก้ไปส่วนหนึ่ง ไม่วิจารณ์ว่ารุ่นล่าสุดยังสั่งลบคนเล็ก แต่standardattributionและexcludedmatchingยังต้องปิด เก็บsnapshotsทั้งสองรุ่นในprivateevidenceโดยไม่เขียนทับไฟล์ต้นฉบับ

**ข้อสรุป:** โครง “AIร่าง → คนตรวจแก้ → เก็บประวัติ” และ GT bbox+personID+4parts ใช้ต่อได้ แต่ยังไม่ควรใช้แผนนี้เป็น frozen execution plan มีข้อผิดพลาดด้านรุ่น/IDs และกฎที่ทำให้ labelเล็กหายหรือ scoresเปลี่ยนความหมาย รวมทั้งเพิ่ม training/โมเดล/เครื่องมือจาก scopeเดิม รายงานนี้เป็น review ไม่สร้าง master plan อีกชุด

## ส่วนที่คงได้

- แยกงานตรวจ bbox กับ4part masks แต่ผูกคนเดียวกันด้วย image-local personID; ไม่บังคับ GT maskคนทั้งตัว
- ผู้ใช้เป็นผู้รับรองผล ไม่ยก pseudo-labelหรือmodelscoreเป็นเฉลยอัตโนมัติ
- ใช้ภาพ RGB ต้นฉบับและmetadataช่วยจัดชุด ไม่ใช้overlayเป็นสีเสื้อ
- เก็บทุกชิ้นของ maskที่เห็น ไม่เติมส่วนถูกบัง และรักษาsource/model/annotationrevisions
- ใช้ตัวช่วยที่ไม่ใช่ checkpointผู้เข้าสอบเป็นการควบคุมข้อหนึ่ง แต่ยังต้องตรวจ bias/คนตกหล่น

## MUST_FIX ก่อนใช้ทำ annotation จำนวนมาก

เลขบรรทัดอ้างต้นฉบับ private ที่ตรึงhashข้างต้น ข้อเสนอในคอลัมน์สุดท้ายไม่แก้คำสั่งต้นฉบับโดยอัตโนมัติ คำตอบผู้ใช้สี่ข้อที่ได้รับระหว่างreviewระบุในตารางคำตัดสินด้านล่าง มีผลแทนข้อเสนอที่ขัดกัน

| ID / บรรทัด | พบอะไร / ผลกระทบ | ข้อเสนอแก้ที่ใช้งานง่าย |
| --- | --- | --- |
| R01 / 1,5–6,78,145 | “เกือบทุกรูป” กับ “ทุกกรอบทุกเส้น” ขัดกัน; คนละarchitecture+คนแก้ไม่พิสูจน์ไม่มีbias100% | ทุกภาพที่เป็นacceptedGTต้องมีhumanreceipt; ไม่บังคับขยับทุกเส้นถ้าถูกอยู่แล้ว เก็บก่อน/หลัง/ไม่แก้ พร้อมfull-frame missed-person review และhuman-first6 คงคำอ้างว่าcontrolledไม่ใช่bias-free |
| R02 / 8–9,80,110,181,243 | บังคับ10–25vertices, ลบcomponentsเล็ก10–15px และไม่คิดส่วน<64px²เพื่อไม่ฉุดIoU ทำให้เปลี่ยนGT/ซ่อนความผิด โดยหน่วย15pxยังไม่ชัด | เก็บrawbinaryทุกชิ้นและรู; simplifyเฉพาะeditablecopy พร้อมrasterroundtrip/diff ไม่ใช้จำนวนvertexคงที่เป็นคุณภาพ ส่วนเล็กอ่านได้เก็บ อ่านไม่ได้มีuncertainty ไม่ทำเป็นBG; cutoffต้องมีเหตุผลก่อนดูคะแนน |
| R03 / 51–54,97–101,143 | อ้าง50px longestsideเป็นกฎCityPersons/NightOwls/CrowdHumanร่วมกัน รุ่นแรกสั่งลบ; รุ่นล่าสุดบรรทัด52/54/97แก้เป็นexcluded/ignoreแล้ว แต่matcher/domainยังไม่กำหนด | แยกannotationinventoryจากevaluationsubsets; CityPersonsใช้height+visibility, NightOwlsใช้height50ของtaskนั้น, CrowdHumanมีvisible/fullboxes ไม่ใช่กฎlongestside50สากล คงคนยืนยันได้ไว้ก่อน หรือประกาศscope50เป็นprojectchoiceพร้อมexcluded/ignoretreatment ไม่ลบหลักฐาน |
| R04 / 54,130,191 | ignoreรวมทั้งรู้ว่าเป็นposter/reflectionและcrowdที่อ่านไม่ได้ แล้วให้modelไม่เสียFPโดยยังไม่กำหนดmatcher | แยกknownnon-person/uncertainperson/unreviewed; เลือกนโยบายposter/reflectionเป็นhardnegativeหรือdeclaredignoredcontextตามโจทย์ ไม่เรียกสิทธิ์ignoreฟรี ต้องกำหนดIoA/IoU,threshold,matchpriority,duplicatesและsmallpeopleให้คงที่ก่อนscoring และรายงานสิ่งที่ถูกยกเว้น |
| R05 / 29,44,79,82–84 | SAM3.1ระบุHieraและสรุปว่าเป็น4classparserอิสระ; SegFormerMiT-B5ยังไม่มีtaskcheckpoint4partsที่ผูกไว้ | SAM3paperใช้PE/DETR-likeimagepath ส่วน3.1releaseเน้นObjectMultiplexvideo ไม่ใช่หลักฐานว่าstatic4partsดีกว่า; localscriptผ่านแค่SAM3เดิมprecheck SegFormerเป็นsemanticarchitecture ต้องระบุpretrain/head/labelsและฝึก/ตรวจจริงก่อน claim |
| R06 / 164,170–171 | SapiensDressid8ผิด: native29id8คือLeft_Lower_Leg; Apparelคือid1 และไม่เท่ากับDress ส่วนCIHPid10คือTorso-skin ไม่ใช่Dress; บรรทัด164ที่อ้างSapiensมีHatแยกก็ไม่ตรงnative29catalog | ใช้taxonomybindingsจริง: CIHPDress6,Torso-skin10; SapiensApparel1,Hair4,Face_Neck3,Upper23,Lower13. ห้ามใช้IDsผิดอ้างกฎGT ไม่เรียกmappingว่าstandardโดยไม่มีrevision |
| R07 / 153,162–173 | “ปล่อยว่าง” รวมไม่ใส่/ถูกบัง/เล็ก/เบลอ; ทิ้งDressโดยไม่มีOTHER/domain และแยกFaceไม่รวมคอแล้วอ้างแก้Face_Neckได้ | คงUIง่ายด้วยสถานะpresent/absent/unobservable/notreviewed+reason; knowncross-zoneกับunknownแยกกัน เก็บregionอ้างอิงเพื่อfixedvaliddomain Face-onlyยังต่างFace_Neck: mappingเป็นproxy/targetincompatibilityที่ต้องรายงาน ไม่ใช่equivalence |
| R08 / 160,169,172,211 | วาดทับกรอบแว่น/สายกระเป๋าเล็กหรือเว้ารูเป็นpolygonเดียวเสมอ ไม่สอดคล้องvisible-materialscopeและไม่รักษาtrueholesทุกกรณี | สิ่งทึบที่แยกได้ไม่ใช่ผ้า/ใบหน้าที่เห็น หากแยกขอบไม่ได้ใช้uncertaintyตามกฎ; เนื้อหน้าที่เห็นใต้เลนส์ใสต่างจากกรอบทึบ เก็บhole/multipartได้จริง ไม่เชื่อมผ่านสิ่งบังเพื่อให้เหลือชิ้นเดียว |
| R09 / 106–120 | bboxแตะขอบ3px=>truncated, ไม่มีLower=>upperonly, lowS=>IR, BoxIoU0=>isolated เป็นข้อสรุปแรงกว่าmeasurement | ให้สคริปต์รายงานnear_border, annotated_target_pattern, low_saturation_candidate, box_overlap_scoreเป็นproxies; ผู้ใช้ยืนยันsemanticstatus สีเทาไม่พิสูจน์IR ไม่มีpolygonอาจยังไม่ทำ และกล่องซ้อน/ไม่ซ้อนไม่พิสูจน์visibleocclusionทั้งหมด |
| R10 / 111,115,207 | erosion2pxเสมอ/HSV-S<12/สี1วินาทีต่อคนเป็นสมมติฐาน ยังไม่validated ค่าสีGTไม่ควรเท่ากับoutputของextractor | แยกannotationmaskจากcolor-samplingmask; บันทึกerodepolicyและretainedpixels ไม่เปลี่ยนGTgeometry การบอกสี apparent/unknown ต้องดูregionจริง; 12colorsเป็นprojectpaletteไม่ใช่มาตรฐานสากล เวลาใช้pilotวัด ไม่รับประกัน |
| R11 / 232–235 | defaultUpper=5และLower=9 ทำให้ประเภทที่ไม่รู้กลายเป็นshirt/pants; upperunionหลายชั้นอาจมีหลายcategory+หลายสี | เก็บgarmenttypeattributeแยก optional/unknown/mixed ไม่มีdefaultเดา4codes; MLPจริงรับ58D+categoryonehot4D ต้องกำหนดadapterเมื่อประเภทไม่ทราบหรือหลายชิ้น แยกoracle-category diagnosticจากend-to-endที่ใช้predictedcategory |
| R12 / 237–243 | วาดทะลุOSDแล้วกรองwhite/greenอัตโนมัติไม่มีsourceimplementationรองรับ; white/greenอาจเป็นเสื้อจริง “allvalidcontours≥15”ยังทิ้งชิ้นเล็ก | sourceartifactregion/uncertaintyแยกจากclothGTและvalidity กรองเฉพาะOSDที่ระบุได้อย่างอิสระจากprediction ไม่ลบสีตามhueอย่างเดียว; scriptปัจจุบันเก็บPNGทุกชิ้น ไม่ใช่polygon≥15px และdesktopeditroundtripยังไม่ผ่าน |
| R13 / 19,57,65,82 | COCOallclassAPใช้ตัดสินhelperCCTVperson/4partsโดยไม่มีcheckpoint/revision/resourcebindings; ตัวเลขRF-DETR-L60.1ผิดรุ่นในtableปัจจุบัน | Co-DETR64.8มีหลักฐานCOCOtest-devของO365pretrainedSwin-Lconfiguration; RF-DETRofficialปัจจุบันL56.5และ2XL60.1 ห้ามเทียบต่างsplit/taskแล้วสรุปCCTVดีที่สุด ระบุexactcheckpointและวัดpersonrecall/FP/แก้จริงบนdevpilotก่อนเลือก |
| R14 / 10,21,31,65,83 | “เรียนรู้สไตล์ที่ชอบ” เสี่ยงทำGTตามความชอบแทนนิยาม; ยังไม่มีdev/test/freezeและหยุดtrainingrule | ฝึกhelperตามannotationpolicyที่ยืนยันแล้ว ไม่รับประกันเรียนจาก300แล้วแม่น/เร็วขึ้น ผู้ใช้เลือกfine-tunehelperหลังverifiedseedแล้ว ให้มีpretrainedcalibration/เครื่องมือผ่านก่อนseed และใช้devvalidationเลือกcheckpointกับbudgetชัดก่อนtraining ไม่อ้างว่าFTรับประกันดีขึ้น |
| R15 / 23,43,200–203 | เพิ่มYOLO4ตระกูลและteacherหลายตัว รวมทั้งwebcolorinterfaceใหม่ต่างจากscopeเดิม | แยกงานdetectorstudyออกจากparserที่ใช้frozenYOLO26x-Seg ต้องยืนยันexactmodels/task/weights ไม่เปิด4×9routesเอง สี3methodsตรงselectionrecordปัจจุบันแต่ไม่ใช่อนุญาตrunใหม่ การตรวจนี้ไม่เปิดเว็บใหม่ |

## Metadata ที่ตรวจจากไฟล์จริง

ใช้acceptedserver-reconciledCSV17fieldsและledgerbindingsเดิม ไม่decode/rehashimagesทั้งชุดซ้ำ SQLiteเปิดmode=ro ไม่เปลี่ยนreviewDB; detailedreceiptเก็บprivate แผนเดิมไม่ได้ถูกอัปเกรดเป็นหลักฐานเพราะเขียนว่าตรวจแล้ว

| รายการในแผน | สิ่งที่ตรวจได้จริง / ขอบเขต |
| --- | --- |
| 2,200ภาพ / 4batch×550 / 9sites / 67camera groups | ตรงmanifest; 300ที่กล้องละ4–5ให้ได้268–335ภาพ จึงต้องจัดquotaรวมให้ตรง300 ไม่ใช่เลือก269เดิมแล้วรับรองcoverageทุกกล้อง |
| day613/night1587 และ5timebins | จำนวนตรงmanifest แต่ชื่อNight_Late_IRไม่ใช่sensorIRproof Timestampเป็นfieldต้นทาง ไม่ใช่หลักฐานcapturetimeหรือlightingที่ยืนยันแล้ว |
| category14 / remark18 | categoryมี14ค่าจริง; remarkมี16ค่าต่างกัน; รายชื่อcategory/บางcountsในตารางไม่ครบตรงไฟล์ categoryระดับrecordไม่รับรองอาชีพของทุกคนหรือมีuniformทุกแบบ |
| ACTUALLY_VIEWED269 / AUTO_PROPOSED1931 | ตรงuploadedmetadata แต่ไม่พิสูจน์คุณเคยreviewทุกภาพนั้นหรือGTaccepted เครื่องมือassistedปัจจุบันมีreviewrecords0; คนละclaimกับlegacyvisualobservations |
| dHash256bit /93calendar dates | encodingมี64hexcharsและparseได้93วันที่ต่างกัน แต่dHashไม่รับรองpose/event/identityindependence |
| selection_reasonมีGap≥14400 | เหตุผลคัดไม่ใช่invariantของactivepopulation: adjacentrecordsกล้องเดียวกันต่ำสุด1807s และ655adjacentgapsต่ำกว่า14400s ไม่ใช้ช่องนี้รับรองeventsไม่ซ้ำ |
| luma/edge/dark/bright | มีmeasurementJSON11keysจริงในSQLite; ตารางmeasurementsเก็บid+content ไม่ใช่11semanticGTfields เป็นwhole-imageCPUproxies ไม่ใช่คนเล็ก/blur/glare/IRGT |
| saturation<12 / BoxIoU crowd / truncation | ยังไม่มีpersonGT/regionGTครบสำหรับยืนยัน อาจimplementเป็นcandidateflagsภายหลัง ต้องมีunknownและหน่วย/rangeชัด ไม่เอาflagจากpredictionเป็นGTdifficulty |

## ความพร้อมโมเดลและเครื่องมือที่ยืนยันได้

| ส่วน | สถานะจริง |
| --- | --- |
| SAM3เดิม | localweights/source/environmentผูกไว้และCPU14fixtures+precheckผ่าน ไม่มีGPUcalibrationหรือ4partqualityacceptance |
| SAM3.1 | พบไฟล์local `sam3.1_multiplex.pt` จริงจากstat แต่ยังไม่ได้ตรวจkeys/hash/architecture/environment/taskbindingsหรือGPUload ไม่สรุปพร้อมจากชื่อไฟล์ และไม่เสียบแทนweightsเดิม |
| Co-DINO/RF-DETR/SegFormer | ข้อมูลupstreamมีจริง แต่ยังไม่มีreadyconfigurationของโครงการที่verifiedในรอบนี้ การค้นชื่อไฟล์แบบจำกัดไม่ใช่หลักฐานว่าไม่มีอยู่ทุกที่ ไม่download/installหรือclaimT4memoryพอ/ไม่พอ |
| X-AnyLabeling | bbox/group_idworkflowทำได้ตามformat แต่actualdesktopversion/editroundtripสำหรับholes/componentsยังต้องตรวจ ไม่รับรองจากsyntheticPNGอย่างเดียว |
| Color methods | sourceรับรองM1/M4/MLPเป็นselectedroster3จริง; MLP58+4=62dimensionsและต้องcategory5/7/9/12; preprocessorปัจจุบัน5×5ellipseพร้อมguards/fallback3×3/ไม่erode ไม่ใช่erode2pxเสมอ ไม่มีOSDwhite/greenremovalตามที่แผนอ้างในsourceที่ตรวจ |
| โปรแกรมที่มี | helperเก็บfullpersonmaskได้แต่GTไม่บังคับ มีone-IDboundeddriver/atomicpacket/history/rawparts/ownedproposal ต่างจากmasterplanที่บอกมีpolygoneditor/FT/colorsgalleryครบแล้ว |

## Fine-tuning และชุดทดสอบต้องแยกหน้าที่ — ผู้ใช้เลือก same-camera held-out events

การฝึก **annotation helper** ไม่เหมือนการฝึก **ผู้เข้าสอบ** และไม่ทำให้คะแนนผู้เข้าสอบผิดอัตโนมัติหากcandidateweightsยังfrozenและGTได้รับการตรวจจริง แต่แหล่งร่างที่ต่างกันตามbatchทำให้annotationerror/style/effortสัมพันธ์กับbatch ต้องเก็บteacher/checkpoint/source/versionและhumaneditsรายimage พร้อมblindmanualauditที่เลือกไว้ก่อนเห็นdraft

หาก300ภาพแรกใช้พัฒนากฎ เลือกhelperหรือfine-tune ให้ติดdevelopmentexposure ไม่เรียกทั้ง2,200ว่าunseenconfirmatorytest ใช้ส่วนdevสำหรับadaptivehelper/policy แล้วfreezeก่อนงานfinaltest; finaltestselectionต้องพิจารณากล้อง/เหตุการณ์/เวลาและduplicates ไม่ใช้randomimageหรือdHashอย่างเดียวรับรองindependence

เป้าหมายunseen-cameraกับfuture-same-cameraต้องsplitต่างกัน หากseed300ครอบทุกกล้องแล้ว จะอ้างcamera-held-outจากกล้องเดิมไม่ได้ ผู้ใช้เลือกกล้องเดิม/คนละเหตุการณ์แล้ว จึงให้วางtemporal/eventgroupsภายในกล้อง ไม่กำหนดจำนวนtrain/dev/testเองในreviewนี้ และไม่รับรอง1900ภาพที่เหลือว่าเป็นindependenttestโดยอัตโนมัติ

การวัดความเร็วใช้actualdraft/edit/reviewtime และpeakRAM/VRAMหลังboundedcalibrationบนT4 ไม่เอาAP/ขนาดweights/ตัวเลขH100ในpaperมาทำนายเวลาหรือmemoryของserverเรา ไม่รับรองfine-tuneCo-DINO/SAM3.1บนT4ก่อนมีresourcecheck

## โครงที่แนะนำให้แก้ในต้นฉบับหลังรับคำตัดสิน

1. คงbbox+personID+4parts/validity+colorstatus ไม่เพิ่มfull-personGTmaskบังคับ ใช้humanreceiptทุกacceptedimage
2. คืนpilot24ก่อนseed300 เก็บ6human-firstและrule-criticalcasesที่พบจริง ห้ามให้draftgateทำคนเล็กหรือชิ้นเล็กหาย
3. เริ่มhelperpretrainedที่bindings/readinessผ่าน วัดpersonmiss/FP/partboundary/ownershipและhumaneditburden ก่อนเลือกเพิ่มmodelหรือFT ไม่มี3-modelbenchmark/trainingแฝงในขั้นintake
4. แยกrawlosslessmasksจากsimplifiededitingcopy เก็บnon-target/uncertainty/OSD/holes/componentsตามcontractไม่ตั้งignoreเพื่อแก้คะแนน
5. ตัดสินdomain/classrules/ownership/boxmatching/aggregationและตรวจactualpacket→scorer→reporterก่อนfreeze ขยาย300และ2,200เป็นbatchesที่ทบทวนได้ รักษาผลเก่า
6. ตามคำตอบผู้ใช้ fine-tunehelperเป็นplanneddevstageหลังseedที่ตรวจรับแล้ว ต้องจัดtrain/validationและresource/configbindingsก่อนรัน เก็บcheckpoint/annotationrevisionsและไม่ฝึกจากfinaltestที่ล็อกไว้

## คำตัดสินผู้ใช้ที่ได้รับระหว่าง review

| Decision | ผู้ใช้ตอบแล้ว | ผลต่อแผน |
| --- | --- | --- |
| MASTER-20261106-FT | ต้องการfine-tunehelperหลังได้seedที่ตรวจรับ | เปลี่ยนจากoptionalproposalเป็นplannedstage ต้องผ่านseed/tool/model/resource/configreadinessก่อน ไม่เริ่มtrainingในรอบอ่านแผน |
| MASTER-20261106-SIZE | คะแนนหลักเฉพาะคน≥50px โดยเก็บคนเล็กและสถานะยกเว้นไว้ | ใช้max(width,height)ของvisibleGTbboxเป็นscopeที่เลือกเอง ไม่ใช่กฎสากล ไม่ลบคนเล็ก ไม่ทำเป็นBG ต้องfreezeexcludedmatch/validdomain/thresholdก่อนscoring |
| MASTER-20261106-DET | เพิ่มbenchmarkYOLO26/11/v9/v8เป็นงานแยก | แยกdetectorstudyจากparser9ตัวที่ใช้frozenYOLO26x ไม่เปิด36combinations; task/รุ่นย่อย/checkpointsยังต้องระบุ |
| MASTER-20261106-SPLIT | กล้องเดิม คนละเหตุการณ์/ช่วงเวลาที่กันไว้ทดสอบ | seedครอบกล้องเดิมได้ แต่กันevent/timegroupsก่อนFT ไม่อ้างunseen-cameraและไม่สุ่มคนจากภาพเดียวกันข้ามชุด |

ขอบเขตGTที่34d2dd8ยังคงเดิม ไม่บังคับfull-personGT รายละเอียดtrainingarchitecture/seedmembership/Face/Dress/ignore/projectionยังไม่freeze การรับscopeสี่ข้อไม่รับรองกฎผิดในmasterplanทั้งหมดหรือทำให้modelsพร้อมรันทันที

**คำตอบเพิ่มเติมที่ได้รับแล้ว — MASTER-20261106-SPLIT:** finaltestหลักเป็น **future/held-out-event same-camera** คือกล้องเดิมแต่กันคนละเหตุการณ์/ช่วงเวลาไว้ทดสอบ ไม่อ้างunseen-cameraหรือunseen-person สามารถกระจายseedทุกกล้องได้เมื่อมีrecordsเพียงพอ แต่ต้องกันevent/timegroupsก่อนhelperfine-tuningและอธิบายtimestampprovenance ไม่รับรองindependenceจากdHashหรือgaptimeอย่างเดียว

**ข้อเสนอminimumในการดำเนินงาน:** ใช้pilot24เป็นsubsetของseedเป้าหมาย300 ไม่เพิ่มอีก24ภาพนอกpool เลือกgroupallocationก่อนfreezeรายชื่อseed; เลือกtrain/validationของhelperจากdevpoolเท่านั้น Freezehelper/policyก่อนfinaltestannotationที่เกี่ยวข้อง เก็บteacherstage/provenanceตามbatch และhuman-first/manualauditเพื่อเปิดเผยการชี้นำ

## Primary sources ที่ใช้ตรวจข้ออ้าง

- [CityPersons official evaluator](https://github.com/cvgroup-njust/CityPersons/blob/master/evaluation/eval_script/eval_MR_multisetup.py), Paramsและ_prepare: height/visibilityและignorematching ต่างจากlongestside50
- [NightOwls official examples](https://www.nightowls-dataset.org/examples/) และ [author paper](https://www.robots.ox.ac.uk/~vgg/publications/2018/Neumann18b/neumann18b.pdf): annotateheight>50และtask-specificignoredcontexts มีจริง ไม่ใช่หลักฐานว่าlongestside50เหมาะทุกCCTVtask
- [CrowdHuman official](https://www.crowdhuman.org/): head/visible/full-bodyboxesต่างชนิด ไม่รับรองvisibleboxpolicyอย่างเดียวเป็นกฎร่วมทุกdataset
- [SAM3 paper v2 §3](https://arxiv.org/html/2511.16719v2) และ [SAM3.1 release](https://github.com/facebookresearch/sam3/blob/main/RELEASE_SAM3p1.md): PE/DETR-likeและObjectMultiplexvideo; ไม่รับรองHiera/static4partheadหรือunbiasedGT
- [Co-DETR official model zoo](https://github.com/Sense-X/Co-DETR) และ [RF-DETR official table](https://github.com/roboflow/rf-detr): ตรวจรุ่น/split/AP ไม่ใช้APต่างtaskเป็นlocalCCTVwinner
- [SegFormer official](https://github.com/NVlabs/SegFormer): semanticsegmentationและtask-specificconfig/checkpoints ไม่ใช่pretrained4partlabelsโดยชื่อarchitecture
- [Sapiens2 official segmentation labels](https://github.com/facebookresearch/sapiens2/blob/main/docs/SEG.md): Apparel1,Left_Lower_Leg8,Face_Neck3; เทียบกับlocalpinnedCIHPmappingที่Dress6/Torso-skin10

Upstreammutablepagesเข้าถึง6พฤศจิกายน2026; localcode/manifestbindingsผูกprivateevidence ไม่โหลดmodelsหรืออ้างbitwiseparity/GTaccuracyจากread-onlyinspection ค้นเท่าที่พอปิดข้ออ้างในแผน ไม่ทบทวนliteratureทั้งโครงการ
