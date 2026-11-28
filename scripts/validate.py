#!/usr/bin/env python3
"""Brain Hub validator (SPEC §12).

Commands:
  structure   schema, ids, links, references, status-rules, skills.lock.yml, governance files
  guards      governance-guard, classification-guard, secrets
  freshness   stale-report (warnings only, always exits 0)
  run-checks  re-run the `kind: test` evidence scripts of notes verified by `check:`
  all         structure + guards + freshness

Exit code: 0 = no errors, 1 = errors found, 2 = bad usage.
Needs Python 3.10+, jsonschema and pyyaml. Never uses the network.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

TOOL_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = TOOL_ROOT / "schemas"
NOTE_DIRS = ("knowledge", "decisions", "repos", "work", "research", "examples")
NOT_NOTES = {"index.md", "README.md"}
SKIP_DIRS = {".git", "node_modules", ".obsidian", "__pycache__", ".venv"}
TOP_LEVEL_SKIP = {"tests"}
KNOWLEDGE_TYPES = {"system", "entity", "field", "rule", "query", "dq", "glossary"}
PROTECTED_PREFIX = "governance/"
# Files that decide how the repo is checked or what agents may do. A branch agent/ may change them,
# but every changed one is reported (warning) for human review. ".github/CODEOWNERS" must list each
# of these and PROTECTED_PREFIX (tests/test_control_plane.py). Entries ending in "/" = whole folder.
CONTROL_PLANE_PATHS = (
    "scripts/",
    "schemas/",
    "tests/",
    ".github/",
    ".claude/settings.json",
    ".claude/agents/",
    "core-paths.txt",
    "SPEC.md",
    "PRINCIPLES.md",
)
AGENT_PREFIX = "agent/"
EXAMPLES_PREFIX = "examples/"
TRANSITIONS = {
    "proposed": {"proposed", "unverified", "conflicted", "deprecated"},
    "unverified": {"unverified", "proven", "conflicted", "deprecated"},
    "proven": {"proven", "deprecated", "conflicted"},
    "conflicted": {"conflicted", "unverified", "proven", "deprecated"},
    "deprecated": {"deprecated"},
}
SECRET_PATTERNS = [
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("anthropic-api-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai-api-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b")),
    ("stripe-live-key", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{20,}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----")),
    ("url-with-credentials", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@'\"<>]+:[^\s/@'\"<>]+@[^\s/'\"<>]+")),
]
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#\n]+)(?:#[^\]|\n]*)?(?:\|[^\]\n]*)?\]\]")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


@dataclass
class Report:
    errors: list[tuple[str, str, str]] = field(default_factory=list)
    warnings: list[tuple[str, str, str]] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)

    def error(self, code: str, path: str, msg: str) -> None:
        self.errors.append((code, path, msg))

    def warn(self, code: str, path: str, msg: str) -> None:
        self.warnings.append((code, path, msg))

    def notice(self, msg: str) -> None:
        self.notices.append(msg)


@dataclass
class Note:
    path: str
    meta: dict | None
    body: str
    problem: str | None = None


_GIT_LOCAL_VARS: list[str] | None = None


def clean_git_env() -> dict[str, str]:
    """Environment for git commands aimed at an explicit folder (git -C <dir>).

    Variables such as GIT_DIR or GIT_INDEX_FILE (set inside git hooks, for example) would make
    git act on a different repository than the one named. The list comes from git itself.
    """
    global _GIT_LOCAL_VARS
    if _GIT_LOCAL_VARS is None:
        res = subprocess.run(["git", "rev-parse", "--local-env-vars"], capture_output=True, text=True)
        _GIT_LOCAL_VARS = res.stdout.split() if res.returncode == 0 else []
    return {k: v for k, v in os.environ.items() if k not in _GIT_LOCAL_VARS}


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def normalize(value):
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    text = text.lstrip("﻿")
    if not text.startswith("---"):
        return None, text, "ไม่มี frontmatter (บรรทัดแรกต้องเป็น ---)"
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text, "บรรทัดแรกต้องเป็น --- อย่างเดียว"
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            raw = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1:])
            try:
                meta = yaml.safe_load(raw)
            except yaml.YAMLError as exc:
                return None, body, f"YAML อ่านไม่ได้: {exc}"
            if not isinstance(meta, dict):
                return None, body, "frontmatter ต้องเป็น mapping"
            return normalize(meta), body, None
    return None, text, "frontmatter ไม่มี --- ปิดท้าย"


def walk_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in SKIP_DIRS and not (here == root and d in TOP_LEVEL_SKIP)
        )
        for name in sorted(filenames):
            yield here / name


def is_note_path(relpath: str) -> bool:
    parts = relpath.split("/")
    return parts[0] in NOTE_DIRS and relpath.endswith(".md") and parts[-1] not in NOT_NOTES


def load_notes(root: Path) -> list[Note]:
    notes = []
    for p in walk_files(root):
        r = rel(root, p)
        if not is_note_path(r):
            continue
        meta, body, problem = split_frontmatter(p.read_text(encoding="utf-8"))
        notes.append(Note(r, meta, body, problem))
    return notes


def build_registry() -> tuple[Registry, dict[str, dict]]:
    resources = []
    by_name = {}
    for f in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = json.loads(f.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
        by_name[f.name[: -len(".schema.json")]] = schema
    return Registry().with_resources(resources), by_name


def schema_errors(schema: dict, registry: Registry, data) -> list[str]:
    validator = Draft202012Validator(schema, registry=registry)
    out = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(x) for x in err.absolute_path) or "(root)"
        out.append(f"{where}: {err.message}")
    return out


class BaseView:
    """Read-only view of the base revision: a git ref or a directory snapshot."""

    def __init__(self, root: Path, ref: str | None = None, directory: Path | None = None):
        self.root, self.ref, self.directory = root, ref, directory

    @property
    def available(self) -> bool:
        return self.ref is not None or self.directory is not None

    def text(self, relpath: str) -> str | None:
        if self.directory is not None:
            p = self.directory / relpath
            return p.read_text(encoding="utf-8") if p.is_file() else None
        if self.ref is not None:
            res = subprocess.run(["git", "-C", str(self.root), "show", f"{self.ref}:{relpath}"],
                                 capture_output=True, text=True, encoding="utf-8", env=clean_git_env())
            return res.stdout if res.returncode == 0 else None
        return None

    def has_prefix(self, prefix: str) -> bool:
        if self.directory is not None:
            d = self.directory / prefix
            return d.is_dir() and any(x.is_file() for x in d.rglob("*"))
        if self.ref is not None:
            res = subprocess.run(["git", "-C", str(self.root), "ls-tree", "-r", "--name-only", self.ref, "--", prefix],
                                 capture_output=True, text=True, encoding="utf-8", env=clean_git_env())
            return bool(res.stdout.strip())
        return False


def git_ref_ok(root: Path, ref: str) -> bool:
    res = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                         capture_output=True, text=True, env=clean_git_env())
    return res.returncode == 0


def make_base(args, root: Path, report: Report) -> BaseView:
    if args.base_dir:
        return BaseView(root, directory=Path(args.base_dir).resolve())
    if args.base:
        if set(args.base) == {"0"} or not git_ref_ok(root, args.base):
            report.notice(f"base {args.base!r} ใช้ไม่ได้ — ข้ามการตรวจที่ต้องเทียบกับ base")
            return BaseView(root)
        return BaseView(root, ref=args.base)
    return BaseView(root)


def changed_files(args, root: Path, base: BaseView) -> list[str] | None:
    if args.changed_files:
        lines = Path(args.changed_files).read_text(encoding="utf-8").splitlines()
        return [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")]
    if base.ref is not None:
        res = subprocess.run(["git", "-C", str(root), "diff", "--name-only", "--no-renames", base.ref, "HEAD"],
                             capture_output=True, text=True, encoding="utf-8", env=clean_git_env())
        if res.returncode == 0:
            return [ln for ln in res.stdout.splitlines() if ln]
    return None


# ---------------------------------------------------------------- structure

def check_schema_and_ids(notes, registry, schemas, report) -> dict[str, Note]:
    by_id: dict[str, Note] = {}
    for n in notes:
        if n.problem:
            report.error("frontmatter", n.path, n.problem)
            continue
        t = n.meta.get("type")
        if t not in schemas or t in {"common"}:
            report.error("schema", n.path, f"type ไม่รู้จัก: {t!r}")
            continue
        for msg in schema_errors(schemas[t], registry, n.meta):
            report.error("schema", n.path, msg)
        nid = n.meta.get("id")
        if isinstance(nid, str):
            if nid in by_id:
                report.error("duplicate-id", n.path, f"id {nid!r} ซ้ำกับ {by_id[nid].path}")
            else:
                by_id[nid] = n
    return by_id


def strip_code(text: str) -> list[str]:
    out, in_fence = [], False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE_RE.sub("", line))
    return out


def check_links(root: Path, report: Report) -> None:
    md_files = [p for p in walk_files(root) if p.suffix == ".md"]
    stems = {p.stem for p in md_files} | {rel(root, p)[:-3] for p in md_files}
    for p in md_files:
        r = rel(root, p)
        text = p.read_text(encoding="utf-8")
        _, body, _ = split_frontmatter(text)
        offset = text.count("\n") - body.count("\n")
        for i, line in enumerate(strip_code(body), start=1 + offset):
            for m in LINK_RE.finditer(line):
                target = m.group(1)
                if target.startswith("#") or SCHEME_RE.match(target):
                    continue
                target = urllib.parse.unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not target:
                    continue
                dest = (root / target.lstrip("/")) if target.startswith("/") else (p.parent / target)
                dest = Path(os.path.normpath(dest))
                try:
                    dest.relative_to(root)
                except ValueError:
                    report.error("broken-link", f"{r}:{i}", f"ลิงก์ออกนอก repo: {m.group(1)}")
                    continue
                if not dest.exists():
                    report.error("broken-link", f"{r}:{i}", f"ไม่พบปลายทาง: {m.group(1)}")
            for m in WIKILINK_RE.finditer(line):
                name = m.group(1).strip()
                if name.endswith(".md"):
                    name = name[:-3]
                if name not in stems:
                    report.error("broken-link", f"{r}:{i}", f"ไม่พบโน้ตของ wikilink: [[{m.group(1)}]]")


def path_exists(root: Path, value: str) -> bool:
    p = Path(os.path.normpath(root / value))
    try:
        p.relative_to(root)
    except ValueError:
        return False
    return p.exists()


def check_refs(root: Path, notes, by_id, report: Report) -> None:
    for n in notes:
        m = n.meta
        if not m:
            continue
        t = m.get("type")
        for key in ("supersedes", "superseded_by"):
            v = m.get(key)
            if isinstance(v, str) and v not in by_id:
                report.error("missing-ref", n.path, f"{key}: ไม่พบ id {v!r}")
        for v in m.get("conflicts_with") or []:
            if isinstance(v, str) and v not in by_id:
                report.error("missing-ref", n.path, f"conflicts_with: ไม่พบ id {v!r}")
        if t in {"handoff", "run"}:
            v = m.get("task")
            if isinstance(v, str) and v not in by_id:
                report.error("missing-ref", n.path, f"task: ไม่พบ id {v!r}")
        if t == "task":
            for v in m.get("context") or []:
                if isinstance(v, str) and not path_exists(root, v):
                    report.error("missing-ref", n.path, f"context: ไม่พบไฟล์ {v!r}")
        if t == "handoff":
            for v in m.get("knowledge_proposals") or []:
                if isinstance(v, str) and not path_exists(root, v):
                    report.error("missing-ref", n.path, f"knowledge_proposals: ไม่พบไฟล์ {v!r}")


def check_status_rules(root: Path, notes, report: Report) -> None:
    for n in notes:
        m = n.meta
        if not m or m.get("type") not in KNOWLEDGE_TYPES:
            continue
        status = m.get("status")
        if status == "proven":
            evidence = m.get("evidence") or []
            if not evidence:
                report.error("proven-without-evidence", n.path, "proven ต้องมี evidence อย่างน้อย 1 รายการ")
            for key in ("verified_at", "verified_commit", "verified_by"):
                if not m.get(key):
                    report.error("proven-without-evidence", n.path, f"proven ต้องมี {key}")
            vb = m.get("verified_by") or ""
            if isinstance(vb, str) and vb.startswith("check:"):
                ok = [e for e in evidence if isinstance(e, dict) and e.get("kind") == "test"
                      and e.get("result") == "pass" and isinstance(e.get("ref"), str)
                      and path_exists(root, e["ref"])]
                if not ok:
                    report.error("proven-without-evidence", n.path,
                                 "verified_by: check:… ต้องมี evidence kind: test, result: pass และ ref ชี้ไฟล์ที่มีอยู่ใน repo")
        if status == "conflicted" and not m.get("conflicts_with"):
            report.error("status-rule", n.path, "conflicted ต้องมี conflicts_with")


def check_transitions(notes, base: BaseView, head_ref: str | None, report: Report) -> None:
    if not base.available:
        report.notice("status transitions: ไม่ได้รัน (ไม่มี base ให้เทียบ)")
        return
    is_agent = bool(head_ref and head_ref.startswith(AGENT_PREFIX))
    for n in notes:
        m = n.meta
        if not m or m.get("type") not in KNOWLEDGE_TYPES:
            continue
        new = m.get("status")
        old_text = base.text(n.path)
        old = None
        if old_text is not None:
            old_meta, _, problem = split_frontmatter(old_text)
            if not problem:
                old = old_meta.get("status")
        if old in TRANSITIONS and new not in TRANSITIONS[old]:
            report.error("bad-transition", n.path, f"เปลี่ยนสถานะ {old} → {new} ไม่ได้ (SPEC §5.2)")
        if is_agent and new == "proven" and old != "proven" and not n.path.startswith(EXAMPLES_PREFIX):
            report.error("agent-promoted-proven", n.path,
                         f"branch {head_ref} ยกสถานะเป็น proven เองไม่ได้ — ต้องให้ Approver (มนุษย์) ทำ")


def check_yaml_file(root: Path, relpath: str, schema_name: str, registry, schemas, report: Report):
    p = root / relpath
    if not p.is_file():
        return None
    try:
        data = normalize(yaml.safe_load(p.read_text(encoding="utf-8")))
    except yaml.YAMLError as exc:
        report.error("schema", relpath, f"YAML อ่านไม่ได้: {exc}")
        return None
    for msg in schema_errors(schemas[schema_name], registry, data):
        report.error("schema", relpath, msg)
    return data


def cmd_structure(args, root: Path, report: Report) -> None:
    registry, schemas = build_registry()
    notes = load_notes(root)
    by_id = check_schema_and_ids(notes, registry, schemas, report)
    check_links(root, report)
    check_refs(root, notes, by_id, report)
    check_status_rules(root, notes, report)
    base = make_base(args, root, report)
    check_transitions(notes, base, head_ref_of(args), report)
    lock = check_yaml_file(root, "skills.lock.yml", "skills-lock", registry, schemas, report)
    if isinstance(lock, dict):
        for s in lock.get("skills") or []:
            if isinstance(s, dict) and s.get("status") == "unresolved":
                level = report.warn
                level("skills-unresolved", "skills.lock.yml",
                      f"{s.get('name')}: ยังเป็น unresolved ({'required' if s.get('required') else 'optional'})")
    check_yaml_file(root, "governance/commands.yml", "commands", registry, schemas, report)
    check_yaml_file(root, "governance/profile.yml", "profile", registry, schemas, report)
    report.notice(f"structure: ตรวจโน้ต {len(notes)} ไฟล์")


# ---------------------------------------------------------------- guards

def head_ref_of(args) -> str | None:
    return args.head_ref or os.environ.get("GITHUB_HEAD_REF") or None


def is_agent_branch(head: str | None) -> bool:
    return bool(head and head.startswith(AGENT_PREFIX))


def is_control_plane(path: str) -> bool:
    return any(path.startswith(p) if p.endswith("/") else path == p for p in CONTROL_PLANE_PATHS)


def check_governance_guard(head: str | None, base: BaseView | None, files: list[str] | None,
                           report: Report) -> None:
    if not is_agent_branch(head):
        report.notice(f"governance-guard: ผ่าน (head ref {head!r} ไม่ใช่ branch agent/)")
        return
    if files is None:
        report.error("governance-touched", "-", "branch agent/ แต่หาไฟล์ที่เปลี่ยนไม่ได้ (ไม่มี base) — ปฏิเสธไว้ก่อน")
        return
    touched = [f for f in files if f.startswith(PROTECTED_PREFIX)]
    if not touched:
        report.notice(f"governance-guard: ผ่าน ({len(files)} ไฟล์ที่เปลี่ยน ไม่แตะ governance/)")
        return
    if not base.available:
        report.error("governance-touched", "-", "แตะ governance/ และไม่มี base ให้ตรวจ — ปฏิเสธไว้ก่อน")
        return
    if not base.has_prefix(PROTECTED_PREFIX):
        for f in touched:
            report.warn("governance-bootstrap", f, "base ยังไม่มี governance/ — อนุญาตการสร้างครั้งแรก (bootstrap) ต้องให้มนุษย์รีวิว")
        return
    for f in touched:
        report.error("governance-touched", f, f"branch {head} แตะ governance/ ไม่ได้ (SPEC §9.1)")


def check_control_plane(head: str | None, files: list[str] | None, report: Report) -> None:
    if not is_agent_branch(head):
        report.notice(f"control-plane: ไม่ตรวจ (head ref {head!r} ไม่ใช่ branch agent/)")
        return
    if files is None:
        report.notice("control-plane: ตรวจไม่ได้เพราะหาไฟล์ที่เปลี่ยนไม่ได้ (governance-guard ปฏิเสธไว้แล้ว)")
        return
    touched = [f for f in files if is_control_plane(f)]
    if not touched:
        report.notice(f"control-plane: ไม่แตะ ({len(files)} ไฟล์ที่เปลี่ยน)")
        return
    for f in touched:
        report.warn("control-plane-touched", f,
                    f"branch {head} แก้ไฟล์ control-plane (ตัวตรวจ/กฎ/CI ของ repo) — "
                    "ต้องให้มนุษย์รีวิวไฟล์นี้ก่อน merge (SPEC §9.1)")


def check_classification(root: Path, report: Report) -> None:
    p = root / "governance" / "profile.yml"
    if not p.is_file():
        report.error("classification-not-allowed", "governance/profile.yml", "ไม่พบ profile.yml — ไม่รู้ว่า repo นี้รับระดับไหน")
        return
    profile = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    allowed = set(profile.get("allowed_classifications") or [])
    if profile.get("role") == "master" and allowed != {"public"}:
        report.error("classification-not-allowed", "governance/profile.yml", "repo แบบ master รับได้แค่ public")
        allowed = {"public"}
    for n in load_notes(root):
        if not n.meta:
            continue
        c = n.meta.get("classification")
        if c not in allowed:
            report.error("classification-not-allowed", n.path, f"classification {c!r} ไม่อยู่ใน {sorted(allowed)}")


def check_secrets(root: Path, report: Report) -> None:
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                data = p.read_bytes()
            except OSError:
                continue
            if b"\0" in data[:8192] or len(data) > 2_000_000:
                continue
            scanned += 1
            text = data.decode("utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), start=1):
                for label, pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        report.error("secret-found", f"{rel(root, p)}:{lineno}", f"พบรูปแบบที่ดูเหมือน {label}")
    report.notice(f"secrets: สแกน {scanned} ไฟล์")


def cmd_guards(args, root: Path, report: Report) -> None:
    head = head_ref_of(args)
    base, files = None, None
    if is_agent_branch(head):
        base = make_base(args, root, report)
        files = changed_files(args, root, base)
    check_governance_guard(head, base, files, report)
    check_control_plane(head, files, report)
    check_classification(root, report)
    check_secrets(root, report)


# ---------------------------------------------------------------- freshness

def cmd_freshness(args, root: Path, report: Report) -> None:
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    stale = 0
    for n in load_notes(root):
        m = n.meta
        if not m:
            continue
        ra = m.get("review_after")
        if isinstance(ra, str):
            try:
                due = dt.date.fromisoformat(ra)
            except ValueError:
                continue
            if due < today:
                stale += 1
                report.warn("stale", n.path, f"เลย review_after ({ra}) แล้ว สถานะ {m.get('status')}")
        if "needs-reverify" in (m.get("tags") or []):
            report.warn("needs-reverify", n.path, "ติด tag needs-reverify")
    report.notice(f"freshness: โน้ตที่เลยกำหนด {stale} ไฟล์ (เตือนอย่างเดียว)")


# ---------------------------------------------------------------- run-checks

def cmd_run_checks(args, root: Path, report: Report) -> None:
    seen = set()
    for n in load_notes(root):
        m = n.meta
        if not m or m.get("status") != "proven" or not str(m.get("verified_by") or "").startswith("check:"):
            continue
        for e in m.get("evidence") or []:
            if not (isinstance(e, dict) and e.get("kind") == "test" and isinstance(e.get("ref"), str)):
                continue
            ref = e["ref"]
            if ref in seen or not ref.endswith(".py") or not path_exists(root, ref):
                continue
            seen.add(ref)
            try:
                res = subprocess.run([sys.executable, str(root / ref)], cwd=root, capture_output=True,
                                     text=True, encoding="utf-8", timeout=120)
            except subprocess.TimeoutExpired:
                report.error("check-failed", ref, "หมดเวลา 120 วินาที")
                continue
            if res.returncode != 0:
                report.error("check-failed", ref, f"exit {res.returncode}: {(res.stdout + res.stderr).strip()[-300:]}")
            else:
                report.notice(f"run-checks: {ref} ผ่าน")
    if not seen:
        report.notice("run-checks: ไม่มี check ให้รัน")


# ---------------------------------------------------------------- main

def emit(report: Report, check: str) -> None:
    gha = os.environ.get("GITHUB_ACTIONS") == "true"
    for msg in report.notices:
        print(f"[{check}] {msg}")
    for code, path, msg in report.warnings:
        if gha:
            f = path.split(":")[0]
            print(f"::warning file={f},title={code}::{msg}")
        print(f"[{check}] WARNING {code} {path}: {msg}")
    for code, path, msg in report.errors:
        if gha:
            f = path.split(":")[0]
            print(f"::error file={f},title={code}::{msg}")
        print(f"[{check}] ERROR {code} {path}: {msg}")
    print(f"[{check}] สรุป: error {len(report.errors)}, warning {len(report.warnings)}")


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Brain Hub validator (SPEC §12)")
    ap.add_argument("command", choices=["structure", "guards", "freshness", "run-checks", "all"])
    ap.add_argument("--root", default=str(TOOL_ROOT), help="root ของ Brain repo ที่จะตรวจ (ค่าเริ่มต้น: repo นี้)")
    ap.add_argument("--base", help="git ref ของ base (เช่น commit ของ main) สำหรับตรวจการเปลี่ยนแปลง")
    ap.add_argument("--base-dir", help="โฟลเดอร์ snapshot ของ base (ใช้ในชุดทดสอบ)")
    ap.add_argument("--head-ref", help="ชื่อ branch ที่เปิด PR (ค่าเริ่มต้น: GITHUB_HEAD_REF)")
    ap.add_argument("--changed-files", help="ไฟล์รายชื่อพาธที่เปลี่ยน บรรทัดละพาธ (แทน git diff)")
    ap.add_argument("--today", help="วันที่อ้างอิงสำหรับ freshness (YYYY-MM-DD)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ไม่พบโฟลเดอร์ {root}", file=sys.stderr)
        return 2
    commands = {"structure": cmd_structure, "guards": cmd_guards, "freshness": cmd_freshness,
                "run-checks": cmd_run_checks}
    selected = ["structure", "guards", "freshness"] if args.command == "all" else [args.command]
    failed = False
    for name in selected:
        report = Report()
        commands[name](args, root, report)
        emit(report, name)
        if report.errors and name != "freshness":
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
