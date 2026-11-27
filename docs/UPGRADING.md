# อัปเกรด instance จากแม่แบบ

instance ที่สร้างด้วยปุ่ม **Use this template** ได้ไฟล์ชุดเดียวกับแม่แบบ แต่ **ไม่มีประวัติ git ร่วมกัน** จึงใช้ `git merge` ตรงๆ ไม่ได้
ใช้ `scripts/upgrade-core` แทน (SPEC §14.1) — มันนำ "ส่วนต่างระหว่างสองเวอร์ชันของแม่แบบ" มาใช้เฉพาะพาธ **core** ใน [`core-paths.txt`](../core-paths.txt)

| ชนิดพาธ | ตัวอย่าง | ตอนอัปเกรด |
|---|---|---|
| core (แม่แบบเป็นเจ้าของ) | `SPEC.md`, `schemas/`, `templates/`, `scripts/`, `.github/workflows/`, `.claude/agents/`, `docs/`, `VERSION`, `CHANGELOG.md`, `tests/` | อัปเกรดให้ (ถ้าคุณแก้ไฟล์ core เอง จะพยายามรวมให้ ถ้าชนกันจะแจ้ง) |
| instance (ของคุณ) | `governance/`, `knowledge/`, `decisions/`, `repos/`, `work/`, `research/`, `README.md`, `skills.lock.yml` | **ไม่แตะ** ถ้าแม่แบบเปลี่ยนตรงนี้ จะแสดงเป็น "ต้องตรวจเอง" |
| อื่นๆ | `examples/`, `.gitignore`, `AGENTS.md`, … | ไม่แตะ และแสดงรายการให้ดู |

## ครั้งแรก: เพิ่ม remote ชื่อ `upstream`

ในโฟลเดอร์ของ instance (แทน `<URL ของแม่แบบ>` ด้วยที่อยู่ของแม่แบบ):

```
git remote add upstream <URL ของแม่แบบ>
```

## ทุกครั้งที่จะอัปเกรด

1. อ่าน `CHANGELOG.md` ของเวอร์ชันใหม่ในแม่แบบ โดยเฉพาะหัวข้อ **Migration notes**
2. ให้แน่ใจว่าไม่มีงานค้างที่ยังไม่ commit (`git status` ต้องว่าง) และอยู่บน `main` ล่าสุด
3. ดูแผนก่อน (ไม่เปลี่ยนอะไร):
   ```
   python scripts/upgrade-core --to v0.2.0
   ```
   ผลแบ่งเป็น 3 กลุ่ม: **จะอัปเกรด** / **ต้องตรวจเอง** / **ไม่แตะ**
4. ลงมือ:
   ```
   python scripts/upgrade-core --to v0.2.0 --apply
   ```
   จะได้ branch ใหม่ `agent/upgrade-core-v0.2.0` ที่มี commit เดียว (ยังไม่ push) — `main` ไม่ถูกแตะ
5. ตรวจ:
   ```
   python scripts/validate.py all
   python tests/run_tests.py
   ```
6. push branch แล้วเปิด PR ตามปกติ ([SETUP-GITHUB.md](SETUP-GITHUB.md) ขั้น 4)
7. รายการ "ต้องตรวจเอง" ที่อยู่ใน `governance/` — มนุษย์อ่านแล้วแก้เองใน PR แยก (agent แตะ `governance/` ไม่ได้)

## ถ้าชนกัน (conflict)

ตัวอัปเกรดจะหยุดบน branch `agent/upgrade-core-<tag>` และบอกไฟล์ที่ชน
- แก้ไฟล์ที่มีเครื่องหมาย `<<<<<<<` / `>>>>>>>` ให้เหลือแบบที่ต้องการ แล้ว `git add` + `git commit`
- หรือยกเลิกทั้งหมด: `git switch main` แล้ว `git branch -D agent/upgrade-core-<tag>`

## หมายเหตุ

- เวอร์ชันเดิมอ่านจากไฟล์ `VERSION` (เช่น `0.1.0` → tag `v0.1.0`) หรือระบุเองด้วย `--from v0.1.0`
- ตัวอัปเกรด fetch เฉพาะ tag สองตัวที่ใช้ ไปเก็บที่ `refs/upstream/tags/…` ไม่สร้าง tag ใน instance และไม่ push อะไร
- ทดสอบอยู่ใน `tests/test_upgrade_core.py` (สร้าง repo ชั่วคราวจำลองแม่แบบ + instance แล้วอัปเกรดจริง)
