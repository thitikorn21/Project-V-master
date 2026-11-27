---
id: fld-example-market-order-total
type: field
title: example-market.order_total
classification: public
spec_version: 0.1.0
status: proven
source_system: example-market
data_type: decimal
effective_from: 2026-01-01
effective_to:
evidence:
  - kind: test
    ref: examples/checks/check_order_total.py
    result: pass
    run_id: run-0001
verified_at: 2026-11-27
verified_commit: "481522143b75"
verified_by: check:check-order-total
review_after: 2027-05-27
written_by: {role: human, tool: editor, run_id: null}
created: 2026-11-27
updated: 2026-11-27
---
## นิยาม
ยอดรวมของคำสั่งซื้อในระบบ [ExampleMarket](../systems/example-market.md):
`order_total = item_total + shipping_fee - discount`

## เงื่อนไขการใช้
ใช้เป็นยอดขายต่อคำสั่งซื้อได้ ยังไม่รวมการคืนเงิน

## ข้อควรระวัง / กรณีพิเศษ
`discount` เป็นยอดส่วนลดรวมของทั้งคำสั่งซื้อ ไม่ใช่ต่อรายการ

## หลักฐาน (สรุปของ evidence)
check [check_order_total.py](../../checks/check_order_total.py) ตรวจทุกแถวของ [orders.csv](../../data/orders.csv) ว่าสูตรตรงกับค่าที่บันทึก — CI รันซ้ำทุก PR ใน job `structure`
