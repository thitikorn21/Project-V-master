---
id: fld-example-market-order-status
type: field
title: example-market.order_status
classification: public
spec_version: 0.1.0
status: unverified
source_system: example-market
data_type: string
effective_from: 2026-01-01
effective_to:
evidence: []
verified_at:
verified_commit:
verified_by:
review_after: 2027-02-27
written_by: {role: executor, tool: example-agent, run_id: run-0001}
created: 2026-11-27
updated: 2026-11-27
tags: [needs-source-check]
---
## นิยาม
สถานะของคำสั่งซื้อในระบบ [ExampleMarket](../systems/example-market.md) — **ยังไม่พิสูจน์**: ได้มาจากการอ่านหน้าจอระบบเท่านั้น ยังไม่ได้เทียบกับเอกสารหรือข้อมูลต้นทาง

## เงื่อนไขการใช้
ห้ามใช้เป็นเงื่อนไขในการนับยอดจนกว่าจะพิสูจน์ (ดู task [task-20261127-example-verify-order-status](../../work/tasks/task-20261127-example-verify-order-status.md))

## ข้อควรระวัง / กรณีพิเศษ
ค่าที่เห็นบนหน้าจอ (`paid`, `shipped`, `cancelled`) อาจไม่ใช่ชุดค่าทั้งหมดในข้อมูลจริง

## หลักฐาน (สรุปของ evidence)
ยังไม่มี
