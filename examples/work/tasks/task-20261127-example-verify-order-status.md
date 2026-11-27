---
id: task-20261127-example-verify-order-status
type: task
title: พิสูจน์ชุดค่าของ order_status ใน ExampleMarket
classification: public
spec_version: 0.1.0
status: inbox
repo: example-owner/example-market-analytics
executor: Executor
risk: R0
context:
  - examples/knowledge/fields/example-market-order-status.md
  - examples/knowledge/systems/example-market.md
acceptance:
  - มี query หรือ check ที่ดึงชุดค่าทั้งหมดของ order_status จากข้อมูลต้นทาง
  - โน้ต field อัปเดต evidence และยังเป็น unverified จนกว่า Approver จะยกสถานะ
budget: {max_attempts: 2, max_minutes: 60}
claimed_by:
claim_expires:
created_by: channel
created: 2026-11-27
updated: 2026-11-27
---
## เป้าหมาย
ยืนยันว่าค่าของ `order_status` มีอะไรบ้างจากข้อมูลจริงของระบบ (prompt card ที่ส่งมาจากห้องแชท)

## ขอบเขต (ทำ / ไม่ทำ)
- ทำ: อ่านข้อมูล เขียน check เสนอ evidence
- ไม่ทำ: เปลี่ยนสถานะเป็น `proven`, แก้ `governance/`

## เกณฑ์เสร็จ
ตาม `acceptance` ด้านบน
