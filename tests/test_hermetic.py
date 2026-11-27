#!/usr/bin/env python3
"""Regression tests: results must not depend on the environment the tests run in.

1. The fixture suite passes when the calling environment looks like a GitHub Actions
   pull_request job on an agent/ branch (plus a stray GIT_DIR).
2. Called directly (not through the test runner), the guard still rejects an agent/ branch
   that has no base: the fail-closed rule is unchanged.
3. The validator reads the repository named by --root even when GIT_DIR points elsewhere.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VALIDATE = ROOT / "scripts" / "validate.py"
GIT_ID = ["-c", "user.name=test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
          "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def polluted_env(**extra: str) -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "CI": "true",
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_HEAD_REF": "agent/bootstrap-master",
        "GITHUB_BASE_REF": "main",
        "GITHUB_REF": "refs/pull/1/merge",
        "GITHUB_REF_NAME": "1/merge",
    })
    env.update(extra)
    return env


def run(cmd, env, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8")


def git(cwd: Path, *args) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    res = run(["git", *GIT_ID, *args], env, cwd=cwd)
    assert res.returncode == 0, res.stderr
    return res.stdout


def write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


NOTE = ("---\nid: fld-x-a\ntype: field\ntitle: x.a\nclassification: public\nspec_version: 0.1.0\n"
        "created: 2026-11-01\nupdated: 2026-11-01\nstatus: {status}\nsource_system: x\n---\n")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        decoy = t / "decoy"
        git(t, "init", "-q", str(decoy))
        write(decoy, "x.txt", "decoy\n")
        git(decoy, "add", "-A")
        git(decoy, "commit", "-q", "-m", "decoy")
        stray = {"GIT_DIR": str(decoy / ".git")}

        res = run([sys.executable, str(HERE / "run_tests.py"), "--fixtures-only"], polluted_env(**stray))
        assert res.returncode == 0, "fixtures must pass under a CI-like environment:\n" + res.stdout + res.stderr

        full_root = HERE / "fixtures" / "valid" / "full" / "root"
        res = run([sys.executable, str(VALIDATE), "guards", "--root", str(full_root)], polluted_env())
        assert res.returncode == 1 and "ERROR governance-touched" in res.stdout, res.stdout + res.stderr
        res = run([sys.executable, str(VALIDATE), "guards", "--root", str(full_root), "--head-ref", "agent/x"],
                  {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")})
        assert res.returncode == 1 and "ERROR governance-touched" in res.stdout, res.stdout + res.stderr

        repo = t / "brain"
        git(t, "init", "-q", str(repo))
        write(repo, "governance/profile.yml", "role: master\nallowed_classifications: [public]\n")
        write(repo, "knowledge/fields/a.md", NOTE.format(status="deprecated"))
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "base")
        base = git(repo, "rev-parse", "HEAD").strip()
        write(repo, "knowledge/fields/a.md", NOTE.format(status="proposed"))
        git(repo, "commit", "-q", "-am", "head")
        res = run([sys.executable, str(VALIDATE), "structure", "--root", str(repo), "--base", base,
                   "--head-ref", "feature/x"], polluted_env(**stray))
        assert res.returncode == 1 and "ERROR bad-transition" in res.stdout, \
            "validator must read the --root repository, not GIT_DIR:\n" + res.stdout + res.stderr
    print("test_hermetic: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
