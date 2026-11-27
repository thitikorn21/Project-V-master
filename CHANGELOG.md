# Changelog

รูปแบบเวอร์ชัน: [semver](https://semver.org/) — tag ของแม่แบบใช้รูป `vX.Y.Z` ตรงกับไฟล์ `VERSION`
ทุกเวอร์ชันที่ instance ต้องแก้ข้อมูลเองจะมีหัวข้อ **Migration notes**

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
