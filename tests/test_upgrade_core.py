#!/usr/bin/env python3
"""End-to-end test of scripts/upgrade-core in throwaway repos (no network).

Builds: a bare "template" repo with tags v0.1.0 and v0.2.0, and an "instance" created the way
"Use this template" does it (same files, no shared history) with its own edits. Then checks that
the dry-run changes nothing, and --apply upgrades core paths only, on branch agent/upgrade-core-v0.2.0.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "upgrade-core"
GIT_ID = ["-c", "user.name=test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
          "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def git(cwd: Path, *args) -> str:
    res = subprocess.run(["git", *GIT_ID, *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise AssertionError(f"git {args}: {res.stderr}")
    return res.stdout


def write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


CORE_PATHS = "[core]\nSPEC.md\nschemas/\ntemplates/\nVERSION\ncore-paths.txt\n\n[instance]\ngovernance/\nknowledge/\nREADME.md\n"
V1 = {
    ".gitattributes": "* text=auto eol=lf\n",
    "SPEC.md": "# SPEC\nline one\nline two\nline three\n",
    "schemas/a.schema.json": "{}\n",
    "templates/old.md": "old template\n",
    "governance/AGENTS.md": "rules v1\n",
    "README.md": "template readme\n",
    "VERSION": "0.1.0\n",
    "core-paths.txt": CORE_PATHS,
    "misc.txt": "not listed\n",
}


def run_upgrade(cwd: Path, *args) -> subprocess.CompletedProcess:
    env_git = subprocess.run(["git", "config", "user.name"], cwd=cwd, capture_output=True, text=True)
    assert env_git.stdout.strip() == "test", "instance repo must have a local identity"
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        bare, tpl, inst = t / "template.git", t / "template-work", t / "instance"
        git(t, "init", "--bare", str(bare))
        git(t, "init", str(tpl))
        for k, v in V1.items():
            write(tpl, k, v)
        git(tpl, "add", "-A")
        git(tpl, "commit", "-m", "v0.1.0")
        git(tpl, "tag", "v0.1.0")
        write(tpl, "SPEC.md", "# SPEC\nline one\nline two CHANGED\nline three\n")
        write(tpl, "schemas/b.schema.json", "{\"new\": true}\n")
        (tpl / "templates/old.md").unlink()
        write(tpl, "governance/AGENTS.md", "rules v2 from template\n")
        write(tpl, "README.md", "template readme v2\n")
        write(tpl, "misc.txt", "changed but not listed\n")
        write(tpl, "VERSION", "0.2.0\n")
        git(tpl, "add", "-A")
        git(tpl, "commit", "-m", "v0.2.0")
        git(tpl, "tag", "v0.2.0")
        git(tpl, "remote", "add", "origin", str(bare))
        git(tpl, "push", "-q", "origin", "main", "--tags")

        git(t, "init", str(inst))
        git(inst, "config", "user.name", "test")
        git(inst, "config", "user.email", "test@example.invalid")
        for k, v in V1.items():
            write(inst, k, v)
        write(inst, "SPEC.md", "# SPEC\nline one\nline two\nline three\nlocal note added by instance\n")
        write(inst, "governance/AGENTS.md", "rules customized by instance\n")
        write(inst, "knowledge/x.md", "instance knowledge\n")
        git(inst, "add", "-A")
        git(inst, "commit", "-m", "instance start")
        git(inst, "remote", "add", "upstream", str(bare))
        start = git(inst, "rev-parse", "HEAD").strip()

        dry = run_upgrade(inst, "--to", "v0.2.0")
        assert dry.returncode == 0, dry.stdout + dry.stderr
        out = dry.stdout
        for needle in ("SPEC.md", "schemas/b.schema.json", "templates/old.md", "ต้องตรวจเอง",
                       "governance/AGENTS.md", "misc.txt", "(dry-run)"):
            assert needle in out, f"dry-run output missing {needle!r}:\n{out}"
        assert git(inst, "rev-parse", "HEAD").strip() == start
        assert git(inst, "branch", "--list", "agent/*").strip() == ""
        assert git(inst, "tag").strip() == "", "instance tags must not be created"

        app = run_upgrade(inst, "--to", "v0.2.0", "--apply")
        assert app.returncode == 0, app.stdout + app.stderr
        assert git(inst, "branch", "--show-current").strip() == "agent/upgrade-core-v0.2.0"
        spec = (inst / "SPEC.md").read_text(encoding="utf-8")
        assert "line two CHANGED" in spec and "local note added by instance" in spec, spec
        assert (inst / "schemas/b.schema.json").is_file()
        assert not (inst / "templates/old.md").exists()
        assert (inst / "VERSION").read_text(encoding="utf-8").strip() == "0.2.0"
        assert (inst / "governance/AGENTS.md").read_text(encoding="utf-8") == "rules customized by instance\n"
        assert (inst / "README.md").read_text(encoding="utf-8") == "template readme\n"
        assert (inst / "misc.txt").read_text(encoding="utf-8") == "not listed\n"
        assert (inst / "knowledge/x.md").is_file()
        st = git(inst, "status", "--porcelain").strip()
        assert st == "", st
        changed = git(inst, "diff", "--name-only", start, "HEAD").split()
        assert sorted(changed) == sorted(["SPEC.md", "VERSION", "schemas/b.schema.json", "templates/old.md"]), changed
        assert git(inst, "rev-parse", "main").strip() == start, "main must not move"

        again = run_upgrade(inst, "--to", "v0.2.0", "--apply")
        assert again.returncode == 0 and "ไม่มีอะไรต้องทำ" in again.stdout, again.stdout + again.stderr
    print("test_upgrade_core: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
