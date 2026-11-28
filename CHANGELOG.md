# Changelog

รูปแบบเวอร์ชัน: [semver](https://semver.org/) — tag ของแม่แบบใช้รูป `vX.Y.Z` ตรงกับไฟล์ `VERSION`
ทุกเวอร์ชันที่ instance ต้องแก้ข้อมูลเองจะมีหัวข้อ **Migration notes**

## [Unreleased]

## [0.2.0] — 2026-11-28

### เพิ่ม
- check `guards`: branch `agent/*` ที่แก้ไฟล์ control-plane (`scripts/`, `schemas/`, `tests/`, `.github/`, `.claude/settings.json`, `.claude/agents/`, `core-paths.txt`, `SPEC.md`, `PRINCIPLES.md`) ได้คำเตือน `control-plane-touched` ทีละไฟล์ (เตือนเท่านั้น ไม่ทำให้ PR ตก) — SPEC §9.1
- `.github/CODEOWNERS` ครอบพาธ control-plane ทั้งหมด และ `tests/test_control_plane.py` ตรวจว่ารายการใน CODEOWNERS ตรงกับ `CONTROL_PLANE_PATHS` ใน `scripts/validate.py`
- ชุดทดสอบ: `case.yml` รับ `expect_output` เป็นรายการ และรองรับ `expect_absent`

### ไม่เปลี่ยน
- กฎของ `governance/` (branch `agent/*` แตะ = error, ไม่มี base = ปฏิเสธไว้ก่อน)

### Migration notes
- instance: `.github/CODEOWNERS` ไม่ใช่ core จึง `scripts/upgrade-core` ไม่อัปเดตให้ — ต้องเพิ่มบรรทัด `/scripts/` `/schemas/` `/tests/` `/.claude/agents/` `/core-paths.txt` `/SPEC.md` `/PRINCIPLES.md` (เจ้าของเป็นบัญชีของคุณ) เอง ไม่งั้น `tests/test_control_plane.py` ใน check `structure` จะล้ม
- PR ที่ upgrade-core สร้าง (branch `agent/upgrade-core-*`) จะมีคำเตือน `control-plane-touched` เป็นปกติ เพราะอัปเกรดไฟล์ core

## [0.1.0] — 2026-11-27

เวอร์ชันแรก

### เพิ่ม
- `SPEC.md` v0.1.0: roles (รวม Sentinel และ Channel แบบอ่านอย่างเดียว), prompt card, Conductor ที่ไม่ผูก vendor, การบังคับ governance ในทางปฏิบัติ, CI 3 checks, โปรไฟล์ใช้คนเดียว, การอัปเกรด instance, skills
- `PRINCIPLES.md`, `governance/` ตั้งต้น (AGENTS, routing, commands, classification, profile)
- JSON Schema ของทุก note type, `skills.lock.yml`, `brain.yml`, `commands.yml`, `profile.yml`
- templates, ตัวอย่างสมมติ (`examples/`), validator (`scripts/validate.py`) และชุดทดสอบ (`tests/`)
- `scripts/upgrade-core`, `scripts/install-skills`
- CI `.github/workflows/validate.yml` (checks: `structure`, `guards`, `freshness`)
- คู่มือใน `docs/`

### Migration notes
- ไม่มี (เวอร์ชันแรก)
