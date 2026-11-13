<a id="dense-helper-tuning"></a>
## จูน SOLIDER RGB → B5 → B4 — 13 พฤศจิกายน 2026

สถานะ **PREPARING / CPU_READY** ผู้ใช้อนุญาตให้เริ่มSOLIDERก่อนแล้วต่อB5/B4 ตามข้อเสนอสองสูตรต่อโมเดล รอบนี้เลือก **10epochsต่อสูตร รวม6trials** โดยทั้งAและBของแต่ละโมเดลเริ่มจากparentBESTเดียวกันอย่างอิสระ สูตรและรายชื่อคิวถูกตรึงก่อนGPUtraining

| ลำดับ | Trial | Parent BEST | LR backbone / head | Loss |
| --- | --- | --- | --- | --- |
| 1 | SOLIDER_RGB_A | SOLIDER_RGB epoch11 | 2e-6 / 2e-5 | CE + Dice เดิม |
| 2 | SOLIDER_RGB_B | SOLIDER_RGB epoch11 | 2e-6 / 2e-5 | weighted CE + Dice เดิม |
| 3 | B5_A | B5_finetuned epoch13 | 2e-6 / 2e-5 | CE + Dice เดิม |
| 4 | B5_B | B5_finetuned epoch13 | 2e-6 / 2e-5 | weighted CE + Dice เดิม |
| 5 | B4_A | B4_refined epoch12 | 1e-6 / 1e-5 | CE + Dice เดิม |
| 6 | B4_B | B4_refined epoch12 | 1e-6 / 1e-5 | weighted CE + Dice เดิม |

### สูตรและสิ่งที่วัด

- คงtrain313crops / validation77cropsจากseed300, batch2, AMPtrainingและFP32evaluation, AdamW/cosine10epochs, seed20261112, horizontalflip/ColorJitter0.2 ตามสูตรเดิม Inputของแต่ละarchitectureและmap-backคงตามparent
- สูตรBใช้weightsตามลำดับBG/OTHER, Hair, Face, Upper, Lower เป็น **1.0000 / 1.8058 / 2.7805 / 1.0000 / 1.0000** คำนวณจากTRAINpixelcountsด้วย `clip(sqrt(mean foreground TRAIN count / class TRAIN count),1,3)` และBG=1 ค่าเต็มอยู่ในprivate `TUNING_PROTOCOL.json`
- weightsเปลี่ยนCross-Entropyเฉพาะตอนฝึก Diceยังใช้สูตรเดิม ส่วนvalidationยังเป็นglobalconfusionและmeanIoUสี่คลาสแบบเดิม พร้อมP/R/F1/support/union GT255เป็นsharedVOID และGT0ยังvalidตามเดิม
- ทั้งสองสูตรเริ่มoptimizer/schedulerใหม่สำหรับtrialใหม่จากselectedparentweights โดยไม่รับผลAมาเป็นจุดเริ่มB Initialevaluationต้องได้confusionตรงacceptedparentก่อนเริ่มtraining มีepoch0เป็นcandidate จึงคงparentได้เมื่อสูตรใหม่ไม่เพิ่มคะแนน
- ใช้validationเลือกdevelopmentconfiguration หลังเห็นbaselineแล้ว ผลนี้ยังแยกจากheld-outtestและเวลาคนแก้ ไม่เปลี่ยนmapping/ignore/thresholdหรือinputresolutionตามpartialVAL

### Readiness และการกู้สถานะ

[Trainer](../scripts/train_annotation_helper.py) รองรับdensewarmstartแบบstrictfullstateแล้ว เพิ่มfull-state `LAST.pt` สำหรับdensemodelsรวมbackbone, optimizer, scheduler, **AMP GradScaler**, Python/NumPy/Torch/CUDA RNG และbeststate เมื่อจบแต่ละepoch มีsource/data/environment/configbindingchecksและworkerlock การกู้เริ่มจากepochที่จบล่าสุด งานค้างกลางepochอาจต้องทำซ้ำ

CPU30testsผ่าน รวมweightedCEที่เปลี่ยนเฉพาะCEและคงVOID, strictdensewarmstart/modelidentity, fullbackbone+AMPscalerrestoreที่ผลตรงuninterruptedCPUfixture รวมtestsเดิม โหลดactualselectedweightsครบสามarchitectureบนCPUแล้วได้tensorsตรงparentทุกค่า และinputpreflightผ่าน6/6 ยังไม่มีGPUimageforwardในreadiness

ใช้T4GPU0 / SHARED_GPU_QUALITY_ONLY / workerทีละตัว AdmissionfreeVRAM10GiB, freedisk50GiB, output80GiBต่อjob และตั้งงบtrialใหม่นี้ **30นาทีต่อjob** ไม่มีautomaticOOM/modelretry ผลเดิมและสภาพแวดล้อมเดิมยังอยู่ครบ

### คิวและรายงานอัตโนมัติ

Run `helper-dense-tuning-20261113T032600Z` อยู่privateใต้ `CCTV_Dataset_Development.local/runs/` คิวต่อA→BของSOLIDERก่อน แล้วB5A/BและB4A/B เมื่อครบหกtrialจึงสร้าง `REPORT_TH.md`, `COMPARISON.csv`, `RESULT_INDEX.json` และgalleryชุดเดิม [Reporter](../scripts/report_helper_comparison.py) ตรวจnewselectedmasks77IDsต่อtrialด้วยindependent `np.add.at` ก่อนรายงาน พร้อมเก็บsource/checkpoint hashes

`SELECTED_HELPERS.json` เลือกparent/A/Bรายfamilyด้วยvalidationmIoU4เต็ม หากเท่ากันคงparentที่อยู่ลำดับแรก ใช้ชื่อconfigurationและcheckpointจริงโดยเก็บทุกtrialไว้ หากยังไม่ครบไฟล์selectionเป็นPENDING_INCOMPLETE ผลparentเดิมยังใช้เป็นcandidateได้ตามรายงานก่อนหน้า

เปิดดูบนserverได้ด้วย

```bash
tmux attach -t helper_dense_tuning
```

หรือจากโฟลเดอร์repo

```bash
cd ../CCTV_Dataset_Development.local/runs/helper-dense-tuning-20261113T032600Z
python3 source_frozen/helper_training_progress.py --watch
```

ดูlogตามชื่อtrial เช่น `tail -f SOLIDER_RGB_A.log` หลังคิวจบตรวจ `REPORT_STATUS.json` และ `SELECTED_HELPERS.json` งานtrainingและartifactทั้งหมดแยกจากผลเดิม ส่วนรายงานผลเดิมด้านล่างคงไว้เป็นbaseline

---

<a id="sam31-fresh15"></a>
## SAM3.1 รอบใหม่จาก warmstart เดิม — 13 พฤศจิกายน 2026

สถานะ **COMPLETE / FULL15_VERIFIED / SAVED_MASK_AUDIT_PASS** ฝึกจบและสร้างรายงานเมื่อ **13 พฤศจิกายน 2026 เวลา 05:35 น. ไทย** ตรวจปิดจาก artifacts เมื่อ **09:28 น. ไทย** มีประวัติ epoch1–15 ครบ, optimizer updatesรวม4,695ครั้ง และ validation predictionsครบ77crops

### ผลหลัง fine-tune ล่าสุด

| Configuration | Hair IoU % | Face IoU % | Upper IoU % | Lower IoU % | mIoU4 % | Best epoch | ครบ | Mean ms/ROI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B4_refined | 74.24 | 46.65 | 77.36 | 62.89 | 65.29 | 12 | 77/77 | 88.15 |
| B5_finetuned | 75.04 | 51.73 | 77.28 | 64.59 | 67.16 | 13 | 77/77 | 114.08 |
| SOLIDER_BGR | 73.41 | 46.92 | 75.46 | 66.42 | 65.55 | 18 | 77/77 | 68.31 |
| SOLIDER_RGB | 71.98 | 51.94 | 77.93 | 68.97 | 67.70 | 11 | 77/77 | 70.82 |
| SAM31_warm_restarted | 74.29 | 54.79 | 80.11 | 63.98 | 68.29 | 6 | 77/77 | 2,758.56 |
| SAM31_fresh15 | 76.88 | 52.75 | 79.22 | 66.29 | 68.78 | 1 | 77/77 | 2,875.31 |

SAM3.1 รอบใหม่มี mIoU4 **68.78%** สูงกว่าผล warm restart เดิม **0.49 จุดเปอร์เซ็นต์** ค่า mean สูงสุดในกลุ่ม configuration หลังฝึกที่มีผลครบอยู่ที่รอบใหม่นี้ ส่วนคะแนนสูงสุดรายส่วนยังต่างกัน

| ส่วน | Configuration ที่ IoU สูงสุด | IoU % |
| --- | --- | --- |
| Hair | SAM31_fresh15 | 76.88 |
| Face | SAM31_warm_restarted | 54.79 |
| Upper | SAM31_warm_restarted | 80.11 |
| Lower | SOLIDER_RGB | 68.97 |

ตัวเลขใน [CSV รายคลาส](HELPER_COMPARISON.csv) มาจาก canonical metrics เต็ม พร้อม Precision/Recall/F1, GT/prediction support, union, source_run_id และ metrics/binding hashes ทั้ง10 configurations แยก ZERO_SHOT4 กับ FINE_TUNED6 ตาม stage ค่าเหล่านี้เป็น helper validation บน77 GT-person crops จาก56ภาพ การเลือก checkpoint ใช้ validation mIoU4 ส่วน held-out performance และเวลาคนแก้ annotation ยังรอการประเมิน

**Best epoch1 หมายถึงเลือกน้ำหนักจากรอบที่ validation สูงสุด** รอบนี้ยังฝึกจนถึงepoch15จริง โดย epoch15มีmIoU4 **61.80%** และคะแนนตลอด15epochsอยู่ระหว่าง **49.00–68.78%** จึงควรใช้ BEST.pt ที่เลือกไว้เมื่อจะตรวจร่าง หลักฐานแสดงว่าคะแนนแกว่งและการฝึกต่อไม่ได้เพิ่ม validation สูงสุดในรอบนี้ สาเหตุของการแกว่งยังยืนยันจาก records ชุดนี้ไม่ได้

### หลักฐานว่าฝึกครบและรักษาสถานะ optimizer

- `ATTEMPTS.jsonl` มีหนึ่ง attempt, resume=false, first_epoch1 และใช้workerPID619846เดียวกับตอนlaunch ประวัติepochเรียง1–15ครบ แต่ละepochมี313updatesและAMPskipped0
- `LAST.pt` อยู่epoch15, scheduler last_epoch15 และAdamWparameter statesทั้ง385รายการมีstep4,695 พารามิเตอร์และmoment tensorsที่ตรวจมีค่าจำกัดครบ ไม่มีnonfiniteในfullstateที่บันทึก
- `BEST.pt` ระบุepoch1และconfusionตรงกับhistoryepoch1 ส่วนbeststateที่ฝังในLASTตรงกับBESTทุกtensor SHA256ของBEST/LASTตรงstatusและrecoveryrecords มีRNG Python/NumPy/Torch/CUDAครบ
- Frozen trainer/controller/reporter/progress sourceตรงlaunchcommit `471b577c1406596de49ad653f18e30f31a81b908` ตรวจdataset manifest/membership identityและcanonical source hashesของทั้ง10configurationแล้ว
- ใช้automatic `SAVED_MASK_AUDIT.json` ที่ตรวจnewmasksด้วยindependent `np.add.at` ได้confusionตรงทุกcell, exact77IDs, missing0/invalid0 และcheckpointSHAตรง นำauditนี้กลับมาใช้โดยไม่รันscoring77ภาพซ้ำเพื่อเขียนรายงาน ตรวจarithmeticจากconfusionและmembershipเพิ่มเติมแล้ว
- Galleryยังเป็นสามvalidationcropsแรกตามกฎเดิม มีหกPNGแยกZERO_SHOT/FINE_TUNED ตรวจinput/output hashesครบ และเปิดดูFTแผงแรกกับแผงที่สามเพื่อดูชื่อโมเดล ตำแหน่งoverlayและlegend ผลนี้ใช้ภาพต้นฉบับกับGTชุดเดิม

หลักฐานอยู่ในprivate `FINAL_COMPLETION_AUDIT.json` และ `sam31/SAVED_MASK_AUDIT.json` ของrun `helper-sam31-fresh15-20261112T171624Z` ขณะตรวจไม่มีtrainingworkerหรือGPUcomputeprocessเหลือ การปิดรอบใช้CPUกับsavedartifactsทั้งหมดและมีmodel callsเพิ่ม0ครั้ง

### ข้อเสนอการใช้ helper จากผลนี้

ใช้ **SAM31_fresh15 / BEST epoch1** เป็นตัวเลือกหลักสำหรับตรวจร่างตามคะแนนเฉลี่ยสี่ส่วนและหลักฐานการฝึกต่อเนื่องที่ตรวจได้ครบ ผลเก่าSAMwarmrestartยังมีFace/Upperสูงกว่า และSOLIDER RGBมีLowerสูงกว่า จึงเก็บเป็นcandidateรายส่วนตามเป้าหมายลดภาระการแก้ การผสมoutputsหลายตัวและเวลาประหยัดที่ได้จริงยังต้องวัดกับdraftsที่นำไปแก้ การตรวจscoreนี้ไม่รับรองว่าภาพนอกvalidationทั้ง2,200ภาพจะได้คุณภาพเท่ากัน

### ความเร็ว inference ที่เพิ่มหลังปิดผลคุณภาพ

**Mean ms/ROI** ในตารางหลัง fine-tune เป็นเวลาเฉลี่ยในการสร้างmaskครบสี่ส่วนสำหรับ **person cropหนึ่งรายการ** เริ่มจากRGBcropที่decodeอยู่ในRAMแล้ว จบเมื่อได้hardmaskบนCPU หน่วยเป็นมิลลิวินาที ค่าน้อยหมายถึงใช้เวลาต่อcropน้อยภายใต้การวัดครั้งนี้ SAM31_fresh15ได้ **2,875.31ms ≈ 2.88วินาที/crop**

จับเวลาเป็นสามช่วงและรวมกันเป็นค่าในตาราง

1. เตรียมinputจากRGBในRAM รวมการแปลงtensor, resize512ของB5 และH2D transfer
2. Parser route รวมpreprocessingภายในโมเดล, forward, projection/union, resizeกลับ576×384และcomposeผลตามrecipeของแต่ละตัว
3. อ่านhardmaskกลับCPUและแปลงเป็นuint8

เวลาYOLO, การสร้างcropจากภาพใหญ่, การdecodeไฟล์, model loading, warmup, GT/scoring, การเขียนไฟล์ และการสกัดสีอยู่นอกช่วงนี้ ภาพต้นทางที่มีหลายคนจะมีหลายROI จำนวนROIและส่วนอื่นของระบบต้องวัดร่วมกันเมื่อต้องการเวลาpipelineต่อภาพ

### เงื่อนไขของการวัดใหม่

- ใช้ **Tesla T4, FP32, batch1, eval/no_grad** และselectedBESTweightsที่ผูกกับผลคุณภาพ มีGPUworkerทีละตัวตามลำดับ ใช้environmentและsourceของแต่ละconfigurationตามbindingเดิม
- เลือกสามvalidationcropsแรกตามชุดgalleryเดิม มีwarmupหนึ่งรอบสามcalls แล้ววัดสามรอบรวม **9 measured calls ต่อconfiguration** คำนวณmean/medianจากcallsทั้งเก้าด้วยfullprecisionก่อนปัดเศษ ใช้ `torch.cuda.synchronize` ที่ขอบช่วงและ `time.perf_counter`
- B4/B5หลังฝึกมีhelperheadห้าค่า SOLIDERสร้างnative20logitsแล้วgroupตามrecipe BGR/RGBของรอบนั้น SAM3.1คำนวณbackboneใหม่ทุกcropและทำdecoderครบสี่prompts เก็บfeaturesในGPUระหว่างcallsของcropเดียวกัน การวัดSAMรอบนี้มีencoderอยู่ในเวลาและไม่อ่านfeaturecacheจากรอบฝึก
- ตรวจpixel parityกับsavedselectedmasksทุกcallรวมwarmup ผ่านตรงทุกpixelบนสามcropsของทุกconfiguration ใช้ความเท่ากันของoutputsเพื่อตรวจroute โดยไม่มีGTช่วยสร้างหรือเลือกprediction คะแนนคุณภาพทั้ง77cropsยังมาจากcanonicalresultsเดิม
- ชุดtimingใช้สามcropsที่เตรียมไว้เดิม รวม72model-framecallsทั้งหกconfigurations การวัดนี้จัดทำหลังเห็นผลคุณภาพและfreezeprotocolก่อนวัดเวลา จึงเป็นsmall fixed-sample timing diagnostic ภายใต้resourcepolicy SHARED_GPU_QUALITY_ONLY
- `HISTORY.jsonl` เก็บเวลาtrainรวมvalidationต่อepochตามขอบเขตเดิม ส่วนคอลัมน์ใหม่นี้มาจากtimerinferenceเฉพาะที่เพิ่มขึ้น Median,จำนวนcallsและค่าเฉลี่ยสามช่วงอยู่ใน [CSV เดิม](HELPER_COMPARISON.csv)

Source [ตัววัด inference](../scripts/benchmark_helper_inference.py) ใช้frozenhelpers/checkpointbindingsที่ตรวจแล้ว CPU27testsผ่านรวมtimer units/phase boundaries, aggregationและSAMliveencoder/four-prompt composition Private run `helper-inference-timing-20261113T024908Z` เก็บ `TIMING_PROTOCOL.json`, `TIMING_INDEX.json`, LEDGERและMETRICSของแต่ละconfigurationพร้อมhashes Sourcecommit `ec0a95b5983e608216e9e0b6dc4ed3550843d355`

### Timing เดิมของ pretrained zero-shot

| Pretrained configuration | Mean native-route ms/ROI | N |
| --- | --- | --- |
| B4_native_zero | 80.71 | 77 |
| B5_native_zero | 110.94 | 77 |
| SOLIDER_native_zero | 159.23 | 77 |
| SAM31_native_zero | 2,872.97 | 77 |

ตารางzero-shotนี้สรุป `timing_seconds.native_route` จากmetadataครบ77cropsต่อโมเดล เป็นlegacyadapterdiagnosticsที่รวมfirstcallและมีsource-specificI/OภายในrouteของSOLIDER ใช้รหัส `LEGACY_NATIVE_ROUTE_77` ในCSV ส่วนผลFTใหม่ใช้ `FIXED3_WARM_FP32_FRESH_ROI` เพื่อระบุขอบเขตคนละชุดอย่างชัดเจน

### ประวัติยืนยันการเปิดงาน

ตรวจเมื่อ `2026-11-13T00:30:06.201571+07:00` งานอยู่epoch1/15ผ่าน20/313crops ใช้tmux `helper_sam31_fresh15` controllerPID619585/workerPID619846 แยกจากCodex ในช่วงนั้นLASTตั้งต้นอ่านกลับได้397decoderkeys, freshoptimizer/scheduler0 และRNGครบ RuntimebindingsตรงCPUpreflightและinitialconfusionบน77cropsตรงbaselineเดิมทุกcell บันทึกนี้เป็นsnapshotตอนเริ่มงาน

### สูตรที่เลือกก่อนเปิดงาน

| รายการ | เงื่อนไข |
| --- | --- |
| โมเดล | SAM3.1 Multiplex detector เดิม พร้อมฝึก decoder และคง backbone แบบ frozen |
| จุดเริ่ม | `sam31_warmstart.pt` ตั้งต้นของ batch เดิม SHA256 `5aeb67b165ef7c229331065442c206a82cd2e520fbcac2c464202ae730d08bbb` มี metadata epoch9 จากรอบก่อนหน้า |
| รอบใหม่ | 15 epochs เริ่ม optimizer และ cosine schedule จากตำแหน่ง 0 ของรอบใหม่นี้ |
| ข้อมูล | train313 crops / validation77 crops จาก seed300 ที่ตรวจรับแล้ว ใช้ split เดิม |
| Training | FP32, batch1, AdamW LR3e-5, weight decay1e-4, cosine15epochs, seed20261112, gradient clipping1.0 |
| Input / loss | RGB576×384 crop → float bilinear1008×1008 / normalize0.5 ตามสูตร helper เดิม ใช้ prompts/loss เดิมครบสี่ส่วน |
| Validation | global pixel confusion, IoU/P/R/F1 และ mIoU4 บน GT domain เดิม เลือก best รวม epoch0 ด้วย |
| ทรัพยากร | T4 GPU0, SHARED_GPU_QUALITY_ONLY, admission free VRAM10GiB, disk free50GiB, output80GiB และ6hต่อjobตามเดิม |
| Scope | ฝึก SAM3.1 หนึ่งตัว ใช้ผล helpers เดิมเพื่อออกรายงานเมื่อจบ |

การเริ่มใหม่นี้ใช้ warmstart ที่เคยเรียนรู้แล้ว และเริ่มนับ 15 epochs เพิ่มจากจุดนั้น Native pretrained zero-shot ยังคงเป็นผลอีก stage ในตารางเดิม การเลือก checkpoint ใช้ validation ซึ่งเป็นข้อมูลที่ใช้พัฒนา helper อยู่แล้ว

### การกู้สถานะที่เพิ่มในรอบนี้

[Trainer](../scripts/train_annotation_helper.py) เพิ่ม `--save-training-state` และ `--resume-training` สำหรับ SAM3.1 โดยเก็บ `LAST.pt` หลัง initial evaluation และเมื่อจบแต่ละ epoch ภายในมี model state, AdamW state, cosine scheduler, Python/NumPy/Torch/CUDA RNG, best weights/metrics และ binding hash ควบคู่กับ `BEST.pt` ที่ใช้เลือกผล validation

หากงานหยุด การเปิด controlled continuation สามารถกลับจาก epoch ที่จบล่าสุดได้ งานที่ทำค้างกลาง epoch ยังอาจต้องทำซ้ำจาก checkpoint นั้น `ATTEMPTS.jsonl` แยกการเปิด process แต่ละครั้ง `RECOVERY.json` บอก epoch/path/hash ล่าสุด มี worker lock ป้องกันการเปิดซ้ำ และตรวจ source/data/environment/config bindings ก่อนกู้สถานะ

CPU acceptance ผ่าน **24 tests** รวม tiny fixture ที่ผล weights และ RNG หลัง restore ตรงกับการฝึกต่อเนื่อง, การเรียก main ผ่าน interruption/resume จริงบน CPU, history reconciliation, binding mismatch และ saved-mask reporter ที่ปฏิเสธ confusion ผิด การทดสอบ CPU นี้ครอบคลุมกลไกกู้สถานะ ส่วนการประมวลผลบน T4 ตรวจหลัง launch

### Feature cache และการตรวจปิดอัตโนมัติ

อ่าน frozen-backbone features จาก parent แบบ read-only เพื่อประหยัดการคำนวณซ้ำ ตรวจ producer source, checkpoint/warmstart, model source และ data bindings แล้ว ตรวจ metadata ของ cache390ไฟล์ว่าตรง SHA ของภาพต้นทางและชนิด/รูปทรง tensors ตาม contract การตรวจครั้งนี้ไม่ได้ full rehash เนื้อหา cache41GiB ทั้งชุด Parent cache และผลเดิมยังอยู่ที่เดิม

เมื่อจบ worker ได้ประเมิน selected checkpoint และบันทึก masks ครบ77 crops แล้ว จากนั้น [reporter](../scripts/report_helper_comparison.py) คำนวณ confusion จาก saved masks ด้วย `np.add.at` ตรวจ exact IDs/labels/shape/GT hashes และ selected checkpoint SHA ก่อนออกรายงานรวม โดยอ่าน canonical metrics ของ configuration เดิมต่อ ผลใหม่ใช้ชื่อ `SAM31_fresh15` แยกจาก `SAM31_warm_restarted`

คิวมีหนึ่ง job และหยุดเมื่อจบ มีการเก็บ failures และ checkpoint ล่าสุด ไม่มี automatic model/OOM restart การกลับมาทำต่อหลัง interruption ต้องตรวจเหตุผล, full-state checkpoint และงบเวลาคงเหลือก่อนเปิด continuation

### ตำแหน่งและการติดตาม

Run `helper-sam31-fresh15-20261112T171624Z` เก็บ private ใต้ `CCTV_Dataset_Development.local/runs/` เปิดจากโฟลเดอร์ repo ด้วยคำสั่งนี้

```bash
cd ../CCTV_Dataset_Development.local/runs/helper-sam31-fresh15-20261112T171624Z
python3 source_frozen/helper_training_progress.py --watch
```

ดู log ด้วย `tail -f sam31.log` หรือ `tmux attach -t helper_sam31_fresh15` ซึ่งเปิดหน้าต่าง `progress` ที่แสดงสถานะสดให้แล้ว หน้าต่าง `runner` แยกไว้สำหรับตัวควบคุม การกด Ctrl+C ใน progress viewer หยุดเฉพาะตัวดูสถานะ เมื่อจบตรวจ `sam31/STATUS.json`, `sam31/SAVED_MASK_AUDIT.json` และ `REPORT_STATUS.json` ก่อนใช้รายงาน

| ไฟล์ | หน้าที่ |
| --- | --- |
| `BATCH_MANIFEST.json` / `LAUNCH.json` | สูตร/คำสั่ง/bindings และ process/session identifiers |
| `sam31/STATUS.json` / `HISTORY.jsonl` | สถานะจริงและผลแต่ละ epoch |
| `sam31/RECOVERY.json` / `ATTEMPTS.jsonl` | จุดกู้สถานะและประวัติเปิด process |
| `REPORT_STATUS.json` | สถานะการตรวจ saved masks และสร้างรายงานหลังฝึก |
| `REPORT_TH.md` / `COMPARISON.csv` / `gallery/index.html` | รายงานอัตโนมัติ ตารางเต็ม และภาพชุดเดิมเมื่อคิวจบ |

Weights อยู่ใน workspace หลักใต้ `models/human_parsing/cctv_helpers/helper-sam31-fresh15-20261112T171624Z/sam31/` ภาพ, masks, cache และ weights เก็บ private ส่วน source/configuration summary นี้อยู่ใน Git

---

> **ประวัติรอบก่อนเพิ่ม SAM31_fresh15** ตารางและข้อความด้านล่างบันทึกผลของกลุ่มที่ปิดก่อนหน้านี้ ผลปัจจุบันอยู่ในส่วน SAM3.1 รอบใหม่ข้างต้น

<a id="b5-and-zero-shot-completion"></a>
## ผลครบทั้ง zero-shot สี่โมเดลและ B5 fine-tune — 12 พฤศจิกายน 2026

สถานะ **COMPLETE / FINAL_SAVED_MASK_CHECK_PASS** งานจบเมื่อ **23:39:03 น. เวลาไทย** และตรวจปิดเมื่อ **23:45:26 น. เวลาไทย** บน Tesla T4 มีผล zero-shot สี่ configuration และผลหลัง fine-tune ห้า configuration ครบตัวละ 77 person crops B5 ฝึกครบ 25 epochs และเลือก checkpoint จาก epoch 13 ผล B4, SOLIDER BGR/RGB และ SAM3.1 หลังฝึกนำกลับมาจากรอบเดิมที่ตรวจรับแล้ว

เป้าหมายคือเลือกตัวช่วยร่าง annotation ที่มีคุณภาพและแก้ง่าย ใช้ train 313 crops จาก 213 ภาพ และ validation 77 crops จาก 56 ภาพ ภายใน seed 300 ภาพที่ผู้ใช้รับรองแล้ว ภาพ seed อีก 31 ภาพไม่มี person crop ตามกติกาสร้างข้อมูล การประเมินนี้ใช้กรอบคนจาก GT จึงครอบคลุมงาน parsing ของ helper บน crop ที่เตรียมไว้ การตรวจจับคนอัตโนมัติและผลทั้งชุด 2,200 ภาพยังเป็นขั้นถัดไป

### ก่อน fine-tune ด้วย CCTV Seed300

| Configuration | Hair IoU % | Face IoU % | Upper IoU % | Lower IoU % | mIoU4 % | Best epoch | ครบ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B4_native_zero | 46.54 | 29.83 | 48.96 | 38.81 | 41.03 | — | 77/77 |
| B5_native_zero | 30.99 | 29.70 | 55.74 | 33.67 | 37.52 | — | 77/77 |
| SOLIDER_native_zero | 57.89 | 47.02 | 69.61 | 57.31 | 57.96 | — | 77/77 |
| SAM31_native_zero | 50.83 | 37.77 | 64.93 | 3.58 | 39.28 | — | 77/77 |

SOLIDER Swin-Small ได้ IoU สูงสุดทั้งสี่ส่วนและ mIoU4 สูงสุด **57.96%** ในกลุ่ม pretrained ที่ทดสอบ สูตร input, native labels และ prompt ของแต่ละตัวถูกตรึงก่อนคำนวณคะแนนตาม [protocol ที่ใช้จริง](../config/helper_zero_shot_v1.json)

### หลัง fine-tune

| Configuration | Hair IoU % | Face IoU % | Upper IoU % | Lower IoU % | mIoU4 % | Best epoch | ครบ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B4_refined | 74.24 | 46.65 | 77.36 | 62.89 | 65.29 | 12 | 77/77 |
| B5_finetuned | 75.04 | 51.73 | 77.28 | 64.59 | 67.16 | 13 | 77/77 |
| SOLIDER_BGR | 73.41 | 46.92 | 75.46 | 66.42 | 65.55 | 18 | 77/77 |
| SOLIDER_RGB | 71.98 | 51.94 | 77.93 | 68.97 | 67.70 | 11 | 77/77 |
| SAM31_warm_restarted | 74.29 | 54.79 | 80.11 | 63.98 | 68.29 | 6 | 77/77 |

SAM3.1 มี mIoU4 สูงสุด **68.29%** สูงกว่า SOLIDER RGB **0.59 percentage points** และ B5 **1.13 percentage points** ส่วนคะแนนสูงสุดรายส่วนเป็นดังนี้

| ส่วน | Configuration | IoU % |
| --- | --- | --- |
| ผม | B5_finetuned | 75.04 |
| ใบหน้า | SAM31_warm_restarted | 54.79 |
| เสื้อผ้าส่วนบน | SAM31_warm_restarted | 80.11 |
| เสื้อผ้าส่วนล่าง | SOLIDER_RGB | 68.97 |

คำนวณค่าสูงสุดและส่วนต่างจากตัวเลขเต็มก่อนปัดเศษ SAM3.1 เป็นตัวเลือกหลักตามคุณภาพ mask โดยเฉลี่ยใน validation นี้ B5 และ SOLIDER RGB เป็นตัวเลือกสำหรับส่วนผมและส่วนล่างตามลำดับ การใช้หลายตัวร่วมกันยังต้องตรวจร่างและกติกาทับซ้อนเพิ่มเติม ตารางนี้ยังไม่มีผลของระบบผสมโมเดล เวลาที่ผู้ใช้ต้องใช้ตรวจแก้ยังไม่ได้วัด

### ตัวเลขวัดอะไรและคำนวณอย่างไร

รวมจำนวนพิกเซลจากทั้ง 77 crops เป็น confusion matrix แถวเป็น GT และคอลัมน์เป็น prediction มีห้าค่าคือ background/OTHER, Hair, Face, Upper, Lower เฉพาะ GT255 เป็น VOID และถูกข้ามเหมือนกันทุกโมเดล พื้นที่ GT0 ยังใช้คิดความผิดพลาด การทำนาย Hair บน GT0 จึงนับเป็น FP ของ Hair

สำหรับแต่ละส่วน TP คือพิกเซลที่ GT และ prediction ตรงกัน FP คือทำนายส่วนนั้นบน GT ส่วนอื่น FN คือ GT เป็นส่วนนั้นแต่โมเดลทำนายอย่างอื่น

- **IoU = TP / (TP + FP + FN)** วัดว่าพื้นที่ที่ทำนายตรงกับ GT มากเพียงใด โดยลงโทษทั้งส่วนเกินและส่วนที่ขาด
- **Precision = TP / (TP + FP)** วัดว่าส่วนที่โมเดลระบายมาเป็นส่วนนั้นจริงเท่าไร
- **Recall = TP / (TP + FN)** วัดว่าเก็บพื้นที่ GT ของส่วนนั้นมาได้ครบเท่าไร
- **F1 / Dice = 2TP / (2TP + FP + FN)** สรุปทั้งส่วนเกินและส่วนที่ขาดในสเกลเดียวกัน
- **mIoU4** คือค่าเฉลี่ย IoU ของ Hair, Face, Upper, Lower ที่คำนวณจาก confusion รวม ไม่นับ background ในค่าเฉลี่ย และไม่เฉลี่ยคะแนนแยกภาพ หากตัวหารของ metric เป็นศูนย์ให้คง null ตาม protocol ค่าเฉลี่ยใช้คลาสที่ union มากกว่าศูนย์ ซึ่งในรอบนี้ครบทั้งสี่คลาส
- **GT support / prediction support / union** คือจำนวนพิกเซล GT, จำนวนพิกเซลที่ทำนาย และจำนวนพิกเซลในพื้นที่รวมของคลาสนั้นตามลำดับ

ค่ารายคลาสเต็มทั้ง IoU, Precision, Recall, F1, support และ union อยู่ใน [ตาราง CSV พร้อม hashes ของ canonical metrics และ binding](HELPER_COMPARISON.csv) สูตรคำนวณอยู่ใน [ตัวประเมิน zero-shot](../scripts/evaluate_helper_zero_shot.py) และ [trainer](../scripts/train_annotation_helper.py) ค่าข้างต้นเป็น pixel metrics ของ helper validation ส่วนการเลือก checkpoint ใช้ validation mIoU4 จึงยังต้องแยกผลนี้จากการทดสอบ held-out

### เงื่อนไขที่ต้องอ่านประกอบคะแนน

- Zero-shot ใช้ pretrained weights ต้นฉบับก่อนฝึกด้วย CCTV พร้อม native head ของ B4/B5/SOLIDER หรือ native prompt detector ของ SAM3.1 แล้ว map เข้าสี่ส่วน Native classes นอกเป้าหมายเป็น OTHER ตามกฎคงที่ เก็บ native outputs แยกจาก common masks
- B5 เริ่มจาก native 18 classes แล้วสร้าง helper head ห้าค่า ใช้ Hair2, Face11, Upper4 และค่าเฉลี่ยน้ำหนัก Skirt5/Pants6 สำหรับ Lower ก่อนฝึก 25 epochs ด้วย AMP, batch 2, backbone LR 1e-5, head LR 1e-4, cosine และ seed 20261112 Input RGB 512×512 และ map logits กลับ 576×384 ค่า epoch 0 ของ head ที่สร้างใหม่เป็น initialization diagnostic
- SAM3.1 หลังฝึกใช้ custom float resize, single-query และ joint-score policy ส่วน pretrained zero-shot ใช้ native processor และหลาย query ตาม source จริง ดังนั้นผลต่างก่อน–หลังสะท้อนทั้ง weights และ adapter ที่ใช้ร่วมกัน
- SAM3.1 หลังฝึกมี warm restart ช่วง epoch labels 6–15 จาก best epoch 3 และเริ่ม AdamW ใหม่ ผลที่เลือกอยู่ epoch 6 หลักฐาน saved masks และ checkpoint ตรวจผ่าน แต่ไม่มี continuation launch-source hash และ starting checkpoint bytes แยกที่ยืนยันเส้นทางการฝึกช่วงต่อได้ครบ
- SOLIDER BGR และ RGB เป็นคนละ configuration ที่คงไว้ตามผลจริง Native Swin ใช้ RGB ส่วน BGR เป็น recipe ที่ฝึกและประเมินสอดคล้องกันภายในรอบของตัวเอง
- ชื่อ 5b ถูกตีความเป็น **SegFormer-B5** ตามบริบทก่อนหน้า มี native parameters 84,607,186 ตัว เวลาที่บันทึกเป็น diagnostics ตามขอบเขต adapter ของแต่ละตัว การทดสอบนี้ยังไม่มีการประเมิน statistical significance หรือเวลาคนแก้

### สิ่งที่ตรวจปิดและตำแหน่งผลจริง

Run `helper-zero4-b5ft-20261112T155416Z` ใช้ launch commit `e5d51692e2d56d0bf41547ce4e3da4975ae2d4ab` เปิดคิวแบบเรียงลำดับใน tmux `helper_zero4_b5ft` controller PID 551837 และ B5 worker PID 556837 จบแล้ว ขณะตรวจปิดไม่มี worker ฝึกเหลือ และ GPU ใช้หน่วยความจำประมาณ 3 MiB ประวัติเปิดงานและ snapshots อยู่ใน private run เดิม

- B5 มี saved predictions ตรงรายชื่อ validation 77 IDs ครบ ไม่มี missing หรือ invalid label/shape คำนวณ confusion ใหม่จาก saved masks ด้วย `np.add.at` ตรง canonical metrics ทุก cell
- B5 มี history epoch 1–25 ครบ รวม 3,925 optimizer updates และ AMP skipped updates 0 ตรวจ best epoch กับประวัติและ checkpoint SHA256 แล้ว ต้นฉบับโมเดลและผลเดิมยังอยู่
- ใช้ audit saved masks เดิมของ zero-shot ทั้งสี่ตัวและผล FT เก่าทั้งสี่ configuration ตรวจ arithmetic IoU/P/R/F1 และ GT support ของทั้งเก้าแถวตรงกัน ตรวจ hashes ของ canonical sources และ CSV full precision แล้ว
- ตรวจไฟล์ crop/GT ทั้ง 780 hashes ตรง data binding และตรวจ hashes ของ gallery inputs/PNGs ครบหกแผง เปิดดูแผง FT ของ crop แรกและ zero-shot ของ crop ที่สองเพื่อตรวจชื่อโมเดลกับตำแหน่ง overlay การตรวจภาพนี้เป็นการตรวจการแสดงผลและ geometry
- การตรวจปิดใช้ CPU และไฟล์เดิมทั้งหมด มี model-frame calls เพิ่ม 0 ครั้ง หลักฐานอยู่ใน `FINAL_COMPLETION_AUDIT.json` ของ run นี้

ผล private อยู่ใต้ `CCTV_Dataset_Development.local/runs/helper-zero4-b5ft-20261112T155416Z/` ซึ่งเป็นโฟลเดอร์ข้าง checkout นี้

| ไฟล์หรือโฟลเดอร์ | เปิดดูอะไร |
| --- | --- |
| `REPORT_TH.md` | รายงานอัตโนมัติจาก canonical results พร้อมสองตารางและผู้ได้คะแนนสูงสุด |
| `COMPARISON.csv` / `RESULT_INDEX.json` | ตัวเลขเต็มและ paths/hashes ของแหล่งผลแต่ละ configuration |
| `gallery/index.html` | ภาพเปรียบเทียบ crop เดียวกัน แยก pretrained กับ fine-tuned มีภาพต้นฉบับและ GT ทุกแผง |
| `gallery/MANIFEST.json` | provenance และ SHA256 ของภาพต้นทางกับภาพที่สร้าง |
| `b5_ft/` | history, binding, metrics และ validation predictions ของ B5 |

ภาพเลือกจากสาม validation crops แรกตามกฎเดิมก่อนดูคะแนน มีสองแผงต่อ crop รวมหกแผง สีผมเหลือง ใบหน้าฟ้า ส่วนบนแดง ส่วนล่างเขียว และ GT VOID สีเทา ภาพข้อมูลจริงเก็บ private

B5 checkpoint ที่เลือกอยู่ใน workspace หลักใต้ `models/human_parsing/cctv_helpers/helper-zero4-b5ft-20261112T155416Z/b5/BEST.pt` พร้อม `huggingface/` export ผลนี้พร้อมนำไปตรวจร่าง annotation ต่อ โดยต้องผูกการโหลด weights และการแปลง mask กลับภาพกับ configuration ที่เลือก

---

<a id="helper-training-complete"></a>
## ปิดรอบฝึก helper และตรวจผล — 12 พฤศจิกายน 2026

สถานะ **COMPLETE / SAVED_MASK_SCORING_VERIFIED** SAM3.1บันทึกผลจบเมื่อ21:30ไทย ตรวจปิดรอบจากartifactsภายหลัง พบB4/SOLIDERBGR/SOLIDERRGB/SAM3.1มีvalidation77cropsครบทุกตัว แยกประเมินสองrecipeของSOLIDER จึงเป็นสามโมเดล/สี่configuration ส่วนB5ยังไม่มีFTในbatchนี้

| Configuration | Hair IoU % | Face IoU % | Upper IoU % | Lower IoU % | mIoU4 % | Saved outputs |
| --- | --- | --- | --- | --- | --- | --- |
| B4 | 74.24 | 46.65 | 77.36 | 62.89 | 65.29 | 77/77 |
| SOLIDER_BGR | 73.41 | 46.92 | 75.46 | 66.42 | 65.55 | 77/77 |
| SOLIDER_RGB | 71.98 | 51.94 | 77.93 | 68.97 | 67.70 | 77/77 |
| SAM3.1 | 74.29 | 54.79 | 80.11 | 63.98 | 68.29 | 77/77 |

คะแนนเป็นhelper validationบน77GT-personcropsจาก56ภาพตามsplitเดิม ใช้input/outputrecipeของแต่ละตัวและGT255เดียวกัน เป้าหมายเลือกตัวช่วยจากร่างจริงและภาระแก้ ตารางนี้แยกจากpurezero-shotที่ผู้ใช้ขอ ซึ่งยังมีผลขาด โดยเฉพาะB5และSAMpretrainedครบ77crops

### สิ่งที่ตรวจปิดจริง

- คำนวณconfusionจากsavedhardmasksครบ77cropsต่อconfigurationด้วยnp.add.atได้ตรงMETRICSทุกcell ตรวจlabels/dimensions/exactmembership ไม่มีmissing/invalidexport IoU/TP/FP/FN/P/R/F1ตรงสูตรและcheckpointSHAตรงcompletion
- ตรวจmanifestและcrop/image/mask780hashesยังตรงbindingเดิม เก็บprivateclosureevidenceในrunเดิมใต้final_closure_20261112 และเชื่อมmetricspath/hashทุกconfiguration
- ขณะตรวจไม่มีtrainingGPUworkerเหลือ ParentSTATUSเคยค้างTRAINING แก้เป็นderivedCOMPLETEจากหลักฐานโดยเก็บSTATUS_BEFOREและappendCOMPLETION_RECONCILED ไม่เขียนทับscientificconfig/BINDINGเดิม

### ประวัติ SAM3.1 ที่ต้องกำกับ

ภายหลังการพักในmemoryที่ตรวจไว้ก่อนหน้า พบcontrollerเดิมรับSIGINTและworkerรับSIGTERMตามtraceback แล้วมีresume_sam31_training.pyกับworkerPID389286มาฝึกช่วงepochlabels6–15ต่อ LogระบุโหลดBESTจากepoch3 mIoU67.82% เริ่มAdamWใหม่ เลื่อนcosineschedule5steps และreseedตามepoch ประวัติHISTORYมีlabels1–15ครบ แต่trajectoryไม่ได้เก็บoptimizerต่อเนื่องตลอดทั้งรอบ ต้องเรียกผลนี้ว่าwarm-restartedhelperconfiguration

Sourceปัจจุบันของcontinuationมีprompt_lossASTตรงoriginalหลังตัดdocstring และevaluatorใช้globalconfusion/query/thresholdpolicyเดิม Sourcehashตรวจหลังrunแล้ว แต่ไม่มีlaunchsourcehashของcontinuationและไม่ได้เก็บbytesของBESTที่โหลดก่อนถูกอัปเดตเป็นbestepoch6 จึงมีข้อจำกัดprovenanceช่วงเริ่มต่อ เก็บCONTINUATION_RECONCILIATIONแยกจากBINDINGของoriginalsegment คะแนนfinal77masksตรวจได้ครบตามข้างต้น

งานปรับเพดาน8hยังไม่ได้launchก่อนกลับมาตรวจพบcompletionผ่านcontinuationแล้ว จึงเก็บdraftตัวคุมที่ไม่ได้ใช้ไว้ในprivateclosureและปิดสถานะตามactualrecords ไม่อ้างว่าเคยเปลี่ยนcapหรือรักษาoptimizerตลอดช่วงcontinuationนี้

ผลทั้งหมดพร้อมดูrasterdraftsและตรวจnewweight→editor/polygonexportต่อ ยังไม่มีเวลาผู้ใช้แก้จริงเพื่อรับรองว่าconfigurationที่IoUสูงสุดลดภาระแก้ได้มากที่สุด

---

<a id="clasp-candidate-review"></a>
## CLASP จาก paper ที่ผู้ใช้เสนอ — 12 พฤศจิกายน 2026

สถานะ **PAPER_REVIEWED / RELEASE_UNVERIFIED / PROPOSED_HELPER_CANDIDATE** อ่านarXiv2601.13133v1และค้นreleaseแบบเจาะจง งานเสนอDINO+CLIPsemanticpseudolabelsและPrompt-ControlledMoEสำหรับhuman-centricpretraining ส่วนhumanparsingใช้CLASPbackboneร่วมกับSCHPและฝึกdownstreamบนLIP [ต้นฉบับและวิธีทดลอง](https://arxiv.org/html/2601.13133v1#S4)

TableVIIIรายงานCLASP(SCHP)Swin-T59.31/Swin-S60.93/Swin-B61.74 เทียบSOLIDERSwin-B60.50 บนLIP ตัวบทระบุmetricparsingเป็นmIoU แต่หัวคอลัมน์TableVIIIพิมพ์mA จึงบันทึกความคลาดเคลื่อนนี้ไว้ คะแนนเหล่านี้ยังไม่ตอบeditingburdenหรือfour-targetCCTVvalidationของเรา [TableVIII](https://arxiv.org/html/2601.13133v1#S4.T8)

ข้อเสนอคือเก็บเป็นcandidateที่น่าลองเมื่อมีsource/weightsพร้อม ค้นรอบนี้ยังไม่พบofficialimplementation/checkpointที่ยืนยันได้ ต้องแยกpretrainedbackboneกับparsingcheckpointที่มีheadพร้อม และตรวจPC-MoE/config/normalization/nativeclasscontractก่อนโหลด การนำCLASPไปใส่SOLIDERloaderเดิมต้องมีหลักฐานความเข้ากันได้

ทางที่คุ้มกับงานปัจจุบันคือเริ่มจากparsingcheckpointที่ผู้เขียนฝึกไว้แล้วเพื่อดูร่างบนfixeddevelopmentcrops แล้วปรับวิธีหรือfine-tuneSeed300เมื่อมีเหตุรองรับ การใช้pretrainingrecipeทั้งหมดต้องใช้ทรัพยากรอีกขอบเขต ขณะนี้ยังไม่มีmodelcall, dependencyinstallation, weightsdownload หรือT4memorymeasurementของCLASP

---

<a id="solider-rgb-interleave"></a>
## พัก SAM3.1 เพื่อดู SOLIDER RGB ก่อน — 12 พฤศจิกายน 2026

สถานะ **SAM_PAUSED_IN_MEMORY / SOLIDER_RGB_TRAINING** ผู้ใช้ขอพักSAM3.1และกลับมาฝึกต่อเพื่อดูSOLIDER BGR/RGBก่อน ใช้วิธีSIGSTOP/SIGCONTค้างprocessและCUDAcontextเดิมไว้ในหน่วยความจำ จึงเก็บoptimizer/RNG/ตำแหน่งฝึกปัจจุบันไว้ได้ การrestartserverหรือสูญเสียprocessทำให้สถานะในหน่วยความจำนี้หาย เพราะtrainerเดิมยังไม่มีfulloptimizerresumecheckpointบนดิสก์

เตรียม [ตัวควบคุมพัก/กลับมาทำต่อ](../scripts/interleave_helper_training.py) ตรวจPID/startticks/commandก่อนส่งsignal พักเฉพาะSAMworkerและcontrollerที่เป็นของbatchนี้ หลังRGBสำเร็จหรือerrorให้resumeทั้งสอง มีwatchdogแยกเฝ้าsupervisorและเพดานพัก1ชั่วโมง พร้อมmanualresumecommandที่ใช้identitychecksเดียวกัน ไม่เพิ่มautomaticmodel/OOMretry

Resource amendmentของRGBรอบนี้คือ**PAUSED_SAM_SHARED_RESIDENCY** SAMยังจองVRAMประมาณ7.6GB ส่วนfreeที่ตรวจ7,279MiB รอบSOLIDERเดิมมีpeakallocated2,618,966,016bytes เลือกguardfreeVRAM5GiBก่อนเริ่มRGBเพื่อรวมheadroom ส่วน50GiBfreediskและ80GiBoutputcapคงตามเดิม หากguardไม่ผ่านให้resumeSAMและเก็บเหตุผล การมีVRAMตามguardยังไม่รับประกันว่าจะรันทุกstepได้

RGBใช้pretrainedSwin-Smallต้นฉบับ GT/seed/313train+77val/groupedlogits/loss/LR/batch/AMP/25epochsตามBGRrecipe เปลี่ยนinputเป็นRGB/normalizationตามmodelพร้อมguardsที่แก้แล้ว Source/output/weights/logsแยกfreshlinkedrun เมื่อจบตรวจ77savedmasksเทียบGTและcanonicalconfusionแล้วสร้างREPORT_TH.mdเปรียบเทียบBGR/RGBในprivate run คะแนนใช้ดูcandidatehelperตามเป้าหมายการแก้ร่าง

เวลาพักถูกบันทึกแยก แต่controllerเดิมมี6hwallcapซึ่งนับเวลาพักด้วย ไม่มีการขยายcapเดิมเงียบๆ EpochsecondsของSAMที่คร่อมช่วงพักมีเวลารอรวมอยู่ ต้องติดป้ายในการนำไปวิเคราะห์เวลา ตัวดูprogressเดิมเพิ่มPAUSED_IN_MEMORYจากstateจริงของprocess

CPUsubprocessfixturesผ่าน3testsครอบคลุมidentitymismatch, success/failurecleanup และwatchdogresumeเมื่อsupervisorหาย ตรวจการสร้างcomparisonreportกับsaved-maskconfusionในtinyfixturesด้วย

ยืนยันlaunchเมื่อ `2026-11-12T16:52:53.838276+07:00` Run `helper-solider-rgb-interleave-20261112T094846Z` ใช้launchcommit `852a61f3d509a9555d319bd3e20dd1ce1007fc4e` tmux `helper_solider_rgb` supervisorPID271857/watchdogPID271890/RGBworkerPID271958 Source/input/config/weightsbindingsและCPUinputpreflightผ่าน RGBมีEFFECTIVE_INPUT_OUTPUT_CONTRACTที่ยืนยันRGB/mean/stdและผ่านtraining100/157batchesของepoch1แล้ว GPUobservationSAM7630MiBค้างและSOLIDER2702MiBกำลังฝึก

SAMworkerPID123721 และcontrollerPID71234เป็นstateTจริง สถานะที่บันทึกก่อนพักอยู่epoch4/15 โดยworkerมีRNG/optimizerเดิมในmemory ตัวดูprogressจะแสดงPAUSED_IN_MEMORY

ดูงานRGBบนserverได้ดังนี้

```bash
cd /home/skyaidev/folk/CCTV_Dataset_Development.local/runs/helper-solider-rgb-interleave-20261112T094846Z
python3 /home/skyaidev/folk/CCTV_Dataset_Development/scripts/helper_training_progress.py --watch
```

เมื่อRGBจบจะสร้างREPORT_TH.mdและRGB_SAVED_MASK_AUDIT.jsonในrunนี้ แล้วมีRESUMED.jsonบันทึกการกลับมาทำต่อของparent ProgressSAMใช้คำสั่งเดิมกับparentrunได้ หากต้องยกเลิกRGBและresumeSAMก่อน ให้ใช้controlledresumeที่ตรวจidentityด้วยคำสั่งนี้

```bash
/home/skyaidev/folk/Human-Body-Extraction/.venv/bin/python /home/skyaidev/folk/CCTV_Dataset_Development.local/runs/helper-solider-rgb-interleave-20261112T094846Z/source_frozen/interleave_helper_training.py /home/skyaidev/folk/CCTV_Dataset_Development.local/runs/helper-solider-rgb-interleave-20261112T094846Z/BATCH_MANIFEST.json --resume
```

คำสั่งresumeจะหยุดเฉพาะRGBworkerของattemptนี้ก่อนปล่อยSAMกลับ ไม่ส่งsignalให้processงานอื่น

---

<a id="helper-practical-selection-reaffirmed"></a>
## ยืนยันเป้าหมายเลือกตัวช่วย annotation — 12 พฤศจิกายน 2026

ผู้ใช้ยืนยันว่าเป้าหมายคือร่างpseudo-labelที่ดีที่สุดและแก้ง่ายที่สุด อนุญาตให้ปรับวิธีของแต่ละโมเดลให้เหมาะกับตัวเอง เลือกคนละhelperต่อส่วนหรือผสมเทคนิคได้เมื่อมีผลร่างจริงรองรับ การเทียบแบบarchitecture-fair/native-reproductionไม่ใช่เงื่อนไขก่อนใช้งานhelper

Codexทำข้อสรุปให้freshRGBtrainingของSOLIDERดูเป็นขั้นบังคับเกินเป้าหมาย ต้องปรับเป็นทางเลือกพัฒนา ผลBGRที่ฝึกแล้วเป็นcandidateที่ใช้ประเมินร่างจริงได้ พร้อมระบุrecipeตามจริง ข้อผิดพลาดที่อ้างว่าBGRเป็นnativeSwinยังคงต้องแก้ด้านprovenance แต่ผลจากการฝึกและประเมินด้วยBGRที่สอดคล้องกันไม่ถูกตัดออกเพียงเพราะต่างจากupstream

| การตัดสินใจ | แนวทางปัจจุบัน |
| --- | --- |
| ใช้สิ่งที่มี | B4/SOLIDERที่ฝึกแล้วและSAM3.1เมื่อจบเป็นตัวเลือกหลัก ดูภาพเดียวกันและไฟล์draftที่แก้ได้จริง |
| เลือกตัวช่วย | พิจารณาmissing parts, พื้นที่เกิน, ขอบmask, ownership, จำนวนส่วนที่ต้องวาดใหม่ และภาระการแก้ ใช้IoU/P/R/F1ประกอบ |
| การปรับปรุง | ปรับpreprocessing/prompts/postprocessing/precisionหรือfine-tuneเฉพาะเมื่อมีเหตุว่าจะลดปัญหาร่างที่พบ บันทึกrecipeและผลก่อนหลัง |
| SOLIDERRGB | เป็นcandidate recipeเพิ่มเติม ไม่เป็นgateก่อนประเมินBGRhelperที่มีอยู่ |
| Zero-shot | จัดแสดงผลก่อนCCTVfine-tuneตามที่ผู้ใช้ขอ แยกน้ำหนักที่ใช้จริงและความครบถ้วน การรอครบตารางzero-shotไม่ใช่gateบังคับก่อนดูhelperที่ฝึกแล้ว |
| การผสมวิธี | เลือกโมเดลต่อHair/Face/Upper/Lowerหรือใช้auxiliaryขั้นแก้ได้เมื่อทดสอบแล้ว เก็บวิธีresolveoverlap/ownershipให้ชัด |
| สิ่งที่คงต้องถูกต้อง | GTตามภาพจริง, IDs/geometry, การโหลดweightsที่เลือก, savedoutputsและรายงานที่อ้างrecipeถูกต้อง |

ยังไม่มีเวลาผู้ใช้แก้ที่วัดจริง จึงยังประกาศผู้ชนะด้านลดเวลาไม่ได้ CurrentSAM3.1trainingทำต่อ ส่วนการเปรียบเทียบfine-tuneและการผสมวิธีรอผลพร้อมตามลำดับที่ผู้ใช้กำหนด ข้อเสนอmandatoryretrain/native-zero-shotก่อนใช้งานhelperในreviewก่อนหน้าให้ใช้คำยืนยันนี้แทน

---

<a id="helper-impact-review"></a>
## ตรวจผลกระทบครบเส้นทาง helper — 12 พฤศจิกายน 2026

**ข้อมูลและB4ใช้ต่อได้ ต้องทำรอบSOLIDER RGBใหม่เพื่อให้ได้ผลจากrecipeที่แก้แล้ว ส่วนSAM3.1ปัจจุบันทำต่อได้** ข้อผิดพลาดคือCodexเลือกBGRจากResNet101simple_extractorให้Swin-Smallโดยไม่ได้ตรวจmodel attributes/train/evaluateของarchitectureนั้นก่อน และCPUfixtureเดิมรับรองสมมติฐานBGRที่ผิด

### ผลตรวจและงานที่ต้องทำต่อ

| ส่วน | หลักฐานที่ตรวจจริง | ข้อสรุปเรื่องทำใหม่ |
| --- | --- | --- |
| Annotation300 | SHA256ตรงreceiptที่ผู้ใช้รับรองครบ300ไฟล์ | ใช้ต่อ ไม่มีเหตุให้ทำGTใหม่จากข้อผิดพลาดpreprocessingนี้ |
| Splitและtrainingdata | membership/manifestตรงhashเดิม ไฟล์crop+mask780ตรงbinding แบ่ง313train/77val คงroleและtimegroup isolation เกณฑ์bboxต่ำสุด52/51px ไม่มีall-VOIDcrop | ใช้ต่อ ไม่มีเหตุให้แบ่งใหม่หรือmaterializeใหม่จากข้อผิดพลาดนี้ |
| B4เดิมและรอบปรับปรุง | RGB/ImageNet normalization สอดคล้องกับupstreamFASHN โหลดhelperห้าคลาสตรงorder มี15epochs/157updatesต่อepoch ไม่มีAMPskipหรือnonfinite loss | ใช้checkpointเดิมและรอบปรับปรุงต่อ ไม่พบเหตุให้เริ่มฝึกB4ใหม่ |
| B4savedresults | exact77PNGs แยกreadbackคำนวณconfusionด้วยnp.add.atได้ตรงMETRICSทุกcell IoU/TP/FP/FN/P/R/F1ตรงสูตร checkpoint hash/bestepochตรง | ผลhelper validation65.2874595303%ใช้ได้ตามcrop/routeนี้ |
| SOLIDER | architectureต้นทางRGB แต่runเดิมใช้BGR กลุ่มlogits/resize/map-backยังต่างจากnativepostprocessing มี25epochsและAMPskip2updatesตามGradScaler ไม่มีnonfinite history | ทำfreshRGBattemptจากpretrainedต้นฉบับเมื่อเข้าสู่ขั้นแก้training เก็บBGRweightsและประวัติเป็นอีกrecipe เพื่อดูร่างจริงได้ |
| SOLIDERsavedresults | 77PNGs/GTmembershipครบ การคำนวณย้อนหลังตรงconfusion/metricsและcheckpointbestepoch18ทุกส่วน | 65.5541324044%เป็นผลrecipeBGRที่วัดได้ ส่วนinitial42.76%ต้องประเมินRGBใหม่ก่อนใช้เป็นnativebaseline |
| SAM3.1กำลังฝึก | source snapshot/inputsตรงlaunch ไม่มีAMP ค่าlosshistoryที่ปิดepochแล้วfiniteและมี313optimizerupdates/epoch cache390entries มีsampletrain/valbindingsตรงและtensorFP32/finite | ยังไม่พบเหตุให้หยุดหรือเริ่มtrainingปัจจุบันใหม่ สถานะยังไม่ครบ15epochs |
| SAM3.1warmstart | ใช้decoderจากbestepoch9ที่หยุดรอบเก่า พร้อมpretrainedbackboneและhashที่ระบุแน่นอน | ผลinitial63.6939527947%เป็นwarmstartedhelper baseline ต้องติดป้ายให้ตรง ใช้purezero-shotต้องโหลดpretrainedโดยไม่warmstart |
| B5 | CPUโหลดweights/config/processorlocalได้ มี84,607,186parameters native18labels และprocessor512×512 RGB/ImageNet/labelreductionfalse | ยังไม่มีFTในbatchนี้ จึงไม่มีงานretrainB5 ผลzero-shot77cropsยังต้องทำให้ครบ |
| Legacyzero-shotB4/B5/SOLIDER | mappingรวมHat/Sunglasses/Dress/Scarf/Jumpsuitบางกลุ่ม และB5scriptเก่าไม่ได้ใช้resize512×512ของprocessor | ทำzero-shot evaluationใหม่ตามcontractที่ประกาศก่อนคะแนน ทั้งสี่ตัวใช้77validationcropsชุดเดิม แยกจากtraining |
| LegacySAMzero-shot | มีJPEGoverlay3ตัวอย่าง ผลscalarครบ77ยังขาด | ต้องเก็บผลpurepretrainedและnativeoutputsครบ77เพื่อทำตารางzero-shotเต็ม |

การตรวจsavedmasksย้อนกลับตอบเรื่องexport/GTmembership/คณิตศาสตร์ของscorer ส่วนการตรวจpreprocessingตอบเรื่องinputตรงmodelหรือไม่ เป็นหลักฐานคนละส่วน จึงพบได้ว่าSOLIDERmaskscoringถูกต้องแต่inputrecipeไม่ตรงpretrainedarchitecture

ไฟล์crop/mask780หมายถึง390cropsที่มีภาพและmaskอย่างละไฟล์ การยืนยันhash300annotationsและ780derivedfilesทำให้reuseผลrasterizationfreshnessเดิมได้ B4เดิมเฉลี่ยclassifierweightsของTop/Dressตอนinitialization แล้วเรียนรู้ห้าคลาสจากGTโดยตรง ขั้นตอนinitializationนี้แยกจากlegacyzero-shotmappingที่รวมDressในUpper จึงไม่มีเหตุให้ล้มผลB4fine-tuneเพียงเพราะต้องแก้mappingของตารางzero-shot

ValidpixelsกำหนดจากGT255เดียวกันทุกระบบ และนับpredictedtargetบนGTbackgroundเป็นFP พื้นที่ของคนอื่นที่annotationกำหนดเป็นVOIDพ้นตัวหาร จึงใช้cropIoUรับรองcross-personownershipในพื้นที่ที่ไม่ได้ให้คะแนนไม่ได้ Nativeclassชื่อใกล้GTยังมีความต่างด้านannotationboundaryได้ ต้องเก็บFP/FNตามGTที่ประกาศและไม่เลือกmappingเพื่อช่วยคะแนน

### รายละเอียด SAM3.1 ที่ต้องประกาศให้ตรง

1. Native Sam3Processorทำuint8resize1008×1008แล้วแปลงfloat/normalize0.5 ส่วนhelperปัจจุบันresizefloatแบบbilinear/antialiasแล้วnormalize0.5 FixtureRGBแบบasymmetricที่คำนวณอิสระให้maxabsolute normalizeddifference0.0039217472 และmean0.0019501935 ทั้งคู่คงRGB/ขนาด/ช่วงค่าเดียวกัน ตัวเลขนี้เป็นfixtureเดียว ต้องไม่ใช้ยืนยันoutputequivalenceทั้งdataset
2. Builderตั้งsupervise_joint_box_scores=True แต่nativeprocessorยังคูณpresenceเพิ่มและเก็บqueriesที่ผ่านthresholdหลายอัน Helperปัจจุบันใช้jointscoreหนึ่งครั้ง เลือกqueryเดียวต่อtargetและresolveoverlapด้วยmaskprobability×score CPUtestของเราเช็กhelperpolicyนี้ ไม่ได้รับรองว่าเป็นnativeprocessorpolicy การเรียกการคูณpresenceเพิ่มในnativeว่าbugจึงเกินหลักฐาน
3. Helperlossใช้single-targettrainingmatching เพิ่มabsent/unmatched-query/score/presencesupervision มีgradientเปิดแม้forwardเป็นevalmodeเพื่อข้ามnativeDAC/matcherที่ใช้targetอีกcontract ตรึงbackboneและใช้cacheในattemptเดียวกัน การฝึกด้วยrecipeที่ประกาศนี้ยังทำต่อได้

ข้อแตกต่างของSAMข้างต้นต้องคงไว้ในlabels/routeของผลปัจจุบัน การทำpurepretrainedzero-shotครั้งถัดไปใช้processorที่เลือกและบันทึกให้ครบก่อนดูคะแนน พร้อมประกาศquery/overlap policy การเปลี่ยนnative-likepostprocessingตอนประเมินสามารถใช้weightsเดิมได้ ส่วนการเปลี่ยนtraining objectiveหรือinputrecipeเป็นอีกtrainingattempt

### จุดส่งต่อไป annotation ที่ยังต้องแก้ แต่ไม่ต้องฝึกโมเดลเพื่อแก้

| จุดส่งต่อ | สิ่งที่พบ | งานที่ต้องทำก่อนขยายpseudo-labeling |
| --- | --- | --- |
| เลือกweights | generate_drafts_helper_v1.pyมีdefaultชี้B4v1เดิมและอ่านHFdirectory ส่วนรอบใหม่เก็บBEST.pt | export/loaderที่ตรวจstrictstateและhashได้ แล้วส่งmodel pathชัดเจน ป้องกันการใช้v1โดยไม่รู้ตัว |
| Polygonexport | ใช้RETR_EXTERNAL, contourarea≥12pxและsimplifyepsilon1px | รักษาrawhardmasks ตรวจsmallparts/holes/ownershipและrasterizeกลับก่อนรับdraft ไม่ใช้IoUก่อนpolygonexportอ้างคุณภาพหลังexportโดยตรง |
| Map-back | draftsourceมีunpad→nearestresize→offsetตามbboxcontext15% | ตรวจasymmetricfixtureและภาพจริงกับnativecoordinatesในรอบintegrationก่อนbulk |
| ขอบเขตคะแนน | 77GT-personcropsจาก56validationimages | บอกcropdenominatorและGTbboxconditioning ใช้ภาพเดียวกันตรวจงานแก้จริงเพิ่มเติม คะแนนนี้ยังไม่วัดmissedpersonหรือbboxdraftgenerationทั้ง2,200ภาพ |

### ข้อสรุปการทำซ้ำและลำดับงาน

- เก็บannotation300, split, materializeddata และB4checkpoints/resultsต่อทั้งหมด
- ปล่อยSAM3.1ปัจจุบันจบตามguardเดิม เก็บhistoryและระบุcustomhelperrouteที่ตรวจพบ
- จัดpurezero-shotครบB4/B5/SOLIDER/SAM3.1บน77cropsต่อโมเดล ใช้pretrainedก่อนCCTVFTและตรึงmapping/input/outputcontractก่อนเปิดงาน เนื่องจากผลเก่าส่วนใหญ่มีเพียงoverlay/roundedreport จึงต้องinferenceเฉพาะzero-shotที่ไม่มีrawoutputsเพียงพอ ไม่ใช่งานtraining
- ทำfreshSOLIDERRGBtrainingattemptจากpretrainedเดิมเพื่อแก้recipe ตามงบที่ตรวจแล้ว ผลBGRเดิมยังเก็บเป็นcandidateภายใต้recipeเดิม การฝึกRGBใหม่ยังไม่รับประกันคะแนนสูงกว่า
- ตรวจcheckpointexport/geometry/polygonroundtripก่อนสร้างdraftชุดใหญ่ แล้วจึงใช้ผลร่าง/ภาระแก้จริงเลือกhelper

ในworkunitตรวจผลกระทบนี้ไม่มีmodel-forwardหรือtraininglaunchเพิ่ม ใช้CPUอ่านsavedartifactsและตรวจmetadata/scorer/source CurrentSAM3.1workerคงsource_frozenเดิม ตรวจprocessจริงถึงepoch3/15แล้ว ตัวเลขepochในreviewนี้เป็นsnapshot การตรวจนี้ไม่ใช่คำรับรองว่าทุกภาพหรือทุกrouteผ่านproductionacceptance

### หลักฐานและขอบเขตที่ยังยืนยันไม่ได้

Privateevidenceอยู่ในrunเดิมใต้impact_review_20261112 มีRESULTS, SOURCE_CHECK, ARITHMETIC_EXTENDED และB5_CPU_IDENTITY sourcePythonที่ใช้launchยังตรงทั้งหมด B4 2files / SOLIDER267 / SAM158 files ใช้auditfreshnessเดิมประกอบการตรวจannotation/cropbindingปัจจุบัน ไม่rasterizeGTใหม่ซ้ำ

ยังไม่มีเวลาผู้ใช้แก้draftจริง ไม่มีrawzero-shotครบทั้งสี่ตัว และยังไม่ได้รับไฟล์SOLIDER_HUMAN_PARSING_BENCHMARK_TH.mdที่อ้าง56.34%/154ms จึงยังผูกแถวนั้นกับrun/processor/timingboundaryไม่ได้ Epochsecondsในtraininghistoryรวมtrain/validationและI/O/cacheบางช่วง ใช้เป็นoperationaldiagnostics เวลา154msต้องตรวจต้นฉบับก่อนนำมาเทียบ

อ้างอิงB4inputจาก[upstreamFASHNparser](https://github.com/fashn-AI/fashn-human-parser/blob/main/src/fashn_human_parser/parser.py) และB5จาก[processorของcheckpointที่เลือก](https://huggingface.co/matei-dorian/segformer-b5-finetuned-human-parsing/blob/fb3404cf7ab68cb62f78885cdf9b992864d080db/preprocessor_config.json) SOLIDER/SAMอ้างsourceที่ผูกrevision/hashในrun ส่วนmean/std/resize/querypolicyตรวจจากarchitectureและprocessorจริง

---

ส่วนถัดไปเป็นประวัติการพบและแก้ปัญหาในแต่ละช่วง

<a id="solider-rgb-correction"></a>
## แก้ข้อผิดพลาด preprocessing ของ SOLIDER Swin — 12 พฤศจิกายน 2026

Codex อ้างBGRจากsimple_extractor.pyที่สร้างResNet101 แล้วนำมาใช้กับSwin-Smallผิดตัว หลักฐานตรงarchitectureคือ `networks/AugmentCE2P.py` กำหนด `pretrained_settings['swin']['imagenet']` เป็นRGB, mean[0.485,0.456,0.406], std[0.229,0.224,0.225] ส่วนSwin-Small constructorนำsettingsนี้ไปตั้งmodel.input_space/mean/std และtrain.py/evaluate.pyเลือกtransformตามmodel attributes ตรวจจากSOLIDER-HumanParsing revision `7bdd9eb0c38c4ca2c2f09ce4db4e7664be8d3357`

ดังนั้นinitial mIoU4=42.760368244993713% และผลfine-tuneSOLIDER65.55413240436256%ที่บันทึกแล้วมาจากrecipeBGRที่Codexกำหนด ต้องเก็บพร้อมป้ายNON_NATIVE_PREPROCESSING_RECIPE ผล42.76%ถูกถอดจากตารางnative-preprocessingzero-shotปัจจุบัน ส่วนweights/logs/masksเดิมเก็บครบ การฝึกบนBGRและประเมินบนBGRยังอธิบายconfigurationนั้นได้ แต่ใช้รับรองbaselineRGBของpretrainedSwinไม่ได้

แก้trainerสำหรับattemptถัดไปให้อ่านinput_space/mean/stdจากmodelจริง และแก้CPUfixtureให้ตรวจRGBตามsourcearchitecture TestsเดิมตรวจBGRตามสมมติฐานที่ผิด จึงไม่ได้รับรองpreprocessingที่ตรงต้นทาง รักษาactiveSAM3.1source snapshotและprocessเดิม ไม่เปิดGPUretestหรือretrainเพิ่มในworkunitนี้

สำหรับpurepretrainedzero-shotให้ใช้weightsก่อนCCTVfine-tune เตรียมภาพตามcheckpoint/architecture ใช้native20logits→resize/map-backตามgeometryต้นทาง→nativeargmax→fixedtargetmapping การรวมlogitsก่อนargmaxเป็นอีกconfigurationที่ต้องระบุแยก ให้Hair={2}, Face={13}, Upper={5,7}, Lower={9,12}และnativeอื่นเป็นbackground/OTHERตามGTcontractที่ประกาศ ห้ามเลือกmappingเพราะคะแนนสูงกว่า

รายงานชื่อSOLIDER_HUMAN_PARSING_BENCHMARK_TH.mdที่ผู้ใช้อ้างยังค้นไม่พบในworkspace ต้องรับpath/ไฟล์และหัวตารางก่อนผูกค่ากับrun จากตัวเลขที่ส่งมา ค่าเฉลี่ย(53.13+47.17+69.37+55.68)/4=56.3375% สอดคล้องกับ56.34%ที่เป็นคอลัมน์แรก จึงยังไม่ถือว่า55.68%เป็นmIoUโดยไม่มีหัวตาราง เวลา154msยังต้องตรวจtimingboundary/denominatorจากต้นฉบับ

ข้ออ้างBGRเป็นวิธีที่ถูกต้องสำหรับSwinในreviewก่อนหน้าด้านล่างถูกแก้โดยส่วนนี้ ประวัติเหล่านั้นเก็บตามเวลาที่บันทึก

---

<a id="helper-zero-shot-only"></a>
## ผล pretrained zero-shot ที่มีอยู่ — 12 พฤศจิกายน 2026

ผู้ใช้จำกัดงานนำเสนอรอบนี้เฉพาะweightsก่อนfine-tuneด้วยCCTVของเรา รวมB4/B5/SOLIDER/SAM3.1 เก็บการเปรียบเทียบก่อน–หลังไว้ทำภายหลังเมื่อผลพร้อม ตารางด้านล่างเป็นหลักฐานที่มีอยู่ คะแนนบน77validationcrops ส่วนgalleryเลือกสามcropsแรกตามSAMzero-shotเดิม ไม่มีmodelcallsเพิ่ม

| Model | Hair IoU % | Face IoU % | Upper IoU % | Lower IoU % | mIoU4 % |
| --- | --- | --- | --- | --- | --- |
| b4 | 46.54 | 29.83 | 49.47 | 38.81 | 41.16 |
| b5 | — | — | — | — | — |
| solider | — | — | — | — | รอผลRGBที่ตรงarchitecture |
| sam31 | — | — | — | — | — |

B4อ้างEVAL_REPORTเดิมที่มีค่าปัดเศษและรวมDressในUpper SOLIDERอ้างINITIAL_METRICSของpretrainednative20ที่ใช้BGR/groupedlogits ภาพSOLIDERzero-shotเดิมใช้RGB/normalization/mappingต่างกัน จึงติดป้ายlegacyและแยกprovenanceของภาพกับคะแนน ยังต้องจัดผลzero-shot77cropsของB5/SAM3.1ให้ครบก่อนสรุปสี่ตัว

Galleryส่วนตัวอยู่ในprivate run `helper-refinement-20261112T073106Z/comparison_20261112/index.html` มีตาราง4แถวและภาพzero-shot3ตัวอย่างพร้อมMANIFESTที่ผูกhashes/readbackgeometry รูปhistoricalมีrender/JPEG/resizeต่างกัน ใช้ดูเชิงคุณภาพ หน้าgalleryแสดงเฉพาะzero-shot ส่วนdraftที่เคยรวมผลfine-tuneเก็บแยกตามประวัติ ไม่เผยแพร่ภาพdatasetบนpublicGit และคงงานฝึกเดิมให้ทำต่อ

---

<a id="helper-training-revision2"></a>
## ฝึกตัวช่วยฉบับปรับปรุง — 12 พฤศจิกายน 2026

สถานะล่าสุดเมื่อ12พฤศจิกายน2026 เวลา15:23ไทย **B4_COMPLETE / SOLIDER_COMPLETE / SAM31_IN_PROGRESS** ผู้ใช้อนุญาตหยุด SAM3.1 รอบเดิมและให้เริ่มตัวที่เร็วกว่า จัดลำดับ SegFormer-B4 → SOLIDER → SAM3.1 ทีละตัวบน Tesla T4 เป้าหมายคือร่าง annotation ที่ผู้ใช้แก้น้อยลง

B4ครบ15epochsและSOLIDERครบ25epochs ทั้งสองมีvalidation predictions77ไฟล์ตามcompletionของตนเอง SAM3.1 PID123721ยังทำงาน ประเมินbaselineครบ77cropsและเริ่มฝึก โดยตรวจfeature cacheของtrainเพิ่มจาก2เป็น10/313ระหว่างการตรวจ สถานะของworkerยังเขียนLOADINGเพราะอัปเดตครั้งถัดไปหลัง20trainingcrops จึงต้องอ่านartifact progressประกอบ คงsource snapshotของrunเดิม

เพิ่ม [ตัวดูสถานะแบบอ่านอย่างเดียว](../scripts/helper_training_progress.py) แสดงphaseจากbaseline/cache/statusที่มีจริง พร้อมแยกจำนวนcacheออกจากtraining counter ผ่านCPUfixtures3กรณีและตรวจกับrunจริง ดูสดได้จากในโฟลเดอร์runด้วย `python3 /home/skyaidev/folk/CCTV_Dataset_Development/scripts/helper_training_progress.py --watch` รายละเอียดการเปิดbatchด้านล่างเป็นsnapshot ณ เวลาเริ่มงาน

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

ตรวจเริ่มงานเมื่อ `2026-11-12T14:40:33.997309+07:00` ยืนยัน controller PID71234 และ B4 worker PID71265 มี session leader แยกจากบทสนทนา อยู่ใน tmux `helper_seed300_r2` และผ่าน training batch20/157 ของ epoch1 แล้ว Run `helper-refinement-20261112T073106Z` ใช้ launch commit `99a55ea14ce833e8c65a7eef6c9e0817cf9c98b8` Source snapshot และ manifest อยู่ใน private run เดิม

| ระบบ | สถานะที่ตรวจหลังเปิด batch |
| --- | --- |
| B4 | TRAINING 15epochs, ได้ INITIAL_METRICS และบันทึกสถานะหลัง backward/optimizer steps แล้ว |
| SOLIDER | PENDING อยู่ลำดับถัดไป ยังไม่มี GPU calls ของรอบใหม่ |
| SAM3.1 | PENDING รันหลัง SOLIDER สำเร็จ รอบเก่าเก็บ best epoch9 ไว้ |

Baseline ก่อนปรับ B4 รอบนี้ global mIoU4=0.645484405181 จาก evaluator FP32 สูตรที่ประกาศ ขณะที่ log ฝึกเดิมประเมินภายใต้ AMP และแสดง0.6454162071 จึงเก็บค่าทั้งสองพร้อม evaluator bindings ไม่ใช้ความต่างนี้อ้างว่ารอบใหม่ได้เรียนรู้ดีขึ้นก่อนเริ่มฝึก

สถานะ controller อ่าน `runs/helper-refinement-20261112T073106Z/STATUS.json` ใน private workspace และดูความคืบหน้า B4 จาก `b4/STATUS.json` กับ `b4.log` เมื่อแต่ละโมเดลจบจะมี METRICS.json, validation_predictions77ไฟล์ และ STATUS=COMPLETE ของตนเอง Controller=COMPLETE เมื่อทั้งสามจบ Controller=STOPPED ให้ตรวจ error/history ก่อนทำต่อ ไม่มี automatic retry

คำสั่งบน server ต่อไปนี้อ้าง path ของ private workspace ที่ใช้งานจริง

```bash
cat /home/skyaidev/folk/CCTV_Dataset_Development.local/runs/helper-refinement-20261112T073106Z/STATUS.json
cat /home/skyaidev/folk/CCTV_Dataset_Development.local/runs/helper-refinement-20261112T073106Z/b4/STATUS.json
tail -f /home/skyaidev/folk/CCTV_Dataset_Development.local/runs/helper-refinement-20261112T073106Z/b4.log
```

ข้อมูลผล train ใหม่ยังไม่ครบสามโมเดล การเลือกตัวช่วยที่ทำให้แก้น้อยที่สุดต้องตรวจร่างและเก็บภาระการแก้เมื่อผลพร้อม

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
