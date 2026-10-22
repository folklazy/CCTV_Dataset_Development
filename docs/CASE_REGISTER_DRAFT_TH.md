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

ตอนนี้มี proposed membership/seed แล้ว แต่ยังไม่เปิดภาพหรือสุ่ม final test; metadata-only deterministic tie-break ไม่ใช่ probability sample ไม่มี prevalence estimate สถานะของเคสเดิมด้านบนยัง REPORTED และ X ยัง HYPOTHETICAL จนมีการเปิดดู/บันทึกตามขอบเขตที่ได้รับอนุญาต

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

เวลาและ observation ใหม่ยังว่างในทุกแถว แบบฟอร์มอาจใช้ free text/สถานะ unknown-not-reviewed ที่เสนอ ก่อนกำหนด controlled vocabulary ใน pilot ไม่มี confidence ที่อ้าง calibrated probability และไม่ถ่ายทอด category เป็นบทบาทคน

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
