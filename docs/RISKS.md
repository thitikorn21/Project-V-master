# Risk register — Brain Hub Standard v0.1.0

ปรับจากรีวิวความเสี่ยงของร่าง v0.1 ให้ตรงกับ SPEC v0.1.0 · ระดับ: 🔴 สูง · 🟠 กลาง · 🟡 ต่ำ

## 1. ความเสี่ยง

| # | ความเสี่ยง | เกิดอย่างไร | ระดับ | ลดด้วย (SPEC) | ที่ยังเหลือ |
|---|---|---|---|---|---|
| 1 | **ความจริงปนเปื้อน** | ข้อสรุปผิดถูก merge → ทุก agent ใช้ต่อ ผิดทั้งระบบ | 🔴 | §5.2 สถานะ + evidence, agent ยก `proven` เองไม่ได้ (CI), §1.6 | มนุษย์อนุมัติผิดได้ — ใช้ evidence ที่ CI รันซ้ำได้ให้มากที่สุด |
| 2 | **Prompt injection** | handoff/เอกสารภายนอก/ข้อมูลมีข้อความสั่ง agent | 🔴 | §9.1 ความรู้ = ข้อมูล, `governance/AGENTS.md` §2, governance แยก | ไม่มีวิธีกันได้ 100%; ลดผลด้วยสิทธิ์น้อยที่สุด |
| 3 | **Conductor สิทธิ์เต็ม** | agent สิทธิ์เต็ม + โมเดลถูกหลอก = รันอะไรก็ได้ | 🔴 | §8 allowlist, ไม่ถือ prod credential, PAUSE | ต้องตั้งสิทธิ์ระดับระบบจริง ไม่ใช่แค่ใน config |
| 4 | **Credential รั่ว** | token อยู่ใน env ของหลาย agent / หลุดเข้า repo | 🔴 | §9.3 secret store, check `guards` (secrets), secret scanning + push protection ของ GitHub | ต้องเลือก secret store ของ instance; pattern ของ `guards` จับได้เฉพาะรูปแบบที่รู้จัก |
| 5 | **ข้อมูลไปถึงผู้ให้บริการโมเดลที่ไม่ควร** | context ลับถูกส่งเข้าโมเดลที่เก็บข้อมูล/นำไปเทรน | 🔴 | §9.4 classification ต่อโน้ต + ต่อ executor, classification-guard | ต้องตรวจนโยบายของผู้ให้บริการแต่ละรายเป็นระยะ |
| 6 | **อนุมัติตัวเอง** | executor เขียน + reviewer ตัวเดียวกัน + auto-merge | 🟠 | §2 แยก role, §7 tiers, subagent reviewer อ่านอย่างเดียว | ใช้คนเดียวด้วยบัญชีเดียว = GitHub บังคับผู้อนุมัติไม่ได้ (ดูข้อ 18) |
| 7 | **งานชนกัน** | 2 agent แก้ไฟล์/งานเดียวกัน | 🟠 | §5.3 claim + expiry, §8 1 task = 1 branch | merge conflict ใน Brain ยังเกิดได้ → โน้ตเล็ก ลดโอกาส |
| 8 | **ความจริงล้าสมัย** | โค้ด/กฎแพลตฟอร์มเปลี่ยน แต่โน้ตยังบอก `proven` | 🟠 | §5.2 effective dates, §6.4 needs-reverify, §10, check `freshness` | ขึ้นกับว่า work repo ประกาศ `entities_written` ครบ; `freshness` เตือนอย่างเดียว |
| 9 | **Loop วิ่งไม่หยุด / ค่าใช้จ่ายบาน** | DQ fail → task → fail → task ... | 🟠 | §8 circuit breaker, budget, dedupe, เพดาน | — |
| 10 | **คอขวดที่มนุษย์** | งานรออนุมัติกองจนระบบช้า | 🟠 | §7 R0/R1 auto-merge ได้ | ต้องปรับเกณฑ์ tier หลังใช้จริง |
| 11 | **Context ล้น** | vault โต agent อ่านไม่หมด/อ่านผิดโน้ต | 🟠 | §11 โน้ตเล็ก, index, context pack (CI ตรวจว่าพาธใน `context` มีจริง) | อาจต้องเพิ่ม search/embedding index ในอนาคต |
| 12 | **ผูกกับเครื่องมือ** | wikilink ไม่ render บน GitHub, พึ่ง plugin | 🟡 | §11 relative link, ไม่พึ่ง plugin, `.obsidian/app.json` | — |
| 13 | **ระบบหนักเกินไปสำหรับคนเดียว** | template/สถานะเยอะ → เลี่ยงไม่ใช้ | 🟠 | §13 L1→L2→L3, §15 โปรไฟล์ใช้คนเดียว | ต้องลดฟิลด์บังคับถ้าใช้จริงแล้วติด |
| 14 | **ข้อมูลจริงหลุดขึ้น master public** | copy ตัวอย่างจาก instance | 🟠 | §14 + classification-guard (`profile.yml` ของ master รับแค่ `public`) | guard ตรวจแค่ป้าย classification ไม่ได้อ่านความหมาย — ต้องรีวิวด้วยตาก่อน merge |
| 15 | **ผลงาน agent ไม่คงที่** | โมเดลต่างกัน คุณภาพต่างกัน | 🟡 | §5.3 acceptance ตรวจด้วยเครื่อง, §5.5 บันทึก model | — |
| 16 | **Conductor ไม่มีเครื่องรัน** | ตัวรันอยู่บนเครื่องที่ปิด → ระบบหยุด | 🟡 | (เรื่องของ instance) §8 ใช้ scheduler บนคลาวด์หรือ CI ได้ | ต้องเลือก host ที่เปิดตลอด |
| 17 | **ใช้เครื่องมือผิดเงื่อนไข vendor / license** | (ก) เอา login แบบบุคคลของเครื่องมือหนึ่งไปใช้ในระบบอัตโนมัติหรือเครื่องมืออื่น (ข) ใช้เครื่องมือ/skill/plugin บุคคลที่สามที่ license ไม่อนุญาตกับงานองค์กร เช่น ห้ามใช้เชิงพาณิชย์ | 🟠 | §8 ช่องทางทางการ + ตรวจ license ก่อนใช้, §16 `skills.lock.yml` บันทึก `license` ทุกรายการ | ต้องตรวจซ้ำเมื่อ vendor เปลี่ยนเงื่อนไขหรือเมื่ออัปเดต ref ใน lock; license ของโฟลเดอร์ย่อยอาจต่างจากทั้ง repo |
| 18 | **การป้องกัน governance ถูกข้ามได้** | agent ใช้บัญชีที่เป็น admin (เช่น บัญชีเดียวกับเจ้าของ) → แก้ branch protection, merge เอง, หรือแก้ไฟล์ผ่าน shell แทนเครื่องมือแก้ไฟล์ | 🔴 | §9.1 CODEOWNERS + branch protection + governance-guard + deny rule, [SETUP-GITHUB.md](SETUP-GITHUB.md) ทางเลือก A | ทุกชั้นกันได้เฉพาะ agent ที่ทำตามกฎ; ต้องให้ agent ใช้บัญชีแยกที่ไม่ใช่ admin |
| 19 | **agent แก้ workflow ของ CI เอง** | CI แบบ `pull_request` รัน workflow จาก branch ของ PR → branch ของ agent แก้ให้ check ผ่านเสมอได้ | 🟠 | CODEOWNERS ครอบ `.github/` → ต้องให้มนุษย์รีวิว (เมื่อตั้ง "Require review from Code Owners") | ถ้าใช้ทางเลือก B ของ SETUP-GITHUB ข้อนี้ไม่มีอะไรบังคับ ต้องดู Files changed ทุกครั้ง |
| 20 | **ข้อยกเว้น bootstrap ของ governance-guard** | ถ้า `main` ไม่มี `governance/` เลย branch agent สร้างได้ (ใช้ตอนสร้างแม่แบบ/instance ครั้งแรก) | 🟡 | แสดงคำเตือนใน check `guards`; การลบ governance ทั้งโฟลเดอร์ออกจาก main ต้องผ่าน PR ที่มนุษย์รีวิว | — |
| 21 | **dependency ของ validator** | CI ติดตั้ง `jsonschema`, `pyyaml` จาก PyPI | 🟡 | ตรึงเวอร์ชันใน `scripts/requirements.txt`, action ตรึง commit SHA | ยังไม่ได้ตรึงด้วย hash ของไฟล์ |

## 2. สิ่งที่ตั้งใจยังไม่ใส่ใน v0.1.0

- ข้อมูลจริงขององค์กร, ชื่อระบบ/ตาราง/ช่องทางจริง (จะไม่มีใน master ตลอดไป)
- search/embedding index
- การ publish ไปเครื่องมือของทีม (เช่น wiki) ทางเดียว
- metric ของระบบเอง (lead time ต่อ task, อัตรา reverify)
- Conductor อัตโนมัติสำเร็จรูป (SPEC กำหนดแค่ข้อบังคับ)

## 3. คำถามที่ยังเปิด

1. ชื่อมาตรฐาน — ตอนนี้ใช้ชื่อชั่วคราว "Brain Hub Standard"

ตัดสินแล้ว: license = MIT · ภาษาเอกสารหลัก = ไทย (มีสรุปอังกฤษใน README) · รูปแบบลิงก์ = markdown relative link
