<a id="helper-training-revision2"></a>
## ฝึกตัวช่วยฉบับปรับปรุง — 12 พฤศจิกายน 2026

สถานะ **CPU_ACCEPTANCE_PASS / BATCH_READY_TO_LAUNCH** ผู้ใช้อนุญาตหยุด SAM3.1 รอบเดิมและให้เริ่มตัวที่เร็วกว่า จัดลำดับ SegFormer-B4 → SOLIDER → SAM3.1 ทีละตัวบน Tesla T4 เป้าหมายคือร่าง annotation ที่ผู้ใช้แก้น้อยลง

### สิ่งที่เก็บจากรอบเดิม

ส่ง SIGINT ให้ SAM3.1 PID4111696 หลังตรวจคำสั่งและเวลาเริ่ม process แล้ว ยืนยัน process ออกและ VRAM คืน เก็บ checkpoint ที่อ่านกลับได้จาก best epoch9 พร้อม log และเหตุผล `USER_INTERRUPTED_FOR_REVISED_HELPER_BATCH` ค่า mIoU_parts ของรอบเดิม 0.6041766173 เป็นค่าเฉลี่ยราย crop ตาม evaluator เดิม ส่วน B4 เดิมมี global mIoU4 0.6454162071 เก็บทั้งสอง checkpoint เป็นตัวเลือกต่อ พร้อมนิยามของแต่ละค่า

### วิธีฝึกที่จัดเตรียม

| ตัวช่วย | จุดเริ่มต้นและสิ่งที่ปรับ | งบรอบใหม่ |
| --- | --- | --- |
| SegFormer-B4 | เริ่มจาก helper ห้าคลาสที่ฝึกแล้ว ลด learning rate เพื่อปรับละเอียด เก็บ batch สุดท้ายและรองรับ batch ที่เป็น VOID ทั้งหมด ประเมิน epoch0 ก่อนฝึก | 15 epochs, batch2, AMP FP16, backbone LR2e-6 / head LR2e-5 |
| SOLIDER Swin-Small | โหลด pretrained LIP20 ตรงทุก key ใช้ BGR และ normalization ตาม local official extractor รวม logits เป็นห้ากลุ่มเพื่อเรียนรู้ GT ของงานนี้ คง running statistics ของ BatchNorm ระหว่างฝึก batch เล็ก | 25 epochs, batch2, AMP FP16, backbone LR1e-5 / head LR1e-4 |
| SAM3.1 | เริ่มจาก detector และ decoder best epoch9 เดิม ตรึง backbone เพิ่ม loss สำหรับคลาสที่ไม่มี, unmatched queries, query score และ presence ใช้ joint score ที่ builder สร้างแล้วหนึ่งครั้ง | 15 epochs, batch1, FP32, decoder LR3e-5 |

ค่าข้างต้นเป็น recipe เริ่มต้นที่ Codex เลือกสำหรับรอบปรับปรุง ยังไม่มีผลยืนยันว่าเป็นค่าที่ดีที่สุดในทุกทางเลือก ใช้ cosine learning-rate schedule, horizontal flip/ColorJitter สำหรับ B4/SOLIDER และ seed20261112 บันทึก flags จริงใน manifest แต่ละระบบ

SAM3.1 ใช้ forward ใน eval mode โดยเปิด autograd และฝึก parameters นอก backbone ด้วย objective ของ helper เอง เพราะ native training mode เรียก matcher/DAC ซึ่งต้องการ target contract อีกแบบ Feature cache ใหม่ผูก image/checkpoint/source/preprocessing กับ attempt และเก็บ positional encoding ร่วมเมื่อเทียบ tensor ได้ตรงกัน ไม่เปลี่ยน FP32 เพื่อประหยัด cache

SOLIDER แบ่ง native IDs ครบ20เป็น `Hair={2}`, `Face={13}`, `Upper={5,7}`, `Lower={9,12}` และกลุ่มอื่น `{0,1,3,4,6,8,10,11,14,15,16,17,18,19}` ใช้ logsumexp รวม logits การจับกลุ่มนี้เป็น output ของ helper ที่ฝึกกับ GT งานนี้ ต้องตรวจร่าง Dress/Jumpsuit ที่ยังผิดจริงจากตัวอย่างต่อ

### ข้อมูลและความหมายของผล

ใช้ seed300 ที่ผู้ใช้รับรองแล้ว มี313 train crops จาก213ภาพ และ77 validation crops จาก56ภาพ ตาม train240/validation60 ที่กัน time blocks ไว้ รายการ300ภาพและ390 masks ตรวจ freshness แล้วใน review ก่อนหน้า ชุด heldout440 และ Boost550 ยังพ้นการฝึกรอบนี้

ประเมินบน valid pixels ของ77 validation crops โดยข้าม GT255 รวม confusion ทั้งชุดก่อนคิด IoU ต่อ Hair/Face/Upper/Lower มี background เป็น negative สำหรับ FP ค่าเฉลี่ย mIoU4 ใช้คลาส foreground ที่ union มากกว่า0 คลาส union0 แสดง null พร้อมจำนวน support เก็บ TP/FP/FN, Precision, Recall และ F1/Dice ไว้ใน metrics ด้วย

- IoU = TP ÷ (TP+FP+FN) แสดงพื้นที่ทับ GT เทียบพื้นที่รวมที่เกี่ยวข้อง
- Precision = TP ÷ (TP+FP) แสดงความถูกต้องของพื้นที่ที่ร่างออกมา
- Recall = TP ÷ (TP+FN) แสดงส่วนของ GT ที่ร่างได้ครบ
- F1/Dice = 2TP ÷ (2TP+FP+FN) รวมความครบและพื้นที่เกินในค่าเดียว ตัวหาร0แสดง null

เลือก best epoch จาก diagnostic mIoU4 โดยรวม epoch0 และ export validation masks ให้ตรวจร่างจริง การเลือก helper ขั้นสุดท้ายยังต้องดูงานแก้ ขอบ mask, missing parts และ ownership ที่ภาพเดียวกัน ตอนนี้ยังไม่มีเวลาคนแก้ที่วัดจริงสำหรับประกาศผู้ชนะด้านความเร็ว annotation

### การทำงานอัตโนมัติและขอบเขตทรัพยากร

ใช้ [trainer](../scripts/train_annotation_helper.py) และ [ตัวควบคุมคิว](../scripts/run_helper_training_batch.py) เก็บ source snapshot, weights/config/source/input hashes, package inventory, launch commit และ attempt history ก่อนเปิด worker ใช้ fresh directories และ global batch lock แต่ละระบบมี log/status/weights ของตนเอง เมื่อ error จะหยุด batch และเก็บหลักฐาน automatic retry=0

งบที่กำหนดสำหรับ batch นี้คือไม่เกิน6ชั่วโมงต่อโมเดลและ output80GiBต่อโมเดล คง free-space guard50GiB ตรวจทุก30วินาที Admission ต้องมี free VRAMอย่างน้อย14GiBก่อนเริ่มแต่ละระบบ ค่านี้เป็น guard ที่เลือกสำหรับการรันทีละตัว ไม่ใช่ผลวัด memory requirement ของทุกโมเดล Runtime OOM ยังคงเป็นเหตุให้หยุดและตรวจหลักฐาน

เก็บ raw data, native annotations, source image IDs, cache และ validation masks ไว้ private ส่วน weights ใหม่อยู่ shared models ภายใต้ workspace เก็บ original dataset และผลเดิมครบ การฝึก helper ชุดนี้แยกจาก frozen parser benchmark และยังไม่เปลี่ยน GT definitions ของโครงการ

### หลักฐานก่อนเปิดงาน

CPU expected fixtures ตรวจ absent-target gradients, positive/negative query scores, VOID invariance, all-VOID finite loss, exhaustive native projection, BGR channel order, global confusion, joint-score handling และ controller sequencing/stop-on-failure แยกจาก GPU forward/backward ที่ต้องตรวจเมื่อเปิด worker โหลด B4 ห้าคลาสและ SOLIDER pretrained20 ด้วย CPU ผ่าน การตรวจข้อมูลก่อนเปิดงานผ่านครบสาม recipe และ CPU expected fixtures ผ่าน10 tests

Run และคำสั่งติดตามจริงจะระบุในสถานะล่าสุดหลังยืนยัน worker เริ่มแล้ว

---

ส่วนถัดไปเป็นประวัติ review ก่อนเริ่ม batch ฉบับปรับปรุง

<a id="helper-purpose-correction"></a>
## ปรับเป้าหมายเลือก helper ตามคำชี้แจงผู้ใช้ — 12 พฤศจิกายน2026

ผู้ใช้ต้องการตัวช่วยpseudo-labelingที่ทำให้แก้annotationน้อยลง การreviewก่อนหน้าของCodexให้น้ำหนักbenchmarkfairnessและcommonmetricเป็นเงื่อนไขมากเกินเป้าหมาย จึงแก้ข้อกำหนดที่sourceให้ใช้practicaldraftqualityและcorrectioneffortเป็นหลัก

| หัวข้อ | กติกาที่ใช้ต่อ |
| --- | --- |
| เป้าหมาย | ลดbbox/partsที่ต้องเพิ่ม ลบ แก้ขอบ วาดใหม่ และแก้owner พร้อมวัดเวลาคนเมื่อมีข้อมูลจริง |
| วิธีของhelper | ใช้prompt/crop/preprocessing/precision/postprocessที่เหมาะกับแต่ละตัวได้ รวมการเลือกhelperต่างตัวตามงาน/ส่วนเมื่อมีผลทดลองรองรับ |
| การเริ่มเลือก | ใช้savedoutputs/checkpointsและตัวอย่างdevelopmentที่มี เริ่มดูผลร่างที่นำไปแก้ในeditorได้จริง |
| Metrics | IoU/P/Rและmodelscoreใช้วิเคราะห์ข้อผิดพลาด ตัวเลขต่างสูตรแสดงนิยามกำกับ การคำนวณใหม่ทำเมื่อช่วยตอบคำถามที่จะเลือกhelper |
| Fine-tuning | ทำเมื่อผลร่างยังเพิ่มภาระแก้และการฝึกมีเหตุให้ช่วยได้ ภายในรอบ/budgetที่ตกลง ปัญหาaggregationของmetricอย่างเดียวไม่ทำให้weightsต้องฝึกใหม่ |
| GTและbenchmark | GTรับจากภาพและคนตรวจตามกฎคลาส/50px/ownershipของdataset Benchmarkparserหลักยังอ้างheldout/protocolของงานนั้น |

คำแนะนำเดิมที่ให้commonvalidation/retrainเป็นขั้นบังคับก่อนเลือกhelperให้ใช้เป้าหมายล่าสุดนี้แทน ข้อพบเรื่องloss/cache/source/runhistoryยังเป็นหลักฐานทางเทคนิคสำหรับการแก้ปัญหาที่เกี่ยวข้อง โดยเลือกทำให้ตรงประโยชน์ต่อการร่างจริง

จากsourceที่ตรวจ ตัวอย่างในsam31_testsสร้างด้วยSAM3.1zero-shot ส่วนSegFormercomparisonsใช้helperที่fine-tuneแล้ว ต้องติดป้ายให้ตรงกับweightsที่นำมาดู การเลือกคนละhelperต่อส่วนเป็นแนวทางที่อนุญาต ยังต้องดูร่างจริงก่อนสรุปว่าช่วยลดงาน และตอนนี้ยังไม่มีข้อมูลเวลาคนแก้ที่ใช้ประกาศผู้ชนะทั่วไปได้

แก้แผนไฟล์เดิม SHA256 `dea61f81a8b32528643975e2f9d9228fe8fc117789dd145b52fca815011db4b1` และคำสั่งทำงานในAGENTSให้ตรงเป้าหมาย อัปเดตreview/statusเดิม โดยเก็บผลฝึก/หลักฐานเก่าไว้ให้ตรวจต่อ

---

ส่วนถัดไปเป็นประวัติreviewตามเป้าหมายในแต่ละช่วง

<a id="helper-retrain-decision"></a>
## ต้องฝึก helper ใหม่ตัวใด — 12 พฤศจิกายน 2026

ตรวจloss/preprocessing/validationของB4เพิ่มเติมด้วยCPUexpectedfixturesและอ่านเส้นทางtrain/evalจริง ข้อสรุปแยกตามผลที่ตรวจ

| ระบบ | การดำเนินงานที่มีหลักฐานรองรับ |
| --- | --- |
| SegFormer-B4 | เก็บcheckpointเดิมเพื่อประเมินต่อ lossมีCE/DiceลงโทษFPของคลาสที่ไม่มีและmaskignoreถูกต้อง evaluatorใช้globalconfusion การตรวจครั้งนี้ยังไม่พบเหตุที่บังคับretraincheckpointเดิม |
| SAM3.1 | sourceปัจจุบันควรปรับobjectiveสำหรับabsent/unmatchedqueries/score supervisionและใช้commonvalidation ก่อนเปิดfreshtrainingattemptฉบับแก้เพื่อยืนยันการเรียนรู้ตามกติกาใหม่ ความตรงกันของsourceกับruntimeรอบปัจจุบันยังเป็นข้อจำกัดตามreviewก่อนหน้า |
| ทั้งสองระบบ | เก็บrun/source/config/input/checkpoint/environment/cachefingerprintsตั้งแต่launch ใช้freshattempt/logและvalidationdomain/aggregationที่ประกาศร่วมกันเพื่อตรวจเทียบ |

**B4ที่ตรวจเพิ่ม** กรณีGTbackgroundถูกต้องให้compositeloss0.01022014 แต่ทำนายHairบนbackgroundให้8.40786171 การเปลี่ยนlogitsเฉพาะพิกเซล255ไม่เปลี่ยนloss Globalconfusionนับmissedtargetและข้ามVOIDถูกต้อง Train/evalใช้ImageNetnormalizationชุดเดียวและvalidationไม่มีrandomaugmentation

**B4กรณีขอบที่ควรแก้ก่อนการฝึกครั้งถัดไป** เมื่อทั้งbatchเป็น255 CrossEntropymeanให้NaN ขณะที่Diceคืน0 ชุดปัจจุบันตรวจครบ313train+77valcropsแล้วพบall-VOID0ทั้งสองฝั่ง จึงเป็นการเพิ่มความทนทานสำหรับinputรุ่นถัดไป ผลนี้ไม่ได้ชี้ว่าการฝึกB4ที่จบแล้วมีNaNจากกรณีนี้

**Metricร่วมที่เสนอใช้ต่อ** globalper-targetTP/FP/FN→IoU/P/R/Dice บนvaliddomainเดียวและชุด77validationcropsที่ผูกhash ใช้ผลB4เดิมเมื่อbindingsและนิยามตรง ตรวจabsentclassesตามglobalunion การตรวจSAMเพิ่มต้องมีoutputcontractเรื่องqueryselection/overlap/thresholdที่กำหนดก่อนประเมิน ใช้GTเพื่อให้คะแนนและtrainingmatchingตามหน้าที่

เปลี่ยนvalidationสูตรใหม่มีผลต่อการเลือกcheckpoint ส่วนการเปลี่ยนtraininglossมีผลต่อweightsที่เรียนรู้ การพิจารณาretrainจึงอิงข้อผิดพลาดที่กระทบแต่ละระบบ เก็บattemptและผลเก่าทั้งหมดพร้อมข้อจำกัดที่ทราบ

---

ประวัติreviewก่อนหน้าด้านล่าง

<a id="training-review-20261112"></a>
## ตรวจคู่มือและงาน helper ที่เริ่มแล้ว — 12 พฤศจิกายน 2026

สถานะ **REVIEW_COMPLETE / TRAINING_ACTIVE / HELPER_SELECTION_METRICS_REQUIRE_REVISION** ตรวจcode/config/manifest/log/checkpointsจริงร่วมกับคำยืนยันผู้ใช้ว่าSeed300ตรวจแก้และรับรองครบแล้ว เก็บhuman confirmationผูกSHA256ของ300JSONในprivate evidence

### งานที่ทำแล้วและนำกลับมาใช้ได้

| รายการ | ผลตรวจ |
| --- | --- |
| Annotation | 300ไฟล์ มีbbox390/ignore95 ภาพ31ไฟล์ไม่มีbbox แยกเป็น13ignore-onlyและ18ไม่มีshapes |
| Train | 313personcrops จาก213ภาพในroleHELPER_TRAIN_INITIAL |
| Validation | 77personcrops จาก56ภาพในroleHELPER_VALIDATION_FIXED |
| Isolation | IDs/timegroupsข้ามtrain/valเท่ากับ0 ไม่มีheldoutเข้าtrain/val ขนาดbboxของcropที่ใช้ต่ำสุดtrain52/val51px |
| Freshness | สร้างexpectedmaskจากannotationปัจจุบันเพื่อเทียบsavedmask390cropsได้ตรงทุกพิกเซล source image bytesที่ใช้ตรงintake เก็บhashesและผลตรวจprivate |
| SegFormer-B4 | train25epochsจบ เวลา13.20นาทีตามlog bestepoch21 mIoU4จากglobalconfusion=64.5416207143% มีcheckpointและhistory |
| SAM3.1 | process4111696บนT4 ตั้ง15epochs lr1e-4 trainable32,745,270/frozen820,811,264 Logsnapshotที่ตรวจถึงepoch6/15 มีvalmetric49.75%ตามrun |
| Triage | รันCPUexpectedfixtures9กรณีผ่าน โค้ด/testsเป็นงานworkingtreeที่ยังไม่commit |

คำยืนยันhumanGTและการตรวจfreshnessตอบคนละส่วน ผู้ใช้รับรองsemanticGT ส่วนreplayเช็กว่าderivedtrainingmasksตรงannotationรุ่นที่ตรวจ การอ่านpreviewจริงสองคู่ช่วยตรวจตัวอย่างgeometryและความชัดในภาพ ยังไม่ขยายเป็นการรับรองpixelboundaryของทั้งชุดโดยผู้ตรวจคนที่สอง

### ประเด็นที่ต้องแก้ก่อนนำผลมาเลือก helper

| ความสำคัญ | หลักฐานที่พบ | ผลกระทบและงานที่ควรทำ |
| --- | --- | --- |
| MUST_FIXก่อนเทียบmetric | SAM3.1sourceปัจจุบันevaluate_sam31เฉลี่ยIoUรายcropและให้empty/empty=1 SegFormerใช้globalconfusionIoU | กำหนดcommonvaliddomain/aggregation/absentclassและoutputcontractก่อนประเมินเทียบ checkpointด้วยmetricเดียว |
| MUST_FIXในtrainingrevisionถัดไป | compute_part_lossให้loss0เมื่อtargetว่าง และpred_scoresไม่ได้ถูกใช้ในloss มีCPUfixtureยืนยัน | เพิ่มnegative/unmatched-query/score supervisionให้สัมพันธ์กับเส้นทางเลือกqueryด้วยscoreตอนinfer วัดFPและการตรวจส่วนที่ไม่มีด้วย |
| MUST_FIXprovenanceก่อนอ้างrunreproduction | SAM3.1processเริ่ม05:06:41UTC แต่sourcemtime05:09:24UTC มีเพียงไฟล์ปัจจุบันและlog | เก็บsource snapshot/hash/config/environment/inputbindingsตอนlaunchในfreshattempt ข้อค้นพบloss/metricที่ตรวจเป็นของsourceบนดิสก์ ยังผูกกับruntimecodeแน่ชัดไม่ได้ |
| MUST_FIXcacheidentityก่อนใช้cacheข้ามrevision | cache_featuresข้ามไฟล์ที่มีsample_id.ptอยู่แล้ว cachemetadataไม่มีimage/checkpoint/preprocesshash | เพิ่มfingerprintsและreconciliationก่อนreuse cachedfeatures ความเป็นfreshของsavedGTmaskยังไม่ยืนยันidentityของfeaturecache |
| MUST_FIXlauncherก่อนเปิดattemptถัดไป | train_helper.shมีtmuxkill-sessionแล้วnew-session และteeไปlogชื่อเดิม trainingเขียนbestcheckpointทับpathเดิม | ให้คำสั่งstartตรวจsessionที่มีอยู่และใช้freshattempt/log/checkpoints เก็บhistoryและbindingsของattemptปัจจุบัน |
| CONTROL_AND_REPORT | 31ภาพไม่เกิดpersoncrop จึงvalidationที่เกิดcropมาจาก56/60ภาพ ทั้งสองhelperใช้77cropsเดียวกัน | แสดงจำนวนภาพทั้งหมด/ภาพที่มีcrop/ignore-only/negativeและcropdenominatorชัด คะแนนอธิบายhelpervalidationบนGTpersoncrops |
| CONTROL_AND_REPORT | baselineFASHNในeval_helper_v1กำหนดDress4→Upper และclassifierinitializationเฉลี่ยtop/dress | ประกาศmappingของbaselineและแยกinitializationจากนิยามGT ปิดขอบDress/cross-zoneตามกฎโครงการก่อนอ้างcommonbenchmark |
| CONTROL_AND_REPORT | seedmanagerverifyปรับlabel/group_idด้วยgeometry และใช้49.5pxในQA ขณะที่เกณฑ์GTคือ50px | เก็บnormalizationdiff/receiptsและทำcutoffให้ตรงdeclaredGTpolicy สำหรับcroppingชุดที่ตรวจทุกbboxที่ใช้≥51px |
| CONTROL_AND_REPORT | materialize_pilot24_xanyใช้morphology/largestcontour/approximationกับmaskก่อนส่งeditor | เก็บrawและยืนยันlossless/editedGTreadbackตามหน้าที่ โครงสร้างQAในmanagerตรวจschema เจ้าของsemanticอ้างhumanreview |

### ตรวจสูตรและขอบเขตตัวเลข

บนval77crops มีGTว่างสำหรับHair16, Face40, Upper4, Lower9 crops SourceSAM3.1ปัจจุบันให้1เมื่อทั้งGT/predว่าง จึงมีน้ำหนักของcropที่ไม่มีคลาสนั้นอยู่ในค่าเฉลี่ย ตัวอย่างอิสระ2crops ที่cropแรกพลาดtargetทั้งหมดและcropสองว่างถูกต้อง จะได้sample-mean0.5 ขณะที่globalclassIoU0 ความต่างของ49.75%ในlogกับ64.54%จึงใช้จัดอันดับตรงกันไม่ได้จากสูตรที่ตรวจ

CPUfixtureของlossที่อ่านจากsourceปัจจุบัน ทำนายpositiveบนtargetว่างได้loss0และไม่มีmask/score gradient ส่วนtargetที่มีGTให้masklossแต่ไม่มีgradientเข้าตัวแปรpred_scores นี่เป็นหลักฐานobjectiveของsourceที่ตรวจ เก็บresultsและsourcehashesprivate ข้อจำกัดsource-at-launchยังคงตามตาราง

FASHNconfigจริงมี18classes sourceindicesface1/hair2/top3/dress4/skirt5/pants6ตรงโค้ดที่อ่าน การเฉลี่ยclassifierweightsเป็นการinitializationซึ่งต้องประเมินผลจากvalidationจริง ข้อความในคู่มือhelperที่รับประกันว่าเริ่มแล้วเก่งทันทีหรือแก้เร็วขึ้นควรแก้เป็นสิ่งที่วัดและรายงาน

### ลำดับทำต่อ

1. จัดเก็บattempt/source/input/checkpoint/cachebindingsของสิ่งที่มีให้ตรวจย้อนกลับ และประกาศความไม่แน่ชัดของruntimecodeรอบนี้
2. ทำcommonhelpervalidationกับsavedcheckpointsตามrouteและvaliddomainเดียวกันเมื่อถึงรอบประเมิน ตรวจpositive/absent/ignore/overlapด้วยexpectedcases
3. แก้loss/cache/launcherในrevisionใหม่ พร้อมfreshattemptและbudgetที่กำหนดก่อนฝึก
4. เลือกhelperด้วยvalidation60ภาพตามกติกาและรายงาน77crop/56imagepopulationจริง แล้วจึงขยายBoost550ตามแผน

ปรับคู่มือหลักเฉพาะสถานะล่าสุดและcanonicalignoreในข้อ4.1 SHA256 `d400c1265c1802877e58a9aaec2051ee19ef963f359752f4990669faf1259c0c` เก็บsnapshotก่อนแก้ คำสั่งและหลักฐานดิบอยู่private training-review run งานรอบนี้ตรวจCPU/metadata/source/logs

---

ประวัติreviewก่อนหน้าด้านล่าง

<a id="person-mask-workload"></a>
## ภาระตรวจรับ person mask — 10 พฤศจิกายน2026

ผู้ใช้ย้ำว่าperson maskทำให้มีงานเพิ่ม จึงยืนยันrequiredGTเป็นbbox/personID/4partsและสีตามที่ประเมินได้ Helper person maskเก็บอัตโนมัติพร้อมwarning ผู้ตรวจรับGTจากbbox/4partsที่ถูกต้องได้แม้helper maskยังผิดหรือoutside_person_pxยังเหลือ

แก้ข้อ4.1ให้outside-personเป็นwarningแยกและเปิดraw4partsเป็นฐานแก้ พร้อมแก้ประโยคเดิมในคู่มือที่เขียนว่าperson masksต้องแก้ตามกฎ การรับงานไม่เพิ่มreceiptหรือภาระเกลาขอบGTคนทั้งตัว ข้อกำหนดtriageและeditorbridgeยังรอตรวจimplementation พบไฟล์annotation_triage.py/testsเป็นงานค้างที่ยังไม่commit รักษาไฟล์เหล่านั้นไว้ตามเดิม

ปรับเฉพาะข้อ4.1ในmaster SHA256 `e66ee428e7d32aa7c53275778bb6bde8f02c59b5b76c8364caa1915308f090ca` ส่วนอื่นคงตามbeforebackup รอบนี้แก้ข้อกำหนด/คู่มือและตรวจdocumentconsistency

---

ประวัติreviewด้านล่าง

<a id="auto-triage-review"></a>
## ตรวจข้อ4.1 Auto-Triage — 10 พฤศจิกายน2026

สถานะ **TRIAGE_SPEC_REVIEW_1_PROPOSED / IMPLEMENTATION_PENDING** ตรวจแผนprivateไฟล์เดิมกับperson_pseudolabel.py, sam3_person_draft.py และlocalSAM3processor revision8330c45f4d47f62588122e462ac3eb7e0a2e6f46 เก็บbackupแล้วปรับเฉพาะข้อ4.1 ส่วนอื่นในแผนตรงกับก่อนแก้

| ประเด็นที่พบ | วิธีปรับข้อกำหนด |
| --- | --- |
| ตั้งAUTO-IGNOREจากกรอบโมเดลเล็ก | เก็บSMALL_CANDIDATEพร้อมraw/bboxแล้วให้คนยืนยันกรอบก่อนรับexcluded_under_50px ข้ามpartcallsชั่วคราวได้ตามbudgetและกติกาที่บันทึก |
| แหล่งbboxมีหลายชนิด | แยกmodel box/mask envelope/human-reviewed box เส้นตัดGTใช้กรอบที่มนุษย์ยืนยันในoriginalpixels กรณีstraddle50ขึ้นflag |
| score≥0.85ยังไม่มีหลักฐานcalibration | เก็บเป็นค่าร่างสำหรับtriageและแยกperson/part prompt score พร้อมrule revision SAM3scoreเป็นsigmoid(pred_logits)×sigmoid(presence_logit_dec)ตามsourceที่ตรวจ |
| BoxIoU0/conflict0/outside0ยังอาจคลาสผิดหรือพลาดคน | ทุกภาพต้องดูเต็มภาพและตรวจparts ก่อนบันทึกhumanreceipt NO_AUTO_FLAGSเป็นป้ายอัตโนมัติที่ระบุเงื่อนไขที่ผ่าน |
| no-proposal/emptyอาจหลุดจากall-passเงื่อนไขว่าง | จัดเข้าคิวneeds-review พร้อมreason เก็บabsence/unobservableแยกหลังมนุษย์ตรวจ |
| clipทำconflict/outsideหาย | วัดจากrawก่อนintersection/compose sourceปัจจุบันมีrawdiagnosticsแล้ว เก็บraw/ownedทั้งสองแบบ |
| หลายโฟลเดอร์เสี่ยงคนละrevision | ใช้views/manifestsอ้างsource/annotation revisionเดียว เก็บderivedexportเมื่อeditorจำเป็นและตรวจreadback |
| แก้bboxแล้วร่างเพิ่มอาจชนattempt/callbudget | สร้างlinkedattempt เก็บbox/source/rule hashes invalidateoldtriage คิดcallsเพิ่มตามbudget/failurepolicy |
| bbox JSONยังมีเฉพาะrectangle | part PNGมีraw/ownedครบ ต้องมีlossless editor bridgeและactualroundtripก่อนอ้างว่าแก้4partsจากexportได้ |

**Evidenceในcode** person_pseudolabel.pyมีmask_info/save_predictions/run_frame เก็บmodel-regressedboxแยกจากmask envelope, raw/ownedและdiagnosticsก่อนclip รวมbboxdescription ส่วนdriverบันทึกCALLSและมี--person-boxesแบบsource-bound แต่ยังไม่มีsize gating/คิวtriage ส่วนlocalprocessorในapp/models/sam3/model/sam3_image_processor.pyบรรทัด216–245นิยามscoresและmaskthresholdจริง

**เกณฑ์ตรวจถัดไป** expected49/50, small-draft→corrected≥50, missing/no-person, high-scorewrongclass, empty/absence, overlap/outsideก่อนclip, ownerwrong, staleflags/callbudgetและactualeditablepacketreadbackต้องตรวจตามrequirement รอบนี้เป็นreview/designของข้อ4.1 รันdocument/source checks ใช้หลักฐานCPUเดิม ไม่ได้วัดความเร็วหรือคุณภาพใหม่

แผนหลักไฟล์เดิมหลังปรับเฉพาะข้อ4.1 SHA256 `851480e6b7526e9fd145a5106246a68486bb451ffc21934850df9648eda5415c` headerrevision2.5ของแผนยังอยู่เดิม ส่วนข้อ4.1ระบุTRIAGE_SPEC_REVIEW_1_PROPOSEDพร้อมสถานะimplementationpending

---

ประวัติsplitและreviewก่อนหน้าด้านล่าง

<a id="balanced-split-complete"></a>
## ปรับ split และจัด helper memberships แล้ว — 10 พฤศจิกายน 2026

สถานะ **BALANCED_MEMBERSHIP_VERIFIED / GT_AND_EVENT_REVIEW_PENDING** ผู้ใช้อนุมัติปรับOuter Splitและhelperpartition รายชื่อรุ่นเดิมเป็นparentพร้อมhash/ผลต่าง รุ่นใหม่ใช้เป้า20%ต่อSiteพร้อมcamera/day-night/group representationตามกติกาmetadataในSUMMARYที่ประกาศก่อนมีผลคะแนน

| ส่วน | ภาพ | กล้อง |
| --- | --- | --- |
| Development รวม | 1,760 | 67 |
| Trainเริ่มต้นในDevelopment | 240 | 67 |
| Validationคงที่ในDevelopment | 60 | 46 |
| BoostในDevelopment | 550 | 39 |
| Developmentหลังfreeze | 910 | 32 |
| Heldouttestcandidate | 440 | 46 |

Pilot24อยู่train240ครบ พร้อมroles6calibration/6human-first/12workflowตามparent Seed300=train240+val60 รอบสองtrain790(240+550)/val60เดิม เลือกจากv1/v2ตามเกณฑ์validationก่อนฝึกแล้วfreezeก่อนร่าง910+440=1,350ภาพ GTที่ตรวจสะสมหลังBoostเท่ากับ850

| Site | ทั้งหมด | Testเดิม | Testใหม่ | Testใหม่ % | กลุ่ม Test | กล้อง Test |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S01 | 351 | 87 | 70 | 19.94 | 14 | 6 |
| S02 | 26 | 6 | 5 | 19.23 | 4 | 2 |
| S03 | 571 | 98 | 115 | 20.14 | 22 | 12 |
| S04 | 147 | 6 | 29 | 19.73 | 16 | 2 |
| S05 | 379 | 59 | 76 | 20.05 | 18 | 10 |
| S06 | 219 | 157 | 44 | 20.09 | 5 | 3 |
| S07 | 70 | 5 | 14 | 20.00 | 9 | 3 |
| S08 | 435 | 22 | 87 | 20.00 | 18 | 8 |
| S09 | 2 | 0 | 0 | 0.00 | 0 | 0 |

Site labelsเป็นนามแฝงเรียงคงที่สำหรับตารางนี้ ชื่อจริงอยู่private Siteที่แบ่งได้8แห่งมีTest19.23–20.14% Site09มี2ภาพในกลุ่มเดียวจึงอยู่development ปัญหาSite04/Site06เดิม4.08%/71.69%แก้เป็น19.73%/20.09%

**ผลแลกเปลี่ยน** Testcameraลด49เป็น46 (3กล้องอยู่development) และtimeblocksเพิ่ม27เป็น106 จากทั้งหมด463 ทุกกล้องในTestมีdevelopment กล้อง21แห่งอยู่developmentอย่างเดียว MetadataTest123day/317night

**Validation isolation** กันทั้ง21กลุ่มรวม206ภาพ คือval60และภาพร่วมกลุ่มอีก146ที่อยู่reserve910และพ้นtrain/Boost Pilot24และrolesอยู่train240ครบ จากparentมีouter716IDsและseed212IDsเปลี่ยน เก็บMEMBERSHIP_DIFF770แถวรวมการเปลี่ยนทั้งสองชนิด

**การตรวจจริง** Exact2,200uniqueIDsไม่มีขาด/ซ้ำ source/parent/pilot hashesและmetadataตรง ไม่มีsite-day/timeguard/hash-linkedgroupข้ามouter และไม่มีvalidationgroupร่วมtrainทั้งสองรอบ CPUexpectedcases9กรณีผ่าน รวมSitebalanceและvalidation siblingsห้ามเข้าBoost [สคริปต์](../scripts/prepare_annotation_split.py) และ [กรณีตรวจ](../tests/test_prepare_annotation_split.py)

**กติกาที่เลือก** DPเก็บmetadata-balancedsubsetต่อจำนวนภาพและรวมSites น้ำหนักsecondarycamera0.05/day-night0.1/groupcount0.02 และoverallcount4ถูกบันทึกก่อนคะแนน การค้นหานี้รายงานเป็นผลจากกติกาที่กำหนด เกณฑ์4h/dHash≤4เป็นข้อกำหนดของงานนี้ หากมีhash-linkedblockข้ามSiteจะหยุดทบทวนallocation ข้อมูลรุ่นนี้ไม่มีกรณีดังกล่าว

**ความพร้อมที่ยังต้องตรวจ** source-contextเรื่องclock/เหตุการณ์ยาว และvisualcoverageคน≥50px/การบดบัง/ความชัด/targetsupport รวมschema/ignore/editorroundtrip/GTacceptanceก่อนfinaltestfreeze ข้อ4.1Auto-Triageที่เพิ่งเพิ่มในแผนเก็บไว้ครบพร้อมสถานะimplementationpending

แผนหลักไฟล์เดิมrevision2.5 SHA256 `b9520610edcc1ce88761ca1e30cec70588fad6bcebb08ef638bb776112329408` เก็บรุ่นก่อนแก้พร้อมhashและสำเนาprivate รายชื่อจริงอยู่balanced split runที่CURRENT_ANNOTATION_SPLIT.txtอ้างถึง

---

ส่วนถัดไปเป็นประวัติreviewและsplitรุ่นก่อนหน้า

<a id="split-detail-review"></a>
## ตรวจข้อเสนอแบ่งข้อมูลอย่างละเอียด — 10 พฤศจิกายน 2026

สถานะ **REBALANCE_REQUIRED_BEFORE_FINAL_TEST_FREEZE / HELPER_PARTITION_PROPOSED** ตรวจแผนprivateล่าสุดrevision2.4และmembershipเดิมจากrun annotation-timeblock-split-20261110T065020Z คำว่าACCEPTEDในชื่อไฟล์เป็นข้อความต้นฉบับที่นำมาตรวจ รอบนี้ตรวจและเสนอรายละเอียดจากmetadata

**ข้อบกพร่องที่พบในsplitเดิม:** Heldout440อยู่ใน27จาก463กลุ่มเวลา แม้ครอบคลุม49กล้อง/8สถานที่ แต่สัดส่วนภาพtestต่อสถานที่ต่างกันมาก ตั้งแต่6/147(4.08%)ถึง157/219(71.69%) วิธีเลือกเดิมให้ความสำคัญกับcamera coverageและจำนวนรวมใกล้440 จึงเลือกกลุ่มขนาดใหญ่จนกระจุกสถานที่ ต้องจัดรายชื่อใหม่ก่อนfreeze โดยเก็บรายชื่อเก่าไว้เป็นparent ภาพรวม80/20เป็นค่าเริ่มต้นของงานที่Codexเลือก

**วิธีที่แนะนำ:** จัดกลุ่มเหตุการณ์/เวลาและhash-linkedgroupsก่อนแบ่ง จากนั้นตั้งเป้าheldoutประมาณ20%ภายในแต่ละสถานที่ที่แบ่งได้ ตรวจสัดส่วนday/nightและกล้อง พร้อมรักษาทั้งกลุ่มไว้ฝั่งเดียวกัน 18กล้องที่มีเพียงวันเดียวอยู่developmentตามขอบเขตsame-cameraheldout จำนวน440เป็นเป้าหมาย ให้รักษากลุ่มก่อนการบังคับยอดพอดี ต้องรายงานส่วนเบี่ยงเบนและจำนวนกลุ่ม/กล้อง/สถานที่จริง เกณฑ์4h/dHash≤4ของรายชื่อเดิมเป็นตัวกรองที่กำหนดในงานนี้ ส่วนclockคลาด/เหตุการณ์ยาวยังรอตรวจsourcecontext

| ส่วนที่เสนอ | ภาพ | บทบาท |
| --- | --- | --- |
| Helper trainเริ่มต้น | 240 | อยู่ในseed300 รวมpilot24ไว้ฝั่งtrain |
| Helper validationคงที่ | 60 | อยู่ในseed300 รักษาทั้งกลุ่มออกจากการฝึกทั้งสองรอบ |
| Boostสำหรับtrainรอบสอง | 550 | เลือกจากdevelopmentที่เหลือและพ้นทุกvalidationgroup ให้คนตรวจรับก่อนใช้ |
| Developmentหลังhelperfreeze | 910 | ร่างและคนตรวจรับภายหลัง รวมภาพอื่นของvalidationgroupsที่กันออกจากtraining |
| Heldouttest | 440เป้าหมาย | ผลประเมินหลักเมื่อGT/protocol/membershipตรวจรับ |

Pilot24เป็นsubsetของseed300 รอบแรกtrain240/val60 รอบสองtrain790/val60 รวมannotationที่ตรวจสะสม850ภาพ ข้อมูล1350ภาพหลังfreezeประกอบด้วยdevelopment910และheldout440 ผลรวม1350/2200รายงานประกอบพร้อมนิยามpopulation ผลหลักใช้heldoutที่ตรวจรับแล้ว กำหนดเกณฑ์เลือกhelperก่อนฝึก ใช้valชุดเดียวเลือกจากv1/v2และเก็บattempts ไม่ตั้งเงื่อนไขรับรองว่าv2ต้องแม่นกว่าหรือแก้เร็วกว่าโดยไม่มีผลวัด

**ตรวจความเป็นไปได้กับmembershipเดิม:** กันval60จาก8สถานที่/47กล้องได้ (metadata22day/38night) พร้อมรักษาseedtrain240ให้มีครบ67กล้องและpilot24อยู่ฝั่งtrain เมื่อกันทุกภาพในvalidationgroupsจะล็อกรวม159ภาพ คือval60และภาพนอกseedอีก99 ภาพ99นี้อยู่ฝั่งdevelopmentหลังfreezeและพ้นทั้งtrain/Boost มีnonseedcandidateที่พ้นvalidationgroupsเหลือ1361ภาพ เพียงพอเลือกBoost550 ตัวเลขนี้เป็นfeasibilityของรายชื่อเดิม ต้องคำนวณและตรวจใหม่เมื่อปรับouter split

**สิ่งที่metadataยังตอบไม่ได้:** personขนาด≥50px, targetvisibility/support, occlusion, blurและactualcolor/IRต้องดูภาพ/GT ไม่ใช้metadatacategoryแทนคลาสบุคคลหรือท่าทาง Helpervalidation60ครอบ8สถานที่/47กล้องตามตัวอย่างที่ตรวจ และการกันกลุ่มไม่รับรองidentityindependenceข้ามเวลา

**ขั้นถัดไปที่มีขอบเขต:** ปรับouterallocationให้กระจายสถานที่/ช่วงเวลา เก็บparent+diff → คัดseed/train/val/Boostด้วยเกณฑ์ที่ประกาศก่อนคะแนน → ตรวจsourcecontext/coverage/toolroundtripสำหรับpilot → ตรวจรับGT → ฝึกhelperตามbudgetที่กำหนด รายชื่อเดิมอยู่สถานะcandidateจนปิดข้อบกพร่องนี้

---

ประวัติการจัดทำsplitและแผนrevisionก่อนหน้าอยู่ด้านล่าง

# แผนที่ปรับแล้ว: อะไรเปลี่ยน และทำไม

อัปเดต 10 พฤศจิกายน 2026 (Asia/Bangkok) — **REVISION_2_3_PLAN_ACCEPTED_SPLIT_MATERIALIZED_NOT_EXECUTION_FROZEN**

ปรับไฟล์แผนหลัก private `PSEUDO_LABELING_MASTER_PLAN_2200_TH.md` ที่ผู้ใช้ส่งมาแล้ว โดยเก็บรุ่นก่อนแก้พร้อมhashไว้ภายนอกGit ไม่สร้างmasterplanอีกชุด รายงานหน้านี้เป็นคำอธิบายการแก้และเก็บreviewเดิม ไม่ใช่แผนคู่ขนาน

<a id="time-block-split"></a>
## จัดทำรายชื่อแบ่งข้อมูลแล้ว — 10 พฤศจิกายน 2026

| ชุด | จำนวนภาพ | กล้อง | สถานะ |
| --- | --- | --- | --- |
| Development | 1,760 | 67 | ฝั่งพัฒนา |
| Seedซึ่งอยู่ในDevelopment | 300 | 67 | รวมPilot24แล้ว รอannotationตรวจรับ |
| Pilotซึ่งอยู่ในSeed | 24 | 24 | 6calibration/6human-first/12workflowตามqueueเดิม |
| DevelopmentนอกSeed | 1,460 | — | สำรองฝั่งพัฒนา |
| Held-out test candidate | 440 | 49 | กันไว้ก่อนhelperFT รอsource-contexteventreviewก่อนfinalfreeze |

Codexใช้ค่าเริ่มต้น80/20, site+วันตามเวลาไทย, same-camera timeguard4ชั่วโมงข้ามเที่ยงคืน และsupplieddHash256bitsระยะไม่เกิน4ก่อนแบ่ง ได้463กลุ่มเวลา ทั้ง49กล้องในheldoutมีข้อมูลdevelopment ส่วน18กล้องอยู่developmentอย่างเดียว เกณฑ์เวลา/hashเป็นกติกาของงานนี้และต้องตรวจบริบทกรณีกำกวม

ตรวจexact2,200IDs ไม่มีขาด/ซ้ำ ไม่มีsite-day/timeblockหรือคู่dHash≤4ข้ามฝั่ง parentpilot/rolesและsourcebindingsตรงเดิม CPUacceptanceเฉพาะงานsplit6กรณีผ่าน รายชื่อ/metadata/pathsจริงและverificationอยู่private run; scriptที่ทำซ้ำได้อยู่ [prepare_annotation_split.py](../scripts/prepare_annotation_split.py)

การแบ่งตามmetadataยังไม่ยืนยันevent/identityindependenceหรือvisualcoverageของคน≥50px สถานะรายชื่อพร้อมเตรียมannotation ส่วนfinaltestfreeze/GTacceptance/helpertrainvalidationยังรอขั้นที่เกี่ยวข้อง ถัดไปตรวจcoverage/rule-criticalcasesและtoolroundtripสำหรับpilot24

<a id="plan-accepted"></a>
## ผู้ใช้รับรองแผนฉบับปรับแล้ว — 8 พฤศจิกายน 2026

คำยืนยัน “ที่เหลือผมว่าโอเคแล้วปรับเลย” รับข้อปรับและกฎเริ่มต้นที่ระบุในrevision2.1เป็นแผนทำงานแล้ว รวมscopeคน≥50px/ข้อมูลยกเว้นขั้นต่ำ, นิยาม4parts/สี/validity, เก็บmaskแบบไม่สูญเสียและprovenance, กันเหตุการณ์ก่อนhelperFT และpilot24ภายในseedเป้าหมาย300 ไม่ถามขอบเขตเดิมซ้ำ

| แผนรับรองแล้ว | ยังต้องทำและตรวจจริง |
| --- | --- |
| ขอบเขต/ลำดับงาน/กฎannotationเริ่มต้น/วิธีลดbiasและข้อจำกัดคำอ้าง | schema, mapping, shared pixel domainและignore matchingที่ยังไม่กำหนดครบ |
| helperFTหลังverifiedseed; helperเป็นร่าง คนตรวจรับทุกภาพ | exacthelper/checkpoint/source/environmentและtrainingbudget; ตัวเลือกโมเดลยังไม่ใช่คำสั่งเลือกทั้งหมด |
| กล้องเดิม คนละเหตุการณ์/ช่วงเวลา; pilot24อยู่ในseedประมาณ300 | membershipจัดทำแล้ว รอตรวจevent-context/visualcoverageและlossless editor roundtrip |
| ไม่ขยายpool/parts/โมเดล/รอบฝึก/เว็บเอง | actualpilot/GTacceptance/scoreracceptance/resource readiness; ไม่มีผลใหม่จากการรับรองแผน |

การตรวจpilotยังอาจพบกฎที่ต้องแก้ ให้เก็บก่อน–หลัง/เหตุผล/งานที่กระทบในrevisionกลาง ไม่ปรับจากคะแนนfinaltest **สถานะแผน:รับรองแล้ว; สถานะexecution:ยังไม่freeze/ยังไม่เริ่มในรอบนี้**

**เรื่องที่ตกลงกันยังเหมือนเดิม:** GT bbox+personID+4parts/validity; ไม่บังคับGTmaskคนทั้งตัว; คะแนนหลักคนด้านยาวvisibleGTbbox≥50pxแต่เก็บคนเล็กพร้อมสถานะ; fine-tunehelperหลังverifiedseed; detector4familiesเป็นงานแยก; finaltestเป็นกล้องเดิมคนละเหตุการณ์/ช่วงเวลา

| สิ่งที่ปรับ | ความหมายในงานจริง |
| --- | --- |
| คนเล็กนอกงานหลัก | คน<50pxเก็บข้อมูลยกเว้นขั้นต่ำ ไม่ต้องวาด4parts/สี/GTmaskทั้งตัวหรือไล่bboxละเอียด; ไม่ทำเป็นbackgroundอัตโนมัติ และต้องมีignorematchingที่ไม่ซ่อนคนใหญ่ |
| ปิดคำอ้างbias100% | ใช้คนตรวจรับและhuman-first6 เก็บร่างก่อน–หลัง ไม่ใช้ชื่อarchitectureรับรองความเป็นกลาง |
| เก็บรูปทรงGTให้ครบ | ไม่ลดทุกpolygonเหลือ10–25จุดหรือทิ้งชิ้นเล็กอัตโนมัติ แยกrawmasksจากสำเนาแก้ง่ายและตรวจอ่านกลับ |
| แยกกลุ่มข้อมูลก่อนfine-tune | กันevent/timegroupsก่อนเลือกseed ไม่ใช้ภาพเหตุการณ์เดียวกันปนtrain/validation/finaltest |
| คืนpilot24ก่อนseed300 | 24เป็นsubsetใน300 เพื่อพบปัญหาเครื่องมือ/กฎก่อนขยาย ไม่เพิ่มเป็น324 และไม่ฝึกจากdraftที่ยังไม่รับรอง |
| แก้รุ่นโมเดลและlabelIDs | ไม่เดาSAM3.1ว่าHiera ไม่รับรองSegFormerเป็น4parthead และแก้SapiensApparel1/Left_Lower_Leg8กับCIHPTorso-skin10ให้ตรงsource |
| สคริปต์วัดค่า คนยืนยันความหมาย | ขนาดไม่ใช่ระยะเมตร สว่าง/คม/สีเทาเป็นproxies ไม่ใช่IR/blur/occlusionGTโดยอัตโนมัติ |
| สีไม่เดาตามcategory | ไม่defaultUpper=shirt/Lower=pants ไม่ลบสีขาวเขียวเพื่อแก้OSDทุกจุด ไม่ใช้erosionเปลี่ยนGTgeometry และไม่ใช้ดำแทนunknown |

**ลำดับที่อ่านง่าย:** กันกลุ่มข้อมูล → ตรวจเครื่องมือ/กฎ → pilot24 → seedประมาณ300รวมpilot → fine-tunehelper → ช่วยร่างภาพถัดไปให้คนตรวจ → freezeและbenchmarkแต่ละงาน

**สิ่งที่ยังต้องทำจริง:** exacthelper/checkpoint/source/resource readiness, event/timegroup manifestและsplit membership, losslessdesktopeditroundtrip, ขอบคลาส/OTHER/validityและignorematching, trainingconfig/budget และ actualpacket→scorer→reporter ไม่ถือว่าแก้เอกสารแล้วงานเหล่านี้ผ่าน

แผนหลักปัจจุบัน revision2.3 มี202บรรทัด SHA256 `4856d9b34b6e168ba4f5794663838dc32c79552b52217d4a2568f387264a556d`; เก็บรุ่นก่อนแก้และhashไว้ในprivatebackupพร้อมประวัติreview การจัดทำsplitครั้งนี้ยังรอevent/visual/toolreadinessตามรายละเอียดข้างต้น

<a id="bounded-scope-50px"></a>
## ขอบเขตที่ทำจริง และไม่ขยายเอง — 8 พฤศจิกายน 2026

ผู้ใช้ย้ำว่าเอาคนตั้งแต่50pxขึ้นไปและต้องการลดงานนอกขอบเขต จึงปิดข้อความเดิมในคู่มือที่ว่า “ยังไม่มีhard minimum” ซึ่งเปิดช่องให้ต้องทำคนเล็กละเอียดเกินความจำเป็น

| ประเด็น | ขอบเขตที่ใช้ต่อ | สิ่งที่ไม่เพิ่มเอง |
| --- | --- | --- |
| คนในงานหลัก | `max(visible GT bbox width,height) ≥ 50` original px;49ไม่เข้า/50เข้า | ไม่กำหนดว่าทั้งสองด้านต้องถึง50 ไม่ใช้predictedbboxคัดGT |
| คนต่ำกว่า50 | บันทึกยกเว้นขั้นต่ำ; ถ้ามีbboxเดิมใช้ต่อ | ไม่ทำ4parts/สี/GTmaskทั้งตัว ไม่ไล่ขอบหรือbboxละเอียดทุกราย |
| งาน annotation | bbox+personID+4parts/validity; สีตามที่สังเกตได้ รูปแบบกลางรุ่นเดียว | ไม่เพิ่มparts ไม่บังคับGTmaskทั้งตัว ไม่เดาคำตอบของส่วนที่ไม่เห็น |
| จำนวนและลำดับ | pool2,200; pilot24อยู่ในseedเป้าหมาย300; helperFTหลังverifiedseed | ไม่เพิ่มpilot/โมเดลhelper/รอบฝึก/เว็บใหม่โดยพลการ; exactFTbudgetยังpending |
| การเปรียบเทียบ | detector4familiesแยกจากparser9/frozenYOLO26x | ไม่เพิ่มmatrix4×9 ไม่แก้ผลหรือprotocolเก่า |
| พบข้อกำกวม | พักเฉพาะเคส เก็บเหตุผล แก้กฎกลางเป็นversionเดียวและระบุงานที่กระทบ | ไม่สร้างกฎเฉพาะภาพ/โมเดลหรือวนตรวจทั้งชุดใหม่ |

**ยังไม่รับรองscorer:** coarse exclusionไม่ใช่GTmaskคนทั้งตัว และไม่ให้ignoreทุกpredictionที่แตะพื้นที่ ต้องปิดmatching/sharedpixel domainร่วมกันก่อนbenchmark ไม่ให้ignoreลบGTpartsของคนที่อยู่ในงานหลัก

**สิ่งถัดไป:** ปิดschema/validity/exclusion policyที่ค้างและการแก้–อ่านกลับไฟล์ให้ตรง แล้วpilot24ตามแผนเดิม ยังไม่เปิดpilot/training/inferenceจากงานเอกสารนี้

---

## ประวัติ review วันที่6พฤศจิกายน — อ้างไฟล์รุ่นก่อนปรับ

เนื้อหาต่อไปนี้เป็นหลักฐานว่าพบอะไรในรุ่นเก่า ข้อความว่า “ผู้ตรวจไม่แก้ต้นฉบับ” และตารางMUST_FIXเป็นสถานะในรอบreviewนั้น รอบวันที่8ได้แก้คำอธิบายในแผนแล้วตามสรุปด้านบน ส่วนreadiness/implementationที่ยังไม่ทำคงเป็นpendingตามจริง

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
