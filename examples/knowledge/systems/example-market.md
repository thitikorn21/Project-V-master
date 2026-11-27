---
id: sys-example-market
type: system
title: ExampleMarket (ระบบสมมติ)
classification: public
spec_version: 0.1.0
status: unverified
system_kind: marketplace
owner: ทีมตัวอย่าง
source_system: example-market
evidence: []
review_after: 2027-05-27
written_by: {role: human, tool: editor, run_id: null}
created: 2026-11-27
updated: 2026-11-27
---
## คืออะไร
ร้านค้าออนไลน์สมมติ ใช้เป็นตัวอย่างในแม่แบบเท่านั้น ส่งออกข้อมูลคำสั่งซื้อเป็นไฟล์ CSV วันละครั้ง

## ข้อมูลที่ Brain ใช้
- คำสั่งซื้อ: [../../data/orders.csv](../../data/orders.csv)
- field ที่บันทึกแล้ว: [order_status](../fields/example-market-order-status.md), [order_total](../fields/example-market-order-total.md)

## ข้อควรระวัง
ชื่อ field ของระบบนี้อาจตรงกับระบบอื่น แต่ความหมายไม่จำเป็นต้องเหมือนกัน (PRINCIPLES B.6)
