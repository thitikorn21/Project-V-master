"""Re-runnable check for examples/knowledge/fields/example-market-order-total.md.

Asserts that for every row of examples/data/orders.csv:
    order_total == item_total + shipping_fee - discount
Exit code 0 = pass, 1 = fail. Uses only the standard library and no network.
"""
import csv
import sys
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "orders.csv"


def main() -> int:
    failures = []
    rows = 0
    with DATA.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows += 1
            expected = Decimal(row["item_total"]) + Decimal(row["shipping_fee"]) - Decimal(row["discount"])
            actual = Decimal(row["order_total"])
            if expected != actual:
                failures.append(f"{row['order_id']}: expected {expected}, got {actual}")
    if rows == 0:
        print("check-order-total: FAIL (no rows)")
        return 1
    if failures:
        print("check-order-total: FAIL")
        for line in failures:
            print("  " + line)
        return 1
    print(f"check-order-total: PASS ({rows} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
