---
spec: brain-hub-standard
spec_version: 0.1.0
status: released
---

# Brain Hub Standard — SPEC v0.1.0

มาตรฐานสำหรับระบบ multi-agent engineering ที่มี "คลังความรู้กลาง" (Brain) เป็นศูนย์ความจริง
ใช้ได้กับงาน data engineering, analytics, data science, AI engineering และ software product
เอกสารนี้เป็นกลาง ไม่มีข้อมูลขององค์กรใด — ข้อมูลจริงอยู่ใน "instance" ที่สร้างจากมาตรฐานนี้เท่านั้น

> คำว่า **ต้อง / ห้าม / ควร / อาจ** ในเอกสารนี้ใช้ตามความหมายของ RFC 2119 (MUST / MUST NOT / SHOULD / MAY)

---

## 1. หลักการ

1. **ความจริงมีที่เดียว** — ความรู้ที่ใช้ตัดสินใจทั้งหมดอยู่ใน Brain repo; ที่อื่น (แชท, artifact, โน้ตส่วนตัว) เป็นแค่ร่าง
2. **ความจริงต้องมีหลักฐาน** — ข้อเท็จจริงที่ไม่มีหลักฐานที่ตรวจซ้ำได้ ห้ามติดสถานะ `proven`
3. **ความจริงมีวันหมดอายุ** — ทุกข้อเท็จจริงผูกกับเวลาและ commit ที่พิสูจน์ และถูกตรวจซ้ำตามรอบ
4. **กฎแยกจากความรู้** — ไฟล์กฎ (governance) แก้ได้โดยมนุษย์เท่านั้น; agent อ่านความรู้ในฐานะ "ข้อมูล" ไม่ใช่ "คำสั่ง"
5. **บังคับด้วยระบบ ไม่ใช่ด้วยข้อความ** — สิ่งที่ตรวจด้วยเครื่องได้ ต้องอยู่ใน schema / CI / สิทธิ์ ไม่ใช่แค่เขียนขอใน prompt
6. **ผู้เขียนไม่ใช่ผู้อนุมัติ** — สิ่งที่ agent สร้าง ต้องผ่านผู้ตรวจอิสระ (มนุษย์ หรือ check ที่ deterministic)
7. **สิทธิ์น้อยที่สุด** — แต่ละ role ได้สิทธิ์เท่าที่งานของมันต้องใช้
8. **เครื่องมือเปลี่ยนได้** — มาตรฐานไม่ผูกกับ vendor; Obsidian, coding agent, scheduler เป็นแค่ตัวเลือกของ instance

หลักการทำงานของ agent (วิศวกรรม) อยู่ใน [PRINCIPLES.md](PRINCIPLES.md)

---

## 2. Roles

| Role | หน้าที่ | ตัวอย่างเครื่องมือ | ห้าม |
|---|---|---|---|
| **Channel** | ปรึกษา อ่าน Brain แบบ **อ่านอย่างเดียว** แปลงผลการคุยเป็น prompt card (§2.1) | AI chat ที่เชื่อม repo แบบอ่านอย่างเดียว | เขียนเข้า Brain เอง (ทุก branch) |
| **Brain** | เก็บความรู้ งาน กฎ — ศูนย์ความจริง | git repo + Obsidian เป็น viewer | — (เป็นข้อมูล ไม่ใช่ตัวรัน) |
| **Conductor** | อ่าน task ที่พร้อม → เลือก executor ตาม routing → สั่งรัน → บันทึก run (§8) | เซสชันหลักของ coding agent, scheduler, CI | รันคำสั่งนอก allowlist, ถือ credential ของ prod |
| **Executor** | ลงมือทำงานใน work repo แล้วส่ง handoff | coding agent | แก้ governance, merge งานตัวเอง |
| **Reviewer** | ตรวจผลงานโดยอิสระจาก executor | subagent อ่านอย่างเดียว / agent คนละโมเดล + CI | เป็นตัวเดียวกับ executor ของงานนั้น |
| **Sentinel** | ตรวจ pipeline / คุณภาพข้อมูล / ความสดของโน้ตตามรอบ แล้วรายงาน | subagent อ่านอย่างเดียว + งานตามรอบ | แก้ไฟล์ใดๆ เอง; สร้างได้เฉพาะ task card สถานะ `inbox` |
| **Approver** | อนุมัติงานเสี่ยงสูงและการยกสถานะเป็น `proven` | มนุษย์ | — |

Role หนึ่งอาจใช้เครื่องมือเดียวกับอีก role ได้ แต่ **Executor กับ Reviewer ของงานเดียวกันต้องแยกกัน**

### 2.1 Channel แบบอ่านอย่างเดียวและ prompt card

- Channel (แชท) อ่าน Brain ผ่านตัวเชื่อมแบบ **อ่านอย่างเดียว** และ **ไม่เขียนกลับ**
- ถ้าผลการคุยทำให้ต้องแก้ Brain ผู้ใช้ต้องส่ง **prompt card** = task card (§5.3) สถานะ `inbox` ที่ `created_by: channel` ให้ Conductor/Executor ทำผ่าน PR ตามปกติ
- prompt card เป็น "คำขอ" ไม่ใช่ "คำสั่งที่ต้องทำทันที" — Conductor ต้องจัดเข้า routing (§7) ก่อนเสมอ

---

## 3. Repo topology

```
            ┌─────────────── Brain repo (1 ต่อ instance) ───────────────┐
Channel ──► │ governance/  knowledge/  decisions/  work/  research/      │
 (อ่านอย่างเดียว) └──────────────▲───────────────────────────┬────────────────┘
                           │ PR (handoff + knowledge)  │ task card
                    work repo A / B / C ◄── Executor ◄─ Conductor
```

- **Brain repo** 1 ตัวต่อ instance มี git ของตัวเอง
- **Work repo** แยกตามงาน แต่ละตัวมี git ของตัวเอง
- Brain **ห้าม** ใส่ซอร์สโค้ดของ work repo ทั้งก้อน และ **ไม่ควร** ใช้ git submodule — อ้างถึงด้วย `repo` + `commit` แทน
- ข้อมูลไหลเข้า Brain ทาง **PR เท่านั้น**

---

## 4. โครงสร้าง Brain repo (instance)

```
brain/
├─ README.md                 แผนที่ repo (ทุกโฟลเดอร์ความรู้มี index.md ของตัวเอง)
├─ governance/               ← มนุษย์แก้เท่านั้น (CODEOWNERS + branch protection)
│  ├─ AGENTS.md              กฎกลางที่ทุก agent ต้องอ่านก่อนเริ่ม
│  ├─ routing.md             ประเภทงาน → executor → risk tier → ต้องอนุมัติไหม
│  ├─ commands.yml           allowlist คำสั่งที่ Conductor รันได้
│  ├─ classification.md      ระดับชั้นข้อมูล และโมเดล/ผู้ให้บริการที่รับได้แต่ละระดับ
│  ├─ profile.yml            ค่าที่ validator ใช้ (เช่น classification ที่ repo นี้รับได้)
│  ├─ local/                 การตั้งค่าเฉพาะ instance
│  └─ PAUSE                  (มีไฟล์นี้ = Conductor หยุดรับงานทั้งหมด)
├─ knowledge/
│  ├─ systems/               ระบบต้นทาง/ปลายทาง (แพลตฟอร์ม, DB, API)
│  ├─ entities/              table, dataset, model, API, service
│  ├─ fields/                นิยาม field ต่อระบบ + เงื่อนไขการใช้
│  ├─ rules/                 กฎธุรกิจ สูตร การคำนวณ
│  ├─ queries/               query/snippet ที่พิสูจน์แล้ว + ผลกระทบยอด
│  ├─ dq/                    data quality check: เกณฑ์ ความถี่ ผลล่าสุด
│  └─ glossary/              คำศัพท์ธุรกิจ ชื่อเรียกหลายภาษา
├─ decisions/                ADR
├─ repos/                    1 โน้ตต่อ work repo
├─ work/
│  ├─ tasks/                 task card (รวม prompt card)
│  ├─ handoffs/              ผลจากแต่ละ run
│  └─ runs/                  log ของ Conductor
├─ research/                 สรุปความรู้ภายนอก (ไม่ใช่ความจริงขององค์กร)
├─ templates/  schemas/  scripts/  docs/
└─ skills.lock.yml           skill ที่ instance ต้องใช้ (§16)
```

---

## 5. Note types และ frontmatter

ทุกโน้ต (ไฟล์ `.md` ในโฟลเดอร์ความรู้ ยกเว้น `index.md` และ `README.md`) **ต้อง** มี YAML frontmatter ที่ผ่าน JSON Schema ใน `schemas/`
คีย์ที่ไม่อยู่ใน schema ใช้ได้ถ้าขึ้นต้นด้วย `x-` (สำหรับ instance); คีย์อื่นที่ไม่รู้จัก = ผิด (กันพิมพ์ผิด)

### 5.1 ฟิลด์ร่วม (ทุก type)

| key | ค่า | บังคับ |
|---|---|---|
| `id` | ไม่ซ้ำทั้ง repo ขึ้นต้นด้วย prefix ของ type (ตารางล่าง) เช่น `fld-<system>-<name>` | ✓ |
| `type` | `system \| entity \| field \| rule \| query \| dq \| glossary \| decision \| repo \| task \| handoff \| run \| research` | ✓ |
| `title` | ข้อความ | ✓ |
| `classification` | `public \| internal \| confidential \| restricted` | ✓ |
| `spec_version` | เวอร์ชันมาตรฐานที่โน้ตนี้ใช้ (semver) | ✓ |
| `created` / `updated` | ISO date `YYYY-MM-DD` | ✓ |
| `tags` | list | — |

prefix ของ id: `sys-` system, `ent-` entity, `fld-` field, `rule-` rule, `qry-` query, `dq-` dq, `gls-` glossary, `adr-` decision, `repo-` repo, `task-` task, `ho-` handoff, `run-` run, `rsch-` research

### 5.2 Knowledge notes (`system, entity, field, rule, query, dq, glossary`)

| key | ความหมาย |
|---|---|
| `status` | `proposed → unverified → proven → deprecated` หรือ `conflicted` (บังคับ) |
| `evidence` | list ของ `{kind: query\|reconciliation\|test\|doc\|observation, ref, result, run_id}` |
| `verified_at` / `verified_commit` / `verified_by` | เวลา, commit ของ repo ที่ใช้พิสูจน์ (ใส่ในเครื่องหมายคำพูด เช่น `"481522143b75"` เพราะ YAML อ่าน commit ที่เป็นตัวเลขล้วนเป็นตัวเลข), ผู้ตรวจในรูป `human:<ชื่อ>` หรือ `check:<check-id>` |
| `effective_from` / `effective_to` | ช่วงเวลาที่กฎ/นิยามนี้มีผล (กฎของแพลตฟอร์มเปลี่ยนได้) |
| `source_system` | ระบบต้นทางของความจริงนี้ (บังคับสำหรับ `field`) |
| `review_after` | วันที่ต้องตรวจซ้ำ |
| `supersedes` / `superseded_by` | id ของเวอร์ชันก่อน/หลัง |
| `conflicts_with` | list ของ id ที่ขัดกัน (ใช้กับ `conflicted`) |
| `written_by` | `{role, tool, run_id}` ที่สร้าง (provenance) |

**กฎสถานะ** (ตรวจด้วย CI §12)
- agent สร้างได้แค่ `proposed` / `unverified`
- `proven` ต้องมี `evidence` ≥ 1 รายการ, `verified_at`, `verified_commit`, `verified_by` **และ** อย่างใดอย่างหนึ่ง:
  (ก) มนุษย์อนุมัติ — `verified_by: human:<ชื่อ>` และการยกสถานะเกิดใน PR ที่มนุษย์รีวิว หรือ
  (ข) evidence เป็น check ที่ CI รันซ้ำได้และผ่าน — `verified_by: check:<id>` และมี evidence `kind: test`, `result: pass`, `ref` ชี้ไฟล์ที่มีอยู่จริงใน repo
- PR จาก branch `agent/*` ที่ทำให้โน้ตกลายเป็น `proven` = CI fail (agent ยกเองไม่ได้) — ยกเว้นไฟล์ใน `examples/` ซึ่งเป็นตัวอย่างสมมติ ไม่ใช่ความจริงขององค์กร (แต่ยังต้องผ่านกฎ evidence ข้างบน)
- การเปลี่ยนสถานะต้องเป็นไปตามลำดับ: `proposed→unverified→proven→deprecated`; สถานะใดก็ไป `conflicted` ได้; `conflicted→unverified|proven|deprecated`; `deprecated` เป็นสถานะสุดท้าย
- ถ้าสองแหล่งขัดกัน ต้องตั้ง `conflicted` และใส่ `conflicts_with` ทั้งสองฝั่ง — **ห้ามเลือกแหล่งเงียบ ๆ**
- ห้ามลบความจริงเก่า ให้ `deprecated` + `superseded_by`

### 5.3 Task card

| key | ความหมาย |
|---|---|
| `status` | `inbox → ready → claimed → running → review → needs-approval → done` / `failed` / `cancelled` |
| `repo` | work repo เป้าหมาย |
| `executor` | role/เครื่องมือ ตาม routing |
| `risk` | `R0–R3` (ดู §7) |
| `context` | list พาธ (เทียบจาก root ของ repo) ของโน้ตที่ executor ต้องอ่าน (context pack) — ต้องมีอยู่จริง |
| `acceptance` | เกณฑ์เสร็จที่ตรวจได้ |
| `budget` | `{max_attempts, max_minutes}` |
| `claimed_by` / `claim_expires` | lock กันสองตัวทำงานเดียวกัน |
| `created_by` | ผู้/ช่องทางที่สร้าง (`channel` สำหรับ prompt card, `sentinel`, `human`) |

### 5.4 Handoff

frontmatter: `task` (id ที่มีอยู่จริง), `run_id`, `executor`, `model`, `started`, `finished`, `outcome (success|partial|failed|skipped)`, `changes` (PR/commit), `checks: {passed, failed, not_run}` — แยกชัด, `knowledge_proposals` (พาธโน้ตที่เสนอ), `open_issues`, `next_steps`

### 5.5 Run log

`run_id, task, conductor_version, command_id, executor, model, exit_code, duration (วินาที), cost, attempt`

### 5.6 Decision (ADR)

frontmatter: `status (proposed|accepted|superseded)`, `supersedes` / `superseded_by`;
เนื้อหาต้องมีหัวข้อ `context`, `options`, `decision`, `consequences` (ดู template)

### 5.7 Repo note และ research note

- `repo`: `repo` (`owner/name`), `purpose`, `default_branch`
- `research`: `sources` list ของ `{title, url, accessed}` — research ไม่ใช่ความจริงขององค์กร จึงไม่มีสถานะ `proven`

---

## 6. Work repo contract

ทุก work repo ที่เข้าระบบ **ต้อง** มี

1. `AGENTS.md` — ชี้กลับไป `governance/AGENTS.md` ของ Brain + กฎเฉพาะ repo
   (เครื่องมือที่อ่านไฟล์ชื่ออื่น เช่น `CLAUDE.md` ให้ import/ชี้มาที่ไฟล์นี้ — มีกฎชุดเดียว)
2. `brain.yml` — manifest: `brain_repo`, `purpose`, `entities_read`, `entities_written`, `allowed_executors`, `default_risk` (schema: `schemas/brain-manifest.schema.json`)
3. Handoff ตาม template ทุกครั้งที่จบงาน
4. CI step ที่ (ก) เปิด PR ส่ง handoff + knowledge proposals เข้า Brain และ (ข) ถ้า PR แตะ entity ใน `entities_written` → ติด tag `needs-reverify` ให้โน้ตที่เกี่ยวข้องใน Brain

---

## 7. Risk tiers และ routing

| Tier | ตัวอย่าง | การ merge |
|---|---|---|
| **R0** | อ่านอย่างเดียว, เอกสาร, โน้ต `proposed` | auto-merge ได้ถ้า CI ผ่าน และ instance อนุญาต |
| **R1** | แก้โค้ดที่ไม่แตะ prod / ไม่เขียนข้อมูลจริง | CI + Reviewer อิสระ; auto-merge ได้ถ้า repo อนุญาต |
| **R2** | แตะ prod data/schema, deploy, credential | มนุษย์อนุมัติ (`needs-approval`) |
| **R3** | ทำลาย/ย้อนไม่ได้: drop, delete, backfill ใหญ่, rotate secret | agent เตรียมแผนเท่านั้น มนุษย์เป็นคนรัน/อนุมัติทีละขั้น |

`governance/routing.md` เป็นตารางตายตัว: ประเภทงาน → executor → tier
Conductor **ห้าม** ตัดสิน routing ด้วยวิจารณญาณของโมเดล; ถ้าไม่ตรงแถวไหน → ส่งกลับ `inbox` พร้อมเหตุผล

---

## 8. Conductor

Conductor เป็น **role** ไม่ใช่ผลิตภัณฑ์ — ทำด้วยเครื่องมือใดก็ได้ (คนกดเอง, coding agent, scheduler, CI) ตราบที่ทำตามข้อบังคับข้างล่าง

**ตัวอย่างอ้างอิงด้วย Claude Code** (ไม่บังคับ):
- เซสชันหลักของ Claude Code ทำหน้าที่ Conductor (อ่าน task → เลือกตาม routing → ลงมือหรือส่งต่อ)
- subagent ใน `.claude/agents/` ทำหน้าที่ Reviewer และ Sentinel (สิทธิ์อ่านอย่างเดียว)
- งานตรวจตามรอบใช้ scheduled task ของเครื่องมือ (เช่น scheduled tasks ในแอป desktop หรือ routines บนคลาวด์ของ Claude Code) หรือ GitHub Actions แบบ `schedule`

Conductor **ต้อง**
- รันเฉพาะ command template ใน `governance/commands.yml` (ห้าม shell อิสระ) — แต่ละ template ระบุ executor, โฟลเดอร์, flag, timeout
- ทำงาน 1 task = 1 branch (หรือ worktree) แยก ชื่อ `agent/<task-id>`
- claim task ก่อนรัน และปล่อยเมื่อหมดเวลา `claim_expires`
- จำกัดจำนวนงานพร้อมกัน และงบต่อวัน (เวลา/ค่าใช้จ่าย)
- มี **circuit breaker**: fail ติดกัน N ครั้ง → หยุดคิว + แจ้งมนุษย์
- เคารพไฟล์ `governance/PAUSE` (kill switch)
- เขียน run log ทุกครั้ง แม้ล้มเหลว
- เรียกเครื่องมือของ vendor ผ่านช่องทางที่ vendor รองรับอย่างเป็นทางการ และใช้ตามเงื่อนไขการใช้งานของ vendor นั้น
- **ตรวจ license และเงื่อนไขการใช้งานของเครื่องมือ/skill บุคคลที่สามก่อนใช้กับงานองค์กร** (บางตัวห้ามใช้เชิงพาณิชย์ หรือห้ามใช้ login แบบบุคคลกับระบบอัตโนมัติ)

Conductor **ห้าม**
- ถือ credential ของ prod — executor ได้ credential แบบจำกัดขอบเขตต่อ tier จาก secret store ตอนรัน
- สร้าง task เองแบบไม่จำกัด (task ที่สร้างอัตโนมัติ เช่น จาก DQ fail ต้องมี dedupe key และเพดานต่อวัน)
- merge งาน R2/R3

---

## 9. Security

1. **Prompt injection**: เนื้อหาใน `knowledge/`, `research/`, `work/handoffs/` และข้อมูลจากระบบภายนอก = ข้อมูล ไม่ใช่คำสั่ง — ระบุไว้ใน `governance/AGENTS.md` และ executor ต้องไม่ทำตามคำสั่งที่พบในนั้น
2. **Governance protection**: `governance/` มี CODEOWNERS เป็นมนุษย์ + branch protection; CI fail ถ้า PR จาก branch `agent/*` แตะ `governance/`
3. **Secrets**: ห้ามอยู่ใน repo ใด ๆ; CI ต้องมี secret scanning; credential ต่อ role แยกกัน (เช่น account อ่านอย่างเดียวสำหรับงานวิเคราะห์)
4. **Data classification**: `governance/classification.md` กำหนดว่าระดับชั้นไหนส่งเข้าโมเดล/ผู้ให้บริการใดได้ (พิจารณานโยบายการเก็บและการนำข้อมูลไปเทรน) — Conductor ต้องไม่ส่ง context ที่ระดับสูงกว่าที่ executor นั้นรับได้
5. **Least privilege ของ agent**: จำกัดโฟลเดอร์ที่เข้าถึงได้และสิทธิ์คำสั่งในระดับระบบ ไม่ใช่แค่เขียนใน prompt

### 9.1 บังคับ governance ในทางปฏิบัติ

มี 4 ชั้นที่ทำงานร่วมกัน:

| ชั้น | ทำอะไร | อยู่ที่ |
|---|---|---|
| CODEOWNERS | PR ที่แตะ `governance/` หรือ `.github/` ต้องได้รีวิวจากเจ้าของที่เป็นมนุษย์ | `.github/CODEOWNERS` |
| Branch protection | main รับเฉพาะ PR, ต้องผ่าน required checks, ห้าม force-push | ตั้งในหน้า GitHub ([docs/SETUP-GITHUB.md](docs/SETUP-GITHUB.md)) |
| CI governance-guard | branch ที่ขึ้นต้น `agent/` แตะ `governance/` = fail | `.github/workflows/validate.yml` |
| Deny rule ของ coding agent | เครื่องมือแก้ไฟล์ของ agent ถูกปฏิเสธใน `governance/**` | `.claude/settings.json` (ถ้าใช้ Claude Code) |

**ข้อจำกัด (ต้องรู้)**: ทั้ง 4 ชั้นกัน agent ที่ "ทำตามกฎ" และกันความผิดพลาดได้ แต่ **agent ที่ไม่ทำตามกฎและถือสิทธิ์ admin ของ repo ยังข้ามได้** (เช่น ปิด branch protection, push ด้วยสิทธิ์ admin, หรือแก้ไฟล์ผ่าน shell แทนเครื่องมือแก้ไฟล์)
ดังนั้น **ห้ามให้ agent มีสิทธิ์ bypass** — agent ควรใช้ GitHub account/token แยกที่มีสิทธิ์แค่ write (ไม่ใช่ admin) และไม่อยู่ใน bypass list
ข้อยกเว้นเดียวของ governance-guard: ตอนสร้าง instance ครั้งแรก ถ้า branch ปลายทางยังไม่มี `governance/` เลย การสร้างโฟลเดอร์นี้ครั้งแรกผ่านได้ (bootstrap) และแสดงคำเตือน

---

## 10. ความสด (staleness) และการตรวจซ้ำ

- ทุก knowledge note ควรมี `review_after` (ค่าเริ่มต้นต่อ type อยู่ใน governance)
- job ตามรอบ (Sentinel) สร้างรายงานโน้ตที่เลยกำหนด / ติด tag `needs-reverify` → เปิด task ตรวจซ้ำ (สถานะ `inbox`)
- DQ check ที่ fail → อัปเดตผลใน `knowledge/dq/` + เปิด task (มี dedupe)
- โน้ต `proven` ที่เลย `review_after` → CI แสดงคำเตือน (ไม่ลดสถานะเอง และไม่ทำให้ PR ตก)

---

## 11. การค้นหาและ context

- โน้ตต้องเป็นหน่วยเล็ก (1 เรื่อง/โน้ต) และควรสั้นพอให้ agent อ่านได้ทั้งโน้ต
- ทุกโฟลเดอร์ความรู้มี `index.md`
- task card ต้องระบุ `context` — executor อ่านเฉพาะที่ระบุ + ตามลิงก์ตามจำเป็น ไม่อ่านทั้ง vault
- ลิงก์: ใช้ **markdown relative link มาตรฐาน** เพื่อให้แสดงผลบน GitHub ได้ (ตั้ง Obsidian ให้สร้างลิงก์แบบนี้); wikilink ใช้ได้ใน instance ถ้ายอมรับว่า GitHub ไม่ render
- ความถูกต้องของระบบห้ามพึ่ง Obsidian plugin — Obsidian เป็น viewer/editor เท่านั้น

---

## 12. CI validators (Brain repo)

CI จัดเป็น **3 required checks** (ชื่อ job ต้องตรงนี้ เพราะใช้ตั้งเป็น required checks ใน branch protection):

| Check (job) | ตรวจอะไร | ทำให้ PR ตกได้ไหม |
|---|---|---|
| `structure` | schema ของ frontmatter ตาม type, `id` ไม่ซ้ำ, ลิงก์ภายในไม่เสีย, การอ้าง id/พาธมีอยู่จริง, status-rules (§5.2), `skills.lock.yml` ผ่าน schema, ชุดทดสอบของ validator เอง | ได้ |
| `guards` | governance-guard (branch `agent/*` แตะ `governance/`), classification-guard (ระดับชั้นต้องอยู่ใน `governance/profile.yml` — ใน master มีได้แค่ `public`), secrets (pattern ของ token ที่พบบ่อยและ private key) | ได้ |
| `freshness` | stale-report: โน้ตที่เลย `review_after` และโน้ตที่ติด `needs-reverify` | ไม่ได้ (เตือนอย่างเดียว) |

ข้อกำหนดของ workflow: trigger เป็น `pull_request` และ push เข้า `main` เท่านั้น, **ห้าม** `pull_request_target`, `permissions: contents: read`, action ของบุคคลอื่นตรึงด้วย commit SHA เต็ม, validator ไม่ใช้เครือข่ายตอนรัน
validator: `scripts/validate.py` · ทดสอบ: `tests/run_tests.py` (โฟลเดอร์ `tests/` ไม่ถูกนับเป็นโน้ตจริง)

---

## 13. Conformance levels

| Level | เงื่อนไข |
|---|---|
| **L1 Structured** | โครงสร้าง §4 + templates + frontmatter; ทำงานด้วยมือ |
| **L2 Gated** | L1 + CI validators §12 + PR-only + CODEOWNERS + branch protection |
| **L3 Orchestrated** | L2 + Conductor §8 + risk tiers §7 + run logs + staleness jobs §10 |

แนะนำให้ instance ใหม่ใช้ L1 → L2 ก่อน และขึ้น L3 เมื่อรูปแบบ task card นิ่งแล้ว

---

## 14. Master repo vs instance

- **Master repo** (public): SPEC, schemas, templates, validators, ตัวอย่างสมมติ — **ห้ามมีข้อมูลขององค์กรจริง**
- **Instance** (private): สร้างจาก master ด้วย "Use this template" แล้วเติมข้อมูลจริง
- การมีส่วนร่วม: PR เข้า master ต้องผ่าน classification-guard

### 14.1 การอัปเกรด instance จากแม่แบบ

- instance ที่สร้างด้วย "Use this template" **ไม่มีประวัติ git ร่วม** กับแม่แบบ จึง merge ตรงๆ ไม่ได้
- ให้เพิ่ม remote ชื่อ `upstream` ชี้ไปที่แม่แบบ แล้วใช้ `scripts/upgrade-core` (ดู [docs/UPGRADING.md](docs/UPGRADING.md))
- `core-paths.txt` แบ่งพาธเป็น
  - **core** — แม่แบบเป็นเจ้าของ อัปเกรดได้ (SPEC, schemas, templates, scripts, workflows, agents, docs, …)
  - **instance** — ของ instance ห้ามอัปเกรดทับ (governance, knowledge, decisions, repos, work, research, README, skills.lock.yml)
- ตัวอัปเกรดนำ "ส่วนต่าง" ระหว่าง tag เดิม (จาก `VERSION`) กับ tag ใหม่ มาใช้เฉพาะพาธ core บน branch ใหม่ `agent/upgrade-core-<tag>`; การเปลี่ยนใน `governance/` ของแม่แบบจะแสดงเป็น "ต้องตรวจเอง" ไม่เขียนทับ
- เวอร์ชันใช้ semver (`spec_version`, `VERSION`, tag `vX.Y.Z`) + `CHANGELOG.md` ที่มีหัวข้อ "Migration notes" ทุกเวอร์ชันที่ต้องแก้ข้อมูลใน instance
- instance เลือกเองว่าจะอัปเกรดเมื่อไร

---

## 15. โปรไฟล์ใช้คนเดียว

สำหรับ instance ที่มีมนุษย์คนเดียว:

- คนเดียวเป็นทั้งเจ้าของ repo และ **Approver**
- เริ่มที่ **L1 → L2** ยังไม่ต้องมี Conductor อัตโนมัติ
- Reviewer แทนได้ด้วย **CI ที่ deterministic + มนุษย์อ่าน PR** (subagent reviewer เป็นตัวช่วยเสริม ไม่ใช่ผู้อนุมัติ)
- **ห้ามผ่อน** แม้ใช้คนเดียว: การป้องกัน `governance/`, การห้าม secret ใน repo, กฎ evidence ของ `proven`, การส่งงานผ่าน PR เท่านั้น
- ข้อสังเกตเรื่องสิทธิ์: GitHub ไม่ให้ผู้เปิด PR อนุมัติ PR ของตัวเอง ถ้า agent ใช้ account เดียวกับเจ้าของ การบังคับ "ต้องมีผู้อนุมัติ" จะทำให้ merge ไม่ได้ — ทางแก้และข้อแลกเปลี่ยนอยู่ใน [docs/SETUP-GITHUB.md](docs/SETUP-GITHUB.md)

---

## 16. Skills และหลักการ

- `skills.lock.yml` — รายการ skill/plugin ที่ instance ต้องใช้ แต่ละรายการมี `name`, `source`, `ref` (commit SHA เต็ม 40 ตัวที่ตรึงไว้), `required`, `verified_at`, `license` หรือ `status: unresolved` พร้อม `reason` เมื่อยังยืนยันที่มาไม่ได้ (schema: `schemas/skills-lock.schema.json`)
- `scripts/install-skills` — อ่าน lock แล้วติดตั้งเฉพาะรายการที่ตรึง commit แล้ว; เจอ `unresolved` ที่ `required: true` → หยุดพร้อมข้อความชัดเจน; **ไม่รันโค้ดจากแหล่งที่ไม่ได้ตรึง ref**; ค่าเริ่มต้นเป็น dry-run
- `PRINCIPLES.md` — หลักการทำงานที่ทุก agent ต้องถือ (อ้างจาก `governance/AGENTS.md`)
- ก่อนเพิ่ม skill ใหม่ใน lock ต้องตรวจ license และเงื่อนไขการใช้งาน (§8)

---

## ภาคผนวก A — Templates

ไฟล์ template จริงอยู่ใน `templates/`:

| ไฟล์ | ใช้กับ |
|---|---|
| `templates/knowledge-note.md` | knowledge note (ตัวอย่างเป็น field) |
| `templates/task-card.md` | task card / prompt card |
| `templates/handoff.md` | handoff |
| `templates/run-log.md` | run log |
| `templates/adr.md` | decision (ADR) |
| `templates/brain.yml` | work repo manifest |

ตัวอย่างที่ผ่าน validator อยู่ใน `examples/`
