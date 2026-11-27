"""Environment for test subprocesses that does not depend on where the tests run.

The validator reads GITHUB_HEAD_REF (to know the PR branch) and GITHUB_ACTIONS (to print
annotations). Inside a GitHub Actions job these are set for the job itself, so a test case that
inherits them would be judged as the job's own branch. Git also honours many GIT_* variables and
the user's global/system config. Every test subprocess therefore starts from this environment and
gets only the variables its case declares.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

CI_PREFIXES = ("GITHUB_", "RUNNER_", "ACTIONS_", "GIT_")
CI_NAMES = {"CI"}
_EMPTY_GITCONFIG = Path(tempfile.gettempdir()) / "brain-hub-tests-empty.gitconfig"


def hermetic_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in CI_NAMES and not k.upper().startswith(CI_PREFIXES)}
    _EMPTY_GITCONFIG.touch(exist_ok=True)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = str(_EMPTY_GITCONFIG)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["PYTHONUTF8"] = "1"
    for k, v in (extra or {}).items():
        env[str(k)] = str(v)
    return env
