#!/usr/bin/env python3
"""Tests for scripts/install-skills (no network).

* required + unresolved  -> exit 3, nothing fetched
* ref that is not a 40-char commit -> exit 2 (schema)
* the real skills.lock.yml passes in dry-run
* --apply with a local throwaway source: installs the pinned commit, not the newer branch tip
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "install-skills"
GIT_ID = ["-c", "user.name=test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
          "-c", "init.defaultBranch=main"]


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8")


def git(cwd: Path, *args) -> str:
    res = subprocess.run(["git", *GIT_ID, *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    assert res.returncode == 0, res.stderr
    return res.stdout


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        lock = t / "unresolved.yml"
        lock.write_text("lock_version: 1\nskills:\n  - name: needed\n    status: unresolved\n"
                        "    required: true\n    reason: ยังหาแหล่งทางการไม่เจอ\n", encoding="utf-8")
        res = run("--lock", str(lock), "--cache", str(t / "cache"))
        assert res.returncode == 3, res.stdout + res.stderr
        assert "needed" in res.stdout and "unresolved" in res.stdout
        assert not (t / "cache").exists()

        bad = t / "bad.yml"
        bad.write_text("lock_version: 1\nskills:\n  - name: x\n    status: resolved\n    kind: skill-folder\n"
                       "    source: https://github.com/example/x\n    ref: main\n    path: skills\n"
                       "    required: true\n    verified_at: 2026-11-27\n    license: MIT\n", encoding="utf-8")
        res = run("--lock", str(bad))
        assert res.returncode == 2, res.stdout + res.stderr

        res = run()
        assert res.returncode == 0, res.stdout + res.stderr
        assert "(dry-run)" in res.stdout

        src = t / "src"
        git(t, "init", str(src))
        (src / "skills").mkdir()
        (src / "skills" / "SKILL.md").write_text("pinned version\n", encoding="utf-8")
        git(src, "add", "-A")
        git(src, "commit", "-m", "pinned")
        pinned = git(src, "rev-parse", "HEAD").strip()
        (src / "skills" / "SKILL.md").write_text("newer unpinned version\n", encoding="utf-8")
        git(src, "commit", "-am", "newer")
        git(src, "config", "uploadpack.allowAnySHA1InWant", "true")
        good = t / "good.yml"
        good.write_text(f"lock_version: 1\nskills:\n  - name: demo\n    status: resolved\n    kind: skill-folder\n"
                        f"    source: {src.as_posix()}\n    ref: {pinned}\n    path: skills\n    required: true\n"
                        f"    verified_at: 2026-11-27\n    license: MIT\n", encoding="utf-8")
        res = run("--lock", str(good), "--apply", "--allow-local-source", "--cache", str(t / "cache"),
                  "--target", str(t / "target"))
        assert res.returncode == 0, res.stdout + res.stderr
        installed = (t / "target" / "demo" / "SKILL.md").read_text(encoding="utf-8")
        assert installed == "pinned version\n", installed
    print("test_install_skills: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
