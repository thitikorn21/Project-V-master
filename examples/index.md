# examples — ตัวอย่างสมมติ

ทุกไฟล์ในนี้เป็น **ข้อมูลสมมติ** (`classification: public`) ของระบบร้านค้าออนไลน์ชื่อ `ExampleMarket` ที่ไม่มีอยู่จริง ใช้ดูรูปแบบและต้องผ่าน validator

| ไฟล์ | แสดงอะไร |
|---|---|
| [knowledge/systems/example-market.md](knowledge/systems/example-market.md) | โน้ตระบบ (system) |
| [knowledge/fields/example-market-order-status.md](knowledge/fields/example-market-order-status.md) | field ที่ยังไม่พิสูจน์ (`unverified`) |
| [knowledge/fields/example-market-order-total.md](knowledge/fields/example-market-order-total.md) | field ที่ `proven` พร้อม evidence ที่ CI รันซ้ำได้ |
| [work/tasks/task-20261127-example-verify-order-status.md](work/tasks/task-20261127-example-verify-order-status.md) | prompt card (task card สถานะ `inbox` จากห้องแชท) |
| [work/handoffs/ho-task-20261127-example-verify-order-status-run-0001.md](work/handoffs/ho-task-20261127-example-verify-order-status-run-0001.md) | handoff ที่แยก ผ่าน / ไม่ผ่าน / ไม่ได้รัน |
| [checks/check_order_total.py](checks/check_order_total.py) + [data/orders.csv](data/orders.csv) | check ที่ใช้เป็น evidence (รันซ้ำได้: `python examples/checks/check_order_total.py`) |

ใน instance จะลบโฟลเดอร์นี้ทิ้งก็ได้
