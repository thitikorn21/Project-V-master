# ตั้งค่า GitHub ทีละขั้น (สำหรับคนที่ไม่ใช่ dev)

คู่มือนี้ทำให้ branch `main` รับงานได้ทาง Pull Request (PR) เท่านั้น และต้องผ่านการตรวจอัตโนมัติ 3 ตัวก่อน merge
ใช้ได้ทั้งกับแม่แบบนี้และกับ instance (private) ที่สร้างจากแม่แบบ
ชื่อเมนูในคู่มือตรวจจากเอกสาร GitHub เมื่อ 2026-11-27 (ลิงก์อยู่ท้ายไฟล์) — ถ้าหน้าจอเปลี่ยน ให้ยึดตามความหมาย

คำศัพท์:
- **PR (Pull Request)** = คำขอให้รวมงานจาก branch หนึ่งเข้า `main` ให้คนตรวจก่อน
- **check** = การตรวจอัตโนมัติที่ GitHub รันให้ทุก PR (ของ repo นี้มี `structure`, `guards`, `freshness`)
- **Code Owner** = เจ้าของพาธที่กำหนดในไฟล์ `.github/CODEOWNERS` (ของ repo นี้คือ `@thitikorn21` สำหรับ `governance/`, `.github/`, `.claude/settings.json`, `.claude/agents/`, `scripts/`, `schemas/`, `tests/`, `core-paths.txt`, `SPEC.md` และ `PRINCIPLES.md`)

---

## ขั้น 0 — เรื่องที่ต้องตัดสินใจก่อน: agent ใช้บัญชี GitHub ของใคร

GitHub **ไม่ให้คนเปิด PR อนุมัติ PR ของตัวเอง** ถ้า agent ส่งงานด้วยบัญชีของคุณเอง PR นั้นนับว่า "คุณเป็นคนเปิด" คุณจึงอนุมัติไม่ได้

| ทางเลือก | ทำอย่างไร | ข้อดี | ข้อเสีย |
|---|---|---|---|
| **A (แนะนำ)** | ให้ agent ใช้บัญชี GitHub แยกอีกบัญชี เชิญเป็น collaborator ของ repo (ได้สิทธิ์ write ไม่ใช่ admin) | คุณอนุมัติ PR ของ agent ได้จริง; เปิด "ห้ามข้ามเงื่อนไข" ได้; agent ไม่มีสิทธิ์ข้ามกฎ | ต้องสร้างบัญชีเพิ่มและตั้งการล็อกอินให้ agent |
| **B (ชั่วคราว)** | agent ใช้บัญชีของคุณ (แบบที่ใช้อยู่ตอนนี้) | ไม่ต้องตั้งอะไรเพิ่ม | ตั้ง "ต้องมีผู้อนุมัติ" ไม่ได้ (ไม่งั้นไม่มีใคร merge ได้) จึงเหลือแค่ "ต้องผ่าน check" — **agent ที่ถือบัญชีคุณ merge งานตัวเองหรือแก้การตั้งค่านี้ได้** การรีวิวของคุณจึงเป็นวินัย ไม่ใช่สิ่งที่ระบบบังคับ (SPEC §9.1) |

**ภายใต้ทางเลือก B ไฟล์ CODEOWNERS ไม่ถูกบังคับ** (ไม่ได้ติ๊ก "Require review from Code Owners") — branch ของ agent แก้ตัวตรวจ (`scripts/`, `tests/`, `.github/` ฯลฯ) แล้ว check ยังเขียวได้
check `guards` จะขึ้นคำเตือน `control-plane-touched` ทีละไฟล์ที่ถูกแก้ ให้เปิดดูไฟล์เหล่านั้นใน Files changed ก่อน merge ทุกครั้ง — แต่เป็น **คำเตือนเท่านั้น ไม่กั้นการ merge** การกั้นจริงต้องใช้ทางเลือก A

ด้านล่างระบุว่าช่องไหนต่างกันระหว่าง A กับ B

---

## ขั้น 1 — ให้ check รันอย่างน้อยหนึ่งครั้งก่อน

ช่องเลือก check ในขั้น 2 จะค้นเจอเฉพาะ check ที่เคยรันสำเร็จใน repo นี้ภายใน 7 วันที่ผ่านมา

1. เปิด PR ใดก็ได้เข้า `main` (เช่น PR แรกของ agent)
2. ในหน้า PR เลื่อนลงดูกล่อง checks รอจนเห็น `structure`, `guards`, `freshness` ขึ้นเครื่องหมายถูก

## ขั้น 2 — ตั้ง branch protection ของ `main`

1. เปิดหน้า repo บน GitHub → แท็บ **Settings** (ถ้าไม่เห็น กดเมนู **…** แล้วเลือก Settings)
2. แถบซ้าย หมวด "Code, planning, and automation" → **Branches**
3. ใต้หัวข้อ "Branch protection rules" กด **Add classic branch protection rule**
4. ช่อง **Branch name pattern** พิมพ์ `main`
5. ติ๊กตามนี้:
   - ☑ **Require a pull request before merging**
     - ☑ **Require approvals** (จำนวน 1) — *ทางเลือก A เท่านั้น* (ทางเลือก B ไม่ติ๊ก ไม่งั้นไม่มีใคร merge ได้)
     - ☑ **Require review from Code Owners** — *ทางเลือก A เท่านั้น* ด้วยเหตุผลเดียวกัน
   - ☑ **Require status checks to pass before merging**
     - ☑ **Require branches to be up to date before merging**
     - ในช่องค้นหา check พิมพ์แล้วเลือกทีละตัว: `structure`, `guards`, `freshness`
   - ☑ **Do not allow bypassing the above settings** — ติ๊กทั้ง A และ B (ให้กฎใช้กับ admin ด้วย)
   - ☐ **Allow force pushes** — ปล่อยว่าง (ห้าม force-push)
   - ☐ **Allow deletions** — ปล่อยว่าง
6. กด **Create** (หรือ **Save changes**)

> อีกแบบหนึ่งคือ **Rulesets** (Settings → Rules → Rulesets → New ruleset → New branch ruleset) ใช้ได้เหมือนกัน
> แต่คู่มือนี้ใช้แบบ classic เพราะชื่อช่องตรวจยืนยันได้ครบกว่า

### ตรวจว่าตั้งสำเร็จจริง

1. กลับไป Settings → Branches ต้องเห็นกฎของ `main` ในรายการ
2. เปิด PR ใหม่ที่ check ยังไม่เสร็จ → ปุ่ม merge ต้องกดไม่ได้ และมีข้อความว่า required checks ยังไม่ผ่าน
3. (ทางเลือก A) PR ที่แตะ `governance/` ต้องขึ้นว่ารอรีวิวจาก Code Owner

---

## ขั้น 3 — Secret scanning และ push protection

repo สาธารณะ: **secret scanning** รันให้อัตโนมัติฟรี ส่วน **push protection** (กันไม่ให้ push ความลับขึ้นไปเลย) ระดับ repo ต้องเปิดเอง

1. Settings → แถบซ้าย หมวด "Security and quality" → **Advanced Security**
2. หา **Secret Protection** กด **Enable**
3. ใต้นั้นหา **Push protection** กด **Enable**
4. (แนะนำ) ที่บัญชีของคุณ: รูปโปรไฟล์ → **Settings** → **Code security** → ตรวจว่า "Push protection for yourself" เปิดอยู่

ตรวจว่าเปิดแล้ว: กลับมาหน้าเดิม ต้องเห็นสถานะเป็นเปิด (ปุ่มเปลี่ยนเป็น Disable)
ดูการแจ้งเตือน: แท็บ **Security and quality** ของ repo (เดิมชื่อ Security) → **Secret scanning**

> repo นี้มี check `guards` ที่ตรวจรูปแบบความลับที่พบบ่อยอีกชั้น แต่ไม่แทน secret scanning ของ GitHub

---

## ขั้น 4 — รีวิวและ merge PR ของ agent

1. แท็บ **Pull requests** → เปิด PR
2. อ่านคำอธิบาย PR และ handoff ที่ agent เขียน — ดูว่ามีส่วน "ไม่ได้รัน" อะไรบ้าง
3. แท็บ **Files changed** ดูไฟล์ที่เปลี่ยน ถ้ามีไฟล์ใน `governance/` ที่คุณไม่ได้ขอ = อย่า merge
4. (ทางเลือก A) กด **Review changes** → เลือก **Approve** → **Submit review**
5. กลับแท็บ **Conversation** เลื่อนลงล่าง ตรวจว่า check ทั้ง 3 ตัวเป็นเครื่องหมายถูก
6. กดลูกศรข้างปุ่ม merge เลือกวิธี (แนะนำ **Squash and merge** = รวมเป็น commit เดียว) → กด **Confirm**
   - ทางเลือก B: ไม่มีขั้นอนุมัติ ให้คุณอ่านข้อ 2–3 ให้ครบก่อนกด merge เพราะระบบไม่บังคับให้มีคนตรวจ
7. กด **Delete branch** ได้หลัง merge (ลบเฉพาะ branch ของ PR นั้น)

ถ้า check ไม่ผ่าน: กดที่ชื่อ check ที่มีกากบาทเพื่อดูข้อความ แล้วส่งข้อความนั้นให้ agent แก้ ไม่ต้อง merge

---

## แหล่งอ้างอิง (เอกสาร GitHub)

- Branch protection: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule
- Check ต้องเคยรันภายใน 7 วัน: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks
- Rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository
- ผู้เปิด PR อนุมัติเองไม่ได้: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews
- CODEOWNERS: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- Secret scanning: https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning
- เปิดฟีเจอร์ความปลอดภัยของ repo: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-security-and-analysis-settings-for-your-repository
- Merge PR: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request
