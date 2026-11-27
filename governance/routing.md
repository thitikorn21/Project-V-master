# Routing (ตารางเริ่มต้น — ตัวอย่างสมมติ)

ตารางนี้ตายตัว: Conductor เลือกแถวที่ตรงกับ `ประเภทงาน` ของ task card เท่านั้น
ถ้าไม่ตรงแถวไหน → ส่ง task กลับสถานะ `inbox` พร้อมเหตุผล **ห้ามตัดสินเอง** (SPEC §7)

| ประเภทงาน | Executor | Reviewer | Tier | ต้องอนุมัติจากมนุษย์ | คำสั่งที่ใช้ (`commands.yml`) |
|---|---|---|---|---|---|
| เขียน/แก้เอกสาร, โน้ต `proposed` | Executor | CI | R0 | ไม่ (ถ้า instance อนุญาต auto-merge) | `validate-brain` |
| เสนอความรู้ใหม่ (`unverified`) | Executor | Reviewer + CI | R0 | ไม่ | `validate-brain` |
| ยกสถานะเป็น `proven` | — (Approver เท่านั้น) | Approver | R2 | **ใช่** | — |
| แก้โค้ดใน work repo ที่ไม่แตะ prod | Executor | Reviewer + CI | R1 | ไม่ (ตามนโยบาย repo) | `run-executor` |
| ตรวจตามรอบ (pipeline, DQ, ความสด) | Sentinel | — | R0 | ไม่ | `stale-report` |
| แตะ prod data/schema, deploy, credential | Executor (เตรียม) | Reviewer + Approver | R2 | **ใช่** | `run-executor` |
| ทำลาย/ย้อนไม่ได้ (drop, delete, backfill ใหญ่, rotate secret) | Executor (เตรียมแผนเท่านั้น) | Approver | R3 | **ใช่ — มนุษย์เป็นคนรัน** | — |
| แก้ `governance/` | มนุษย์เท่านั้น | Approver | R2 | **ใช่** | — |

Role ทั้งหมดเป็นชื่อทั่วไป (Conductor, Executor, Reviewer, Sentinel, Approver) — instance ผูกกับเครื่องมือจริงใน `governance/local/`
