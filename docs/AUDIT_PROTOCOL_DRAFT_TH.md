# แผนสำรวจข้อมูลรอบถัดไป — DRAFT

ฉบับทบทวน 22 ตุลาคม 2026: ใช้ [ผลตรวจฐานงาน](../reports/README.md) และ [ขอบเขต/DEC](BENCHMARK_REQUIREMENTS_DRAFT_TH.md) วางการสำรวจเพื่อค้นหาปัญหา ยังไม่เลือกภาพจริง ไม่เปิดตรวจภาพเพิ่ม ไม่กำหนด specification หรือคู่มือ annotation ฉบับใช้งาน

## 1. คำถามที่ต้องตอบและหลักฐานที่ต้องใช้

| คำถาม | metadata/หลักฐานต้นทางตอบได้เพียงใด | ต้องดูภาพในรอบที่อนุญาตภายหลังเพื่ออะไร |
| --- | --- | --- |
| ภาพมาจากไหนและครอบคลุมอะไร | ตรวจ snapshot/export, site×camera×date/time และ unknown; ต้องขอวิธีสร้าง event/ขอบเขตข้อมูลที่ไม่ได้ export | ตรวจความต่างสภาพภาพ ไม่ใช้ sample ยืนยันความเป็นตัวแทนของทุกเฟรมในระบบ |
| ประวัติคัดเลือกเชื่อมกันอย่างไร | ขอ curation snapshot/notes/version แล้ว join ด้วย key ที่พิสูจน์ได้; ห้าม row-order join | ตรวจกรณีคลุมเครือภายหลัง โดยไม่แก้ raw status |
| category ผูกกับใคร/เวลาอะไร | มีเพียง record label และ incident_timestamp; ต้องมี source dictionary/event ID ก่อนยืนยันความหมาย | การเห็นคนไม่พิสูจน์บทบาท และภาพเดียวอาจมีหลายคน; ไม่เดาอัตลักษณ์ |
| คน/ส่วน/เสื้อผ้ามองเห็นได้เพียงใด | ไม่มี geometry/person count/modality fields ให้สรุปจาก metadata | สำรวจขนาดที่เห็น occlusion/truncation ส่วนที่แยกได้ และความกำกวม ownership |
| สี/ความยาว/ลวดลายสมเหตุผลหรือไม่ | ไม่มีค่าคุณลักษณะอ้างอิง | ตรวจ observability/แสง/compression; ภาพขาวดำไม่พิสูจน์ว่าเป็น IR และเวลาไม่แทนสภาพแสง |
| ภาพซ้ำหรือเป็นเหตุการณ์เดียวกันหรือไม่ | filename ไม่ซ้ำไม่พิสูจน์เนื้อหาไม่ซ้ำ; กล้อง+เวลาชี้ได้เพียง candidates | ตรวจ byte identity/ความคล้าย/บริบทต่อเนื่องตามแผนข้อ 4 ไม่สรุปบุคคลเดิมจากเวลาติดกัน |

## 2. ลำดับงานและจุดทบทวน

1. **ก่อนเลือกตัวอย่าง:** ยืนยันลำดับความสำคัญของ task กับผู้ใช้และหาต้นทาง curation/dictionary หากยังขาด ให้จำกัด scope และระบุสถานะ unknown แทนการรอหรือเติมคำตอบเอง บันทึก source snapshot ID/hash ของ metadata, รายการ archive parts, audit ID, config/code revision ที่ใช้; ยังไม่แต่ง source-system version หรือประกาศ release
2. **metadata-only:** ใช้ inventory/linkage/format comparison เดิมเมื่อ checksums ยังใช้ได้ ตรวจเพิ่มเฉพาะความไม่แน่นอน เช่น schema เปลี่ยน คีย์กำกวม หรือได้ curation export ใหม่ เก็บ raw/normalized แยก; ห้ามเปลี่ยน selected/rejected/flagged/pending หรือเขียนต้นทาง
3. **เสนอ sampling frame ให้ตรวจทาน:** สรุป strata ที่มีจริงและช่องที่ยังไม่มี ไม่ทำ Cartesian product ทุก field จนงานบานปลาย จัด coverage กับ edge-case discovery แยก membership และเหตุผล; รอบปัจจุบันยังไม่สร้าง membership
4. **เมื่ออนุญาตรอบสำรวจภาพ:** เปิดแบบจำกัดภาระครั้งละภาพ/กลุ่มสั้น ใช้ original เพื่อดูรายละเอียด เก็บ observation/uncertainty และ provenance ภายนอก โดยยังไม่ทำ pixel annotation/โมเดล หยุดพักทบทวนเมื่อครบงบแรกหรือพบประเด็นเปลี่ยน scope
5. **สรุปเพื่อออกแบบ:** coverage ที่ทำจริง/ที่ขาด, ambiguity log, candidate alternatives และคำถามสำหรับ pilot; ขอการตัดสินก่อนใช้เป็น specification/pilot ไม่เลื่อนเป็น accepted อัตโนมัติ

ทุกครั้งอ่าน source แบบ read-only ไม่ตาม symlink เพิ่ม scope เอง stat ก่อน–หลังและ hash bytes ที่ใช้อ้าง หาก source เปลี่ยนให้แยก snapshot/retry แบบจำกัด ไม่หยุดแอปหรือ lock ต้นทาง ใช้ run ใหม่ใต้ external work_root/runs และเก็บไฟล์เก่าไว้

## 3. การเลือกตัวอย่างที่เสนอและขนาดงานเริ่มต้น

**ข้อเสนอเพื่อประเมินภาระ ไม่ใช่จำนวนชุดประเมิน:** เริ่มรอบทำงานที่ประมาณ **32 ภาพไม่ซ้ำ** แบ่ง coverage ราว 24 และ edge-case discovery ราว 8; ถ้ากรณีเป้าหมายซ้อนกัน ให้ tag ทั้งสองเหตุผลโดยนับภาพจริงครั้งเดียว ตัวเลขนี้ยังไม่อนุมัติ และไม่ใช่ขนาดตัวอย่างเชิงสถิติหรือจำนวน annotation pilot

เหตุผลคือ metadata มีหลายกลุ่มกล้องและช่วงเวลา มากกว่างบเปิดดูละเอียดครั้งเดียว จึงเริ่มขนาดที่ตรวจบริบทและบันทึกข้อสงสัยรายภาพได้ แล้วปรับจากเวลาทำจริง ยังไม่อ้างว่าครอบคลุมทุกกล้อง ทุกคู่ปัจจัย หรือพบ rare case ครบ

- **Coverage:** กระจายกลุ่ม site/camera ที่ทราบ รวม unknown แยกกลุ่ม; หมุนกล้อง วัน และช่วงชั่วโมงที่มีจริง หลีกเลี่ยงให้กล้องที่มี records มากครองตัวอย่าง อาจใช้ช่วงชั่วโมง 6 ชั่วโมงเป็น proxy เริ่มต้น แต่ไม่เรียก day/night หรือ IR จนมีหลักฐานภาพ/ระบบ เลือกด้วย seed/กติกาที่บันทึกได้หลังยืนยัน frame; อย่าแทนกล้องที่ยังไม่ดูด้วยกล้องที่ดูแล้ว
- **Edge-case discovery:** อาศัยประเด็นจาก visual report เดิมเป็นเบาะแส เช่นคนเล็ก/บัง/ชิดขอบ/สีตัดสินยาก และ candidate กล้อง/เวลาห่างสั้นที่ metadata ชี้ได้ ความยากต้องยืนยันด้วยภาพ ไม่จัดจาก category หรือเวลาล้วน หากหาเคสไม่ได้ให้บันทึก not found ไม่เติมสมมติฐาน
- **เมื่อได้ curation linkage:** เพิ่ม coverage ของผลคัดแต่ละประเภทตามความหมายจริง ไม่แบ่ง strata ตาม pending เพื่อแทนผลคัดเก่า และไม่ต้องเปลี่ยน raw status เพื่อทำ sampling
- **เงื่อนไขขยาย:** ถ้างบแรกไม่ครอบคลุมกลุ่มที่จำเป็น หรือพบ ambiguity/รูปแบบใหม่ที่เปลี่ยน candidate/คู่มือ ให้เสนอเพิ่มรอบละประมาณ 8 ภาพเฉพาะช่องว่าง พร้อมเหตุผลและเวลาคงเหลือ หากถึงราว 48 ภาพในรอบแรกแล้วยังมีปัญหาเชิงนิยาม/ที่มา ให้ทบทวนแผนกับผู้ใช้ก่อนขยายต่อ ไม่ใช้จำนวนนี้เป็นเกณฑ์คุณภาพหรือหลักประกัน saturation

coverage และ discovery ไม่ใช่ probability sample ของประชากรทั้งหมด ไม่รวมสองกลุ่มเพื่อประมาณ prevalence เว้นแต่มี sampling design/weights รองรับ เก็บ strata ที่ยังไม่ดูและเหตุผลการข้ามทุกครั้ง

## 4. ภาพซ้ำ ภาพต่อเนื่อง และการแยกชุดประเมิน

- **Exact duplicate:** ในขั้นที่ได้รับอนุญาตให้อ่าน payload ให้เทียบ SHA256 ของ encoded image bytes; ZIP CRC/size ใช้คัด candidates เท่านั้น กรณี bytes ต่างแต่ภาพเหมือนให้บันทึกต่างชนิด ไม่ลบ/เปลี่ยนชื่อหรือคัดออกเอง
- **Near duplicate:** เริ่มจาก candidates ที่มีบริบทกล้อง/เวลา หากจำเป็นค่อยเสนอกระบวนการ perceptual similarity พร้อม threshold sensitivity และ manual verification ห้ามติดตั้งเครื่องมือหรือใช้โมเดลจากแผนนี้เอง
- **ภาพต่อเนื่อง:** ใช้ incident_timestamp พร้อม offset และ site+camera เป็น candidate neighborhood เท่านั้น ทดลองเปรียบเทียบช่วงห่าง เช่น 5/30/60 วินาทีเพื่อดูว่ากลุ่มเปลี่ยนอย่างไร ไม่เลือกเป็น cut-off จริงจากตัวเลขนี้ ช่วงห่างใกล้ไม่ยืนยัน event/person เดียว และช่วงห่างไกลไม่ยืนยันอิสระ; event IDs/ลำดับจากต้นทางมีน้ำหนักมากกว่าการเดาจากชื่อไฟล์
- เก็บ `candidate_group`, `group_basis`, `verification_state`, membership และหลักฐานเป็นผลสำรวจแยกจาก curation ไม่สร้างกลุ่มบุคคลข้ามกล้องโดยอนุมานตัวตน
- ชุดที่ใช้ค้นหาปัญหา/แก้คู่มือคือ **development/discovery** ต้องมีประวัติ exposure แยกจาก final evaluation ยังไม่เลือกสมาชิก final หรือบังคับ train/validation/test ภายหลังต้องจัดการ overlap ของภาพซ้ำ/กลุ่มที่ยืนยันแล้วก่อนตรึง membership; หากแยกไม่ได้ให้บอกข้อจำกัด ไม่อ้าง independence

## 5. สิ่งที่จะบันทึกขณะสำรวจ

ใช้ [visual sample manifest](../templates/visual_sample_manifest.csv), [case register](../templates/visual_case_register.csv) และ [เคส K/X](CASE_REGISTER_DRAFT_TH.md) เดิมเป็นฐาน ปรับเฉพาะเมื่อเริ่ม run จริง ไม่สร้าง annotation schema สุดท้ายจาก header ของ template

| กลุ่มข้อมูล | สิ่งที่จะเก็บภายนอก Git |
| --- | --- |
| Provenance/linkage | run ID, source/metadata hash, row locator ภายใน snapshot, filename/member ID, match method/ambiguity; row locator ไม่ใช่ stable event ID |
| Selection | coverage/discovery tags, strata, seed/กติกาเลือก, เหตุผลรวม/ข้าม, replacement และ duplicate/group candidates |
| Observation | ผู้ดู/เวลา/วิธีดู/การแสดงภาพ, รายงานเดิมหรือเปิดใหม่, จำนวนคนโดยประมาณและความไม่แน่ใจ, overlap/truncation/scale/เสื้อผ้า/แสงที่สังเกตได้, K/X และเคสใหม่ |
| Attribute questions | candidate ใดมีหลักฐานแยกได้, absent/not applicable/unobservable/unreviewed พร้อมเหตุผล; ยังไม่สร้าง class IDs/สีบังคับหรือบังคับกรอกคุณลักษณะที่ผู้ใช้ยังไม่ต้องการ |
| Measurements เมื่อทำจริง | bbox height(px), bbox area/frame area และ visible-mask area/frame area ต้องแยกหน่วย; ไม่วัด mask area เมื่อไม่มี mask หรืออ้างขนาดคนจากขนาด frame อย่างเดียว |
| Review/change | reviewer, uncertainty/conflicting readings, เวลาใช้จริง, สิ่งที่ต้องขอคำอธิบาย, DEC ที่เกี่ยวข้อง และผู้ตัดสิน; review ไม่เท่ากับ annotation agreement |

ไม่เก็บข้อสันนิษฐานอัตลักษณ์หรือบทบาทรายคนจาก category เพียงอย่างเดียว Preview/contact sheet ถ้าจำเป็นในอนาคตต้อง local-only และย้อนกลับ original ได้

## 6. ผลสำรวจจะใช้ตัดสินอะไร

| ผลที่ต้องได้ | การตัดสินที่จะรองรับภายหลัง |
| --- | --- |
| ข้อจำกัดจำนวนคน/scale/owner/ส่วนที่เห็นและตัวอย่างกำกวม | full-frame vs crop, coarse/fine/side/accessory candidates และ denominator ที่เหมาะกับ task |
| observability ของสี/ความยาว/ลาย และภาระบันทึก | เก็บเป็นงานหลัก/ส่วนขยาย/เลื่อนออก; observed vs physical color; applicability/unknown ไม่กำหนด palette จาก paper โดยตรง |
| ปัญหานิยามและการอ่านต่างกัน | เตรียม guideline pilot/ผู้ทำ/การตรวจอิสระและ adjudication; ยังไม่สรุป reliability หรือ QA threshold จาก exploration |
| coverage, curation linkage และ duplicate/group uncertainty | ประชากรที่สรุปผลได้ เหตุผลเลือกชุดประเมิน และวิธีหลีกเลี่ยง leakage; ยังไม่กำหนด final quota/split หรือเกณฑ์คัดออก |

ไม่เริ่ม annotation, inference, training หรือ benchmark ตามแผนฉบับนี้ การจะเริ่ม pilot ต้องมีขอบเขต/ผู้ทำ/คู่มือร่างและวิธีเก็บผลที่ทบทวนแล้วตาม [REQ/DEC](BENCHMARK_REQUIREMENTS_DRAFT_TH.md)
