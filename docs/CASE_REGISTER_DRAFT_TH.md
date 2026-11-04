# ทะเบียนเคสและแบบสำรวจ — inherited DRAFT

นำกติกาและ case register เดิมมาใช้ ไม่แนบสถิติบริษัท/ข้อทักท้วงตัวเลขรายงานเก่า P1 และ REPORTED เป็นที่มาจาก private legacy report ไม่ใช่การยืนยันภาพในรอบตั้ง workspace ตารางนี้ยังไม่ใช่ actual case observations

## 3. กรณีที่รายงานไว้แล้ว แต่ต้องยืนยันจากภาพ

| ID | สิ่งที่ P1 รายงาน / locator | ประเด็น annotation ที่ต้องแก้ | หลักฐานที่ต้องเก็บ | สถานะ |
| --- | --- | --- | --- | --- |
| K01 | §3.2/§6: หลายคนแต่ระบบเดิมพบเพียงบางคน | นับและผูก owner ทุกคนตามเกณฑ์ ไม่ใช้ prediction เป็น GT | ภาพเต็ม source ID จำนวนคนที่ผู้ตรวจเห็น ข้อมูลระบบเดิมแยกต่างหาก | REPORTED |
| K02 | §5.3/§6: เสา ต้นไม้ รั้ว หรือวัตถุบังคน | visible geometry, disconnected regions และ owner | ตำแหน่งบัง region ที่ยืนยันได้ เหตุผลส่วนที่ตัดสินไม่ได้ | REPORTED |
| K03 | §5.3/§6: คนเล็กหรือไกล | ระดับรายละเอียดที่ annotate ได้ และความหมาย threshold พิกเซล | original resolution, person bbox height/width, mask area ถ้ามี | REPORTED |
| K04 | §5.3/§6: กลางคืน low-light และ glare | ขอบเขตที่ไม่ชัดกับสีที่ตัดสินไม่ได้อาจเป็นคนละส่วน | ภาพต้นฉบับ modality แสงที่เห็น และ validity แยกงาน | REPORTED |
| K05 | §5.3: IR grayscale | ห้ามอนุมานสีวัตถุจริงจากความสว่างขาวดำ | modality metadata ถ้ามี; หากไม่มีให้ระบุว่า grayscale appearance เท่านั้น | REPORTED |
| K06 | §6: ไม่มีคน/วัตถุถูกระบบเดิมตีเป็นคน | negative frame และ false-positive evaluation ตามขอบเขต | ภาพเต็ม ผลตรวจคน ระบบที่ให้ prediction และเหตุผลคัดออก | REPORTED |
| K07 | §5.1: ภาพกล้องเดียวกันห่างกันสั้น | การจัดกลุ่มและการนับหน่วยอิสระ | camera/time/source event และการเทียบภาพ ไม่ยืนยันคนเดิมจากเวลาอย่างเดียว | REPORTED |
| K08 | §4: event category ไม่พอระบุทุกคนหรือเสื้อผ้า | แยก metadata บทบาทจากสิ่งที่มองเห็น | mapping event-to-image และ annotation รายคนโดยไม่เดาบทบาท | REPORTED |

ไม่เติมชื่อภาพ camera ID หรือ person count เฉพาะกรณีจากการคาดเดา notes ที่ยกตัวอย่างใน P1 ยังไม่ใช่ image-level linkage


## 4. กรณีที่เสนอให้ค้นเพิ่ม

| ID | กรณีทดสอบ | เหตุผล | สถานะ |
| --- | --- | --- | --- |
| X01 | คนหลุดขอบภาพ เห็นชนิดเสื้อผ้าแต่ไม่เห็นปลาย | ทดสอบชนิดกับความยาวและ truncation | HYPOTHETICAL |
| X02 | คนหันหลัง/ไขว้แขน/เอียงตัว | ทดสอบซ้ายขวาของคนกับด้านภาพ | HYPOTHETICAL |
| X03 | เสื้อคลุมซ้อนเสื้อ กระเป๋าบังลำตัว | ทดสอบชั้นเสื้อผ้าและ visible surface | HYPOTHETICAL |
| X04 | กระเป๋าถือหรือร่มอยู่ระหว่างคนสองคน | ทดสอบ ownership และขอบเขต person mask | HYPOTHETICAL |
| X05 | เสื้อหลายสี โลโก้เล็ก หรือเส้นจาก compression | ทดสอบสีหลัก/หลายสี/ลวดลายกับ artifact | HYPOTHETICAL |
| X06 | ภาพมีกรอบ ข้อความ timestamp หรือ mask วาดทับอยู่แล้ว | ทดสอบต้นฉบับและบริเวณที่ข้อมูลสูญหาย | HYPOTHETICAL |
| X07 | เงา ภาพสะท้อน โปสเตอร์หรือหุ่น | กำหนด eligible person กับ depiction/reflection | HYPOTHETICAL |
| X08 | ภาพซ้ำ exact แต่คนละ event record | แยกจำนวนรายการจากจำนวนภาพอิสระ | HYPOTHETICAL |

รายการนี้ไม่ใช่การยืนยันว่าบริษัทมีทุกกรณี และไม่ใช้ความถี่จากชุดค้นเคสเป็น prevalence


## 6. วิธีเลือกรายการเสนอสำหรับสำรวจ — ปรับหลัง eafe703

ตาม [protocol 24+8](AUDIT_PROTOCOL_DRAFT_TH.md): reuse ประวัติเดิม 12 records แล้วเติม coverage ใหม่ 12 จาก raw site-camera pairs ที่ยังขาด และ discovery ใหม่ 8 จากบริบทของ anchors ตามกติกา/seed ที่บันทึกใน private manifest ไม่ใช้ category เป็น event/person label และไม่ใช้เวลาเป็นหลักฐานสภาพภาพ

ณ preparation มี proposed membership/seed แล้วและยังไม่เปิดภาพ ภายหลัง bounded exploration ทำครบตามรายการเดิมโดยไม่มี final test; metadata-only deterministic tie-break ไม่ใช่ probability sample ไม่มี prevalence estimate สถานะของเคสเดิมด้านบนยัง REPORTED และ X ยัง HYPOTHETICAL จนมีการเปิดดู/บันทึกตามขอบเขตที่ได้รับอนุญาต

ไม่เปลี่ยน raw curation/status/notes ตาม proposal หากรอบหน้าพบเคสไม่ตรงสมมติฐานให้บันทึก found/not found/uncertain พร้อมเหตุผลการเพิ่ม/แทนรายการใน revision ใหม่ คงประวัติรายการเดิม ไม่แปลง pending เป็น unreviewed หรือโยก discovery ไป final โดยเงียบ ๆ

## 7. แบบบันทึก exploration ตาม requirements ล่าสุด — PROPOSED

ใช้กับ proposed manifest ภายในที่จัดเตรียมหลัง eafe703; เป็นรายการคำถาม ไม่ใช่ ground truth/taxonomy/annotation schema สุดท้าย หนึ่งแถวเริ่มจากภาพเต็ม หากต้องแยกคนหรือคำถาม region ภายหลัง ให้เพิ่มแถวโดยคง exploration_id และใช้ candidate locator ชั่วคราว ไม่ถือว่าเป็น person GT ID หรืออัตลักษณ์ข้ามภาพ

| กลุ่ม / fields ในแบบบันทึกภายใน | สิ่งที่ต้องบันทึกเมื่อเปิดรอบที่ได้รับอนุญาต |
| --- | --- |
| `exploration_id`, `proposed_order`, `observation_unit`, `candidate_person_locator_not_GT_ID` | ผูก proposal และหน่วยคำถาม; ยังไม่สร้าง mask/person annotation |
| `historical_sample_alias`, `historical_observation_reported_only`, `current_visual_review_state` | แยกผลรายงานเก่าจากการเปิดดูใหม่; ทุกภาพยัง NOT_STARTED สำหรับ checklist ล่าสุด |
| `person_separation_observability`, `region_owner_observability`, `person_mask_boundary_observability` | แยกบุคคลได้หรือไม่ region เป็นของใครและไม่แน่ใจที่ใด; ปัญหาขอบ person/อุปกรณ์ ไม่ผูกกับ detector prediction |
| `upper_visibility_notes`, `lower_visibility_notes`, `footwear_visibility_notes` | ส่วนใดเห็น/ไม่เห็น/ถูกบัง/หลุดขอบและหลักฐาน; ไม่ใช้ not visible แทน absent หรือเดา footwear ที่อยู่นอกภาพ |
| `one_piece_or_upper_lower_ambiguity`, `outer_layer_overlap_notes`, `accessory_person_mask_scope_question` | ชิ้นเดียว เสื้อคลุมซ้อน รอยต่อบน–ล่าง สิ่งถือ/สวมและ ownership; บันทึกทางเลือก ไม่กำหนด numeric classes |
| `upper_color_readability`, `lower_color_readability`, `color_uncertainty_reason` | อ่านสีบน–ล่างได้เพียงใด/อะไรทำให้ลังเล; ไม่บังคับชื่อสี/palette หรือเดาสีจริงจาก grayscale |
| `scale_evidence`, `occlusion_evidence`, `frame_boundary_evidence` | สิ่งเห็นเกี่ยวกับขนาด/บัง/ตัดขอบ แยกการวัดจริงจากความรู้สึก; ไม่สรุปขนาดคนจาก frame dimensions |
| `lighting_observation`, `modality_evidence_and_source` | แสงที่เห็นและที่มาหลักฐาน modality; grayscale appearance ไม่พิสูจน์ IR และ record-clock ไม่พิสูจน์กลางคืน |
| `observed_from_image`, `inference_hypothesis`, `needs_human_review` | แยก observation จริง สมมติฐาน และประเด็นให้มนุษย์ทบทวน ถ้ายังไม่เปิดภาพให้ว่าง ไม่เติมจาก metadata |
| `structured_output_support_question`, `description_support_question` | สิ่งที่ข้อมูลรองรับให้สื่อได้/ต้องละเว้น/แสดง uncertainty; ยังไม่สร้าง structured GT หรือคำบรรยายอ้างอิง |
| `explorer_id`, `exploration_started_at`, `exploration_finished_at`, `visual_exploration_seconds`, `recording_seconds` | ผู้สำรวจและเวลาเปิดดู/เวลาเขียนบันทึกจริง แยกกัน; ไม่ประมาณไว้จากจำนวนภาพ |
| `reviewer_id`, `review_state`, `independent_review_state` | ผู้ทบทวนกับผู้สำรวจคนละบทบาท ถึงยังไม่ทราบคนจริงก็เก็บ UNASSIGNED/NOT_PERFORMED; ไม่อ้าง independent review จนทำตามวิธีที่กำหนด |
| `annotation_time_seconds_not_collected`, `case_tags_proposed`, `decision_refs` | เวลา annotation ยังว่าง/ไม่เก็บ และห้ามใช้ exploration time ประมาณแรงงาน masks; K/X tags และ DEC เชื่อมข้อสงสัย |

แบบ draft ใน preparation คงเวลา/observation ว่างตามเดิม ผล visual ใหม่แยกใน fresh run ด้วย exploration-v1.1 เป็น frame records และ locator rows เพิ่มได้ ไม่เขียนทับ draft/ประวัติ รูปแบบ free text/สถานะยังแก้ได้ก่อน controlled vocabulary ใน pilot ไม่มี confidence ที่อ้าง calibrated probability และไม่ถ่ายทอด category เป็นบทบาทคน

## 8. กติกาการดูภาพสำหรับ audit

- ดูภาพเต็มก่อน crop เพื่อเข้าใจเจ้าของส่วนและบริบท
- ตรวจจากต้นฉบับที่ความละเอียดจริง; zoom เพื่อดูได้แต่ไม่สร้างรายละเอียดใหม่
- หากใช้ภาพปรับความสว่าง ให้เก็บแยกและระบุผลต่อการตัดสินสี ไม่แก้ทับ original
- แยกข้อเท็จจริงที่เห็นออกจากข้อสันนิษฐาน; ไม่อนุมานบทบาทบุคคลจาก category/Category_EN หรือเสื้อผ้า; export ปัจจุบันยังไม่มี event/person binding ที่พิสูจน์ได้
- หากดูหลายเฟรมเพื่อหาตัวบุคคลหรือวัตถุ ให้บันทึกว่ามี temporal assistance; ไม่ใช้เฉลยจากเฟรมอื่นแทน observability ของ target frame โดยไม่ประกาศ protocol
- คำตอบที่ไม่แน่นอนเข้าสู่ adjudication log; ไม่ลบหลักฐาน disagreement หลังได้ข้อยุติ


## 10. เกณฑ์รายงานผลรอบถัดไป

ต้องรายงานจำนวนภาพ/คนที่ตรวจจริง จำนวนไฟล์อ่านไม่ได้ วิธีเลือก หน่วย denominator ความถี่กรณีแบบ multi-label และรายการที่ยังไม่ตัดสิน
แยกจำนวนเหตุการณ์จากภาพและคน; หากรายงานช่วงความไม่แน่นอนต้องพิจารณาการจับกลุ่มตามเหตุการณ์/กล้อง ไม่สมมติว่าภาพต่อเนื่องทั้งหมดอิสระกัน

เอกสารที่เชื่อมกัน:

- BENCHMARK_REQUIREMENTS_DRAFT_TH.md — REQ-01, REQ-08 ถึง REQ-20
- EVIDENCE_AND_HYPOTHESES_TH.md — C01 ถึง C11 และ H-01 ถึง H-06
- P1: DATASET_DETAILS(2).md Rev. 2; ไม่แก้ไขต้นฉบับในรอบนี้

## 11. บทเรียนสำหรับกฎร่างจาก bounded visual exploration

มีข้อสังเกตจากภาพใหม่ครบตาม manifest แล้ว แต่ตาราง K/X ข้างบนยังบอกที่มาจาก P1/สมมติฐานเดิม ไม่อัปเกรดทุกเคสเป็น observed โดยรวม ผลรายเคส/IDs อยู่ใน private run ผู้สำรวจเป็น assistant/Codex; independent human review NOT_PERFORMED

ประเด็นที่ต้องร่างก่อน annotation pilot คือ visible support ที่ขาดเป็นช่วงเมื่อถูกบัง, region owner เมื่อคน/สิ่งถือ/ผ้าพาดซ้อน, scope ของ bag/outer layer กับ person mask, upper/lower ที่ไม่เห็นรอยต่อ, barefoot/sandal/unobservable, สีในแสง/cast/หลายชั้น และ source text/boxes/black regions ที่ไม่ใช่ GT ไม่มีหลักฐานให้เรียกทุกคน/ทุก region annotate ได้ครบจาก exploration นี้

ข้อสังเกตคนเล็ก/ส่วนหัวที่ขอบ/possible person ต้องใช้ locator และ uncertainty ไม่สร้าง GT Person ID หรือ certify negative จากการมองไม่พบคน เสื้อชิ้นเดียวชัดเจน/รองเท้ารายละเอียดหลายมุมและ known-modality ยังเป็นช่องว่าง ไม่เพิ่มภาพนอก manifest ในรอบนี้

ผล discovery มีทั้งเคสที่พบ/ไม่พบและ component ที่ uncertain พร้อมกรณี exact duplicate ของ anchor จึงไม่เป็น success rate หรือ prevalence เวลา active visual ที่ไม่วัดและ annotation time คง null แม้มีเวลาประมวลผลภาพ ไม่มีการใช้เวลา AI ประมาณแรงงาน masks มนุษย์


## ข้อสังเกตภาพจริงรอบต่อ — 4 พฤศจิกายน 2026

ตารางนี้เป็น **OBSERVED_BY_CODEX** จาก native full-frame displays ที่มี SHA256/locator ส่วนตัว ไม่ใช่ REPORTED จาก legacy report และไม่ใช่ GT/การตรวจรับโดยผู้ใช้ รหัส N ใช้เชื่อมหลักฐาน private ของ work unit `visual-review-continuation-20261104T103212Z` โดยไม่เผยแพร่ image IDs หรือภาพจริงใน Git

| Case | สิ่งที่เห็นจากต้นฉบับ | ผลต่อกติกาที่แนะนำ (PROPOSED) | สิ่งที่ยังยืนยันไม่ได้ |
| --- | --- | --- | --- |
| N01 / K03,K05 | ฉากเกือบขาวดำ แต่กรอบและข้อความที่ติดมาเป็นสี คนอยู่ระยะไกล | แยก semantic observability ออกจาก color validity; ไม่ใช้สีกรอบเป็นสีเสื้อผ้า ไม่ใช้กรอบเดิมเป็น person GT | กล้องเป็น IR หรือไม่ และ chromatic color ของเสื้อผ้า |
| N02 / K02 | คนก้มและถูกโครงเหล็กบัง มีสิ่งสะพายแยกจากเสื้อ | annotate เฉพาะ visible support, รักษารูพื้นหลังและแยก accessory/garment | รูปร่างใต้โครงสร้างและขอบส่วนที่ซ่อน |
| N03 / reflection | คนเดินชิดผิวสะท้อน เห็น reflection อีกด้าน | ไม่เพิ่ม physical-person count จาก reflection; เสนอ scene validity region ที่กำหนดจาก GT และใช้ร่วมทุกระบบ | ยังไม่มี reflection mask หรือผลตรวจโดยผู้ใช้ |
| N04 / blur,partial | คนถูกตัดขอบล่าง ขอบหน้าและผมเบลอในภาพเกือบขาวดำ | มี person ไม่แปลว่า annotate ครบ4targetsหรือสีได้; unknown ไม่ใช่ absent/BG | precise Hair/Face boundary และสีเสื้อผ้า |
| N05 / K02,K04 | คนสองคนเดินชิดกัน มีแขนพาดใกล้ไหล่และแสงไฟแรง | แยก owner เฉพาะส่วนที่เห็น; สีที่ปรากฏไม่ใช่สีแท้ภายใต้แสงมาตรฐาน | ขอบส่วนที่ถูกคนข้างเคียงบังและ intrinsic color |
| N06 / K06 | เปิดต้นฉบับบริเวณแคบหลังตู้แล้ว ยังยืนยันบุคคลไม่ได้ | คง uncertain-presence; ไม่รับเป็น negative หรือบังคับสร้าง person GT | มีคนอยู่หลังสิ่งบังหรือไม่มีจริง |

เคสเหล่านี้เป็นรายการสำหรับทดสอบกติกา/coverage ไม่ใช่ prevalence หรือความสำเร็จของ annotation; ไม่อนุมานชนิดเสื้อผ้าหรือ modality จากชื่อ field และไม่ขยาย scope ไปหาโมเดลใหม่


## Native detail เพิ่มจาก S0077-S0088

**OBSERVED_BY_CODEX / NOT_GT** — private work unit `visual-review-continuation-20261104T104316Z` เชื่อม source/cache hashes และเหตุผลเลือกจากความกำกวม ไม่มีการใช้คะแนนโมเดลเลือกภาพ ไม่อ้าง prevalence หรือความถูกต้องของ annotation

| Case | สิ่งที่เห็น | ข้อเสนอการจัดการ / สิ่งที่ยังไม่ทราบ |
| --- | --- | --- |
| N07 / viewpoint, headwear, occlusion | ภาพมุมก้มมาก คนสวมหมวกและมีพุ่มไม้บังลำตัวส่วนล่าง เห็นเสื้อเพียงบางส่วน | หมวกแยกจาก Hair ไม่เติมผมที่ซ่อนหรือเสื้อใต้พุ่มไม้; บันทึก visible person แยกจาก target observability ไม่คัดทิ้งทั้งภาพเพียงเพราะคนไม่เต็มตัว มุมเป็น qualitative ไม่ใช่องศาที่สอบเทียบแล้ว |
| N08 / image artifact, visibility | ปื้นสว่างขนาดใหญ่ทับบริเวณศีรษะและบางส่วนของลำตัว แต่ยังเห็นขาและบางส่วนของเสื้อผ้า | presence ยังบันทึกได้; Hair/Face boundary ที่ถูกปื้นทับยังอ่านไม่ได้ เสนอ task-specific GT validity ที่ใช้ร่วมทุกโมเดล ไม่เดารูปร่าง/สีใต้ปื้นหรือยืนยันสาเหตุว่าเป็นน้ำ/เลนส์/แสงสะท้อนโดยไม่มีหลักฐาน |

สถานะ policy เป็น PROPOSED_NOT_FROZEN ไม่มี polygon/GT หรือผู้ใช้ตรวจรับ การเปิดต้นฉบับช่วยระบุปัญหาที่ต้องทดสอบ ไม่ได้พิสูจน์ว่าจะวาดขอบ mask ได้เท่ากันทุกผู้ทำ
