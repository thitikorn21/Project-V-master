#!/usr/bin/env python3
"""Self-tests for the Brain Hub tooling. Run: python tests/run_tests.py

1. tests/fixtures/valid/<case>   every run in case.yml must exit 0, print every expect_output and
                                 none of expect_absent (each: one string or a list)
2. tests/fixtures/invalid/<case> the validator must exit 1 and report expect_code
3. tests/test_upgrade_core.py, tests/test_install_skills.py, tests/test_hermetic.py and
   tests/test_control_plane.py

Every subprocess runs with tests/hermetic.py: CI variables (GITHUB_*, CI, ...) and GIT_* are
removed, and a case adds variables only through an `env:` mapping in its case.yml.
--fixtures-only runs steps 1 and 2.

Each fixture is copied to a temp folder first. Placeholders such as @@FAKE_GITHUB_TOKEN@@ are
replaced there with values built at run time, so no secret-shaped text is ever stored in the repo.
No network is used.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from hermetic import hermetic_env

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VALIDATE = ROOT / "scripts" / "validate.py"
PLACEHOLDERS = {
    "@@FAKE_GITHUB_TOKEN@@": "gh" + "p_" + "A1b2C3d4" * 5,
    "@@FAKE_PRIVATE_KEY_HEADER@@": "-----" + "BEGIN " + "RSA PRIVATE" + " KEY-----",
}


def materialize(case_dir: Path, tmp: Path) -> Path:
    dest = tmp / case_dir.name
    shutil.copytree(case_dir, dest)
    for p in dest.rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            new = text
            for k, v in PLACEHOLDERS.items():
                new = new.replace(k, v)
            if new != text:
                p.write_text(new, encoding="utf-8")
    return dest


def as_list(value) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def run_validator(case: Path, args: list[str], env: dict | None) -> subprocess.CompletedProcess:
    args = [str(a).replace("{case}", str(case)) for a in args]
    return subprocess.run([sys.executable, str(VALIDATE), *args, "--root", str(case / "root")],
                          capture_output=True, text=True, encoding="utf-8", env=hermetic_env(env))


def main() -> int:
    fixtures_only = "--fixtures-only" in sys.argv[1:]
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    failures = []
    count = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for case_dir in sorted((HERE / "fixtures" / "valid").iterdir()):
            spec = yaml.safe_load((case_dir / "case.yml").read_text(encoding="utf-8"))
            case = materialize(case_dir, tmp)
            for r in spec["runs"]:
                count += 1
                res = run_validator(case, r["args"], r.get("env"))
                out = res.stdout + res.stderr
                name = f"valid/{case_dir.name} {' '.join(map(str, r['args']))}"
                missing = [s for s in as_list(r.get("expect_output")) if s not in out]
                present = [s for s in as_list(r.get("expect_absent")) if s in out]
                if res.returncode != 0:
                    failures.append(f"{name}: exit {res.returncode}\n{out}")
                elif missing:
                    failures.append(f"{name}: ไม่พบข้อความ {missing!r}\n{out}")
                elif present:
                    failures.append(f"{name}: พบข้อความที่ไม่ควรมี {present!r}\n{out}")
                else:
                    print(f"PASS {name}")
        for case_dir in sorted((HERE / "fixtures" / "invalid").iterdir()):
            spec = yaml.safe_load((case_dir / "case.yml").read_text(encoding="utf-8"))
            case = materialize(case_dir, tmp)
            count += 1
            res = run_validator(case, spec["args"], spec.get("env"))
            out = res.stdout + res.stderr
            name = f"invalid/{case_dir.name}"
            if res.returncode != 1:
                failures.append(f"{name}: ควร exit 1 แต่ได้ {res.returncode}\n{out}")
            elif f"ERROR {spec['expect_code']} " not in out:
                failures.append(f"{name}: ไม่พบ error {spec['expect_code']!r}\n{out}")
            else:
                print(f"PASS {name} (จับได้: {spec['expect_code']})")
    modules = () if fixtures_only else ("test_upgrade_core.py", "test_install_skills.py", "test_hermetic.py",
                                        "test_control_plane.py")
    for test in modules:
        count += 1
        res = subprocess.run([sys.executable, str(HERE / test)], capture_output=True, text=True, encoding="utf-8",
                             env=hermetic_env())
        if res.returncode != 0:
            failures.append(f"{test}: exit {res.returncode}\n{res.stdout}{res.stderr}")
        else:
            print(f"PASS {test}")
    print(f"\nรวม {count} ชุด, ไม่ผ่าน {len(failures)}")
    for f in failures:
        print("\nFAIL " + f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
