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


## 6. วิธีเลือกภาพสำหรับสำรวจ
แยกสองกิจกรรม:
1. Coverage audit: สุ่มจากกรอบภาพที่ระบุเพื่อประมาณการกระจาย โดยเก็บ sampling probabilities/weights เมื่อใช้ไม่เท่ากัน
2. Edge-case discovery: เจาะจง flagged/notes และกรณี X เพื่อค้นปัญหาคู่มือ ไม่ใช้ประมาณสัดส่วนภาพทั้งชุด

ขั้นตอนที่เสนอ:
- ตรวจ manifest และ unique image IDs ก่อน; เก็บรายการที่โหลดไม่ได้/อ่านไม่ได้แยก
- แบ่งตาม site, camera, time block และ curation status ที่มีจริง ไม่สร้าง strata จากค่าที่เดา
- เลือกภาพภายใน strata ด้วย seed ที่บันทึกไว้ และเก็บกลุ่มภาพต่อเนื่องเพื่อไม่แบ่งข้าม pilot/final
- บันทึกภาพจาก selected, rejected, flagged และ not-yet-reviewed หากมี; เหตุผลเดิมไม่หาย
- สำรวจสภาพแสง/scale/occlusion จากภาพเป็นข้อมูลใหม่ เพราะบางค่าไม่มี metadata
- เพิ่มตัวอย่างใน strata หรือคู่คลาสที่ยังไม่ครอบคลุม แล้วรายงานขั้นตอนเพิ่ม
- กำหนดขนาด audit หลังรู้จำนวน strata และทรัพยากร; ไม่อ้างจำนวนเริ่มต้นใดเป็นมาตรฐานโลก

ยังไม่มี seed หรือภาพที่ถูกสุ่มจริงในรุ่นนี้


## 7. แบบฟอร์มตรวจภาพหนึ่งรายการ
| กลุ่ม field | ข้อมูล |
| --- | --- |
| Provenance | audit_id, image_id, source filename/hash, source event ID, camera/site/time, timezone ถ้ารู้ |
| File | width/height, decode status, original/derived, overlay present, transformation history |
| Curation | selected/rejected/flagged/unreviewed, original note, reason for audit inclusion |
| Person | instance ID ภายในภาพ, eligible status/reason, bbox ตามนิยามที่เลือก, visible region |
| Measurements | bbox height px, bbox area ratio, mask area ratio เฉพาะเมื่อมี mask; ระบุ null เมื่อยังไม่วัด |
| Conditions | visible lighting, modality evidence, occlusion, truncation, blur และ confidence/reason |
| Task validity | part/type/color/length/pattern: applicable? observable? annotated? พร้อมเหตุผล |
| Cases | K/X tags, source of claim (reported/observed/measured), question for adjudication |
| Review | annotator, reviewer, date, guideline version, independent result, consensus decision |
| Trace | candidate IDs / hypothesis IDs / decision IDs ที่เกี่ยวข้อง |

ฟอร์มนี้เป็น specification ยังไม่มีแถวข้อมูลจริง ตัวเลข confidence ไม่ใช่ calibrated probability โดยอัตโนมัติ


## 8. กติกาการดูภาพสำหรับ audit
- ดูภาพเต็มก่อน crop เพื่อเข้าใจเจ้าของส่วนและบริบท
- ตรวจจากต้นฉบับที่ความละเอียดจริง; zoom เพื่อดูได้แต่ไม่สร้างรายละเอียดใหม่
- หากใช้ภาพปรับความสว่าง ให้เก็บแยกและระบุผลต่อการตัดสินสี ไม่แก้ทับ original
- แยกข้อเท็จจริงที่เห็นออกจากข้อสันนิษฐาน; ไม่อนุมานบทบาทบุคคลจาก Category_EN หรือเสื้อผ้า
- หากดูหลายเฟรมเพื่อหาตัวบุคคลหรือวัตถุ ให้บันทึกว่ามี temporal assistance; ไม่ใช้เฉลยจากเฟรมอื่นแทน observability ของ target frame โดยไม่ประกาศ protocol
- คำตอบที่ไม่แน่นอนเข้าสู่ adjudication log; ไม่ลบหลักฐาน disagreement หลังได้ข้อยุติ


## 10. เกณฑ์รายงานผลรอบถัดไป
ต้องรายงานจำนวนภาพ/คนที่ตรวจจริง จำนวนไฟล์อ่านไม่ได้ วิธีเลือก หน่วย denominator ความถี่กรณีแบบ multi-label และรายการที่ยังไม่ตัดสิน
แยกจำนวนเหตุการณ์จากภาพและคน; หากรายงานช่วงความไม่แน่นอนต้องพิจารณาการจับกลุ่มตามเหตุการณ์/กล้อง ไม่สมมติว่าภาพต่อเนื่องทั้งหมดอิสระกัน

เอกสารที่เชื่อมกัน:
- BENCHMARK_REQUIREMENTS_DRAFT_TH.md — REQ-01, REQ-08 ถึง REQ-20
- EVIDENCE_AND_HYPOTHESES_TH.md — C01 ถึง C11 และ H-01 ถึง H-06
- P1: DATASET_DETAILS(2).md Rev. 2; ไม่แก้ไขต้นฉบับในรอบนี้
