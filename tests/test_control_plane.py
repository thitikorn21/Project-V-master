#!/usr/bin/env python3
"""CODEOWNERS must cover exactly the paths the validator protects (SPEC §9.1).

The list lives once, in scripts/validate.py (CONTROL_PLANE_PATHS plus PROTECTED_PREFIX). This test
reads the real .github/CODEOWNERS: every protected path must have an anchored entry ("/" + path)
with at least one owner, and every CODEOWNERS entry must be a protected path. Adding a path in
one place and forgetting the other fails here.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


def codeowners_entries(text: str) -> dict[str, list[str]]:
    entries = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            pattern, *owners = line.split()
            entries[pattern] = owners
    return entries


def sync_problems(protected: list[str], text: str) -> list[str]:
    entries = codeowners_entries(text)
    expected = {"/" + p for p in protected}
    problems = [f"CODEOWNERS ไม่มี {e}" for e in sorted(expected - entries.keys())]
    problems += [f"CODEOWNERS มี {e} แต่ validate.py ไม่ได้ป้องกัน" for e in sorted(entries.keys() - expected)]
    problems += [f"{e} ไม่มีเจ้าของ" for e in sorted(expected & entries.keys()) if not entries[e]]
    return problems


def main() -> int:
    protected = [validate.PROTECTED_PREFIX, *validate.CONTROL_PLANE_PATHS]
    assert len(set(protected)) == len(protected), f"พาธซ้ำ: {protected}"

    sample = "/governance/ @owner\n/scripts/ @owner\n/extra/ @owner\n/schemas/\n"
    assert sync_problems(["governance/", "scripts/", "tests/", "schemas/"], sample) == [
        "CODEOWNERS ไม่มี /tests/",
        "CODEOWNERS มี /extra/ แต่ validate.py ไม่ได้ป้องกัน",
        "/schemas/ ไม่มีเจ้าของ",
    ], "sync check must catch missing, extra and ownerless entries"

    text = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    problems = sync_problems(protected, text)
    assert not problems, "CODEOWNERS ไม่ตรงกับ validate.py:\n" + "\n".join(problems)
    print(f"test_control_plane: PASS ({len(protected)} พาธ)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
