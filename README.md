# Brain Hub Standard — แม่แบบ (template)

แม่แบบสาธารณะสำหรับสร้าง **Brain** = repo กลางที่เก็บความรู้ งาน และกฎ ให้คนและ AI agent หลายตัวทำงานร่วมกันโดยมี "ความจริงที่เดียว"
ใช้กับงาน data engineering, analytics, data science, AI engineering และ software product

> ⚠️ **repo นี้ห้ามใส่ข้อมูลขององค์กรใดๆ** — ทุกอย่างในนี้เป็นตัวอย่างสมมติ (`classification: public`)
> ข้อมูลจริงให้ใส่ใน instance ที่เป็น **private** ที่สร้างจากแม่แบบนี้เท่านั้น

## มีอะไรในนี้

| ส่วน | คืออะไร |
|---|---|
| [SPEC.md](SPEC.md) | มาตรฐาน: บทบาท โครงสร้างโฟลเดอร์ ชนิดโน้ต กฎสถานะ ความปลอดภัย |
| [PRINCIPLES.md](PRINCIPLES.md) | หลักการทำงานที่ทุก agent ต้องถือ |
| [governance/](governance/AGENTS.md) | กฎที่มนุษย์แก้เท่านั้น (agent อ่านก่อนเริ่มงานทุกครั้ง) |
| `knowledge/` `decisions/` `repos/` `work/` `research/` | ที่เก็บความรู้และงานของ instance (ในแม่แบบมีแค่ `index.md`) |
| [templates/](templates/index.md) · `schemas/` | แม่แบบโน้ตและกติกาที่เครื่องตรวจได้ (JSON Schema) |
| `scripts/` · `tests/` | ตัวตรวจ (validator), ตัวอัปเกรด, ตัวติดตั้ง skill และชุดทดสอบ |
| [examples/](examples/index.md) | ตัวอย่างสมมติของระบบ `ExampleMarket` |
| [docs/](docs/SETUP-GITHUB.md) | คู่มือตั้งค่า |

## ระดับการใช้งาน (L1 / L2 / L3)

| ระดับ | หมายถึง | เหมาะกับ |
|---|---|---|
| **L1 Structured** | ใช้โครงสร้างโฟลเดอร์ + template + frontmatter ทำงานด้วยมือ | เริ่มต้น |
| **L2 Gated** | L1 + CI ตรวจอัตโนมัติ 3 ตัว + รับงานทาง PR เท่านั้น + CODEOWNERS + branch protection | ใช้จริงคนเดียวหรือทีมเล็ก |
| **L3 Orchestrated** | L2 + Conductor ที่จ่ายงานให้ agent ตาม routing + run log + งานตรวจตามรอบ | เมื่อรูปแบบงานนิ่งแล้ว |

แนะนำ: เริ่ม L1 → L2 ก่อน (SPEC §13, §15)

## สร้าง instance ของคุณ

1. บนหน้า repo นี้ (เหนือรายการไฟล์) กด **Use this template** → **Create a new repository**
2. เลือก Owner ตั้งชื่อ repo ตั้ง visibility เป็น **Private** → กด **Create repository from template**
   (repo ใหม่เริ่มด้วย commit เดียว ไม่มีประวัติร่วมกับแม่แบบ — จึงอัปเกรดด้วย `scripts/upgrade-core` แทนการ merge)
3. ใน repo ใหม่ แก้ไฟล์เหล่านี้ (เป็นงานของมนุษย์ เพราะอยู่ใน `governance/` หรือ `.github/`):
   - `governance/profile.yml` → `role: instance` และใส่ระดับชั้นที่รับได้ เช่น `[public, internal, confidential]`
   - `.github/CODEOWNERS` → เปลี่ยนเป็นชื่อบัญชี GitHub ของคุณ
4. ตั้ง branch protection และ secret scanning ตาม [docs/SETUP-GITHUB.md](docs/SETUP-GITHUB.md)
5. ติดตั้ง skill ที่จำเป็น: `python scripts/install-skills` (ดูแผน) แล้ว `python scripts/install-skills --apply`
6. (ถ้าใช้ห้องแชท) เชื่อมแบบอ่านอย่างเดียวตาม [docs/SETUP-CLAUDE-CHAT.md](docs/SETUP-CLAUDE-CHAT.md)
7. เมื่อแม่แบบออกเวอร์ชันใหม่ อัปเกรดตาม [docs/UPGRADING.md](docs/UPGRADING.md)

## ตัวอย่างการใช้แบบคนเดียว

1. คุยในห้องแชท (อ่าน Brain แบบอ่านอย่างเดียว) จนรู้ว่าต้องทำอะไร → ให้ช่วยร่าง **prompt card** (task card สถานะ `inbox`)
2. ส่ง card ให้ coding agent ในเครื่อง agent ทำงานบน branch `agent/<task-id>` เสนอความรู้ใหม่เป็น `unverified` และเขียน handoff
3. agent push branch และเปิด PR → CI ตรวจ `structure`, `guards`, `freshness`
4. คุณอ่าน handoff (ดูว่าอะไร "ไม่ได้รัน") และ Files changed แล้วกด merge
5. ถ้ามีหลักฐานพอ คุณ (Approver) เปิด PR ยกสถานะเป็น `proven` เอง — agent ทำแทนไม่ได้

ตรวจในเครื่องได้ด้วย (ต้องมี Python 3.10+ และ `pip install -r scripts/requirements.txt`):

```
python scripts/validate.py all
python tests/run_tests.py
```

## License

[MIT](LICENSE) — skill หรือเครื่องมือบุคคลที่สามที่ instance ติดตั้งเพิ่มมี license ของตัวเอง (ดู `skills.lock.yml` และ [docs/RISKS.md](docs/RISKS.md) ข้อ 17)

---

## English summary

- A public **template** for a "Brain": one git repo that holds knowledge, task cards and rules for humans and multiple AI agents.
- **No organisation data here** — everything is fictional and `public`. Real data goes into a **private instance** created with *Use this template*.
- `SPEC.md` defines roles (Channel is read-only; Sentinel and Reviewer are read-only), note types, the evidence rules for `proven`, security, and conformance levels L1 → L2 → L3.
- `governance/` is human-only. CI (`structure`, `guards`, `freshness`) validates frontmatter schemas, ids, links, status rules, governance and classification guards, and common secret patterns.
- `scripts/upgrade-core` upgrades only template-owned paths of an instance from a template tag; `scripts/install-skills` installs pinned skills from `skills.lock.yml`.
- Documentation is primarily in Thai. Licensed under MIT.
