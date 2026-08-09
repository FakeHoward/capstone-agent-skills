#!/usr/bin/env python3
"""Validate Capstone agent skills layout, metadata, claims, and fixtures.

Dependency-light: stdlib only (no PyYAML, no jsonschema package).

Exit codes:
  0  OK (warnings allowed)
  1  validation failures
  2  usage / I/O / bad arguments
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
USE_WHEN_RE = re.compile(r"(?i)\buse when\b")

MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
MAX_SKILL_LINES = 500

SCHEMA_FILES = {
    "skills.manifest.json": "schemas/skills.manifest.schema.json",
    "triggers.json": "schemas/triggers.schema.json",
    "claims.json": "schemas/claims.schema.json",
    "fixtures/pointers.json": "schemas/pointers.schema.json",
    "expected": "schemas/expected-fixture.schema.json",
}

# Patterns that indicate known unsafe/hallucinated Capstone guidance.
FORBIDDEN_PATTERNS: List[Tuple[str, str]] = [
    (
        # Allow negations like "Do not promise Capstone is thread-safe".
        r"(?i)(?<!not\s)(?<!n't\s)(?<!promise\s)\bCapstone\s+is\s+thread[- ]safe\b",
        "Promises Capstone is thread-safe",
    ),
    (
        r"(?i)(?<!not\s)\bshared\s+csh\s+is\s+thread[- ]safe\b",
        "Promises shared csh thread-safety",
    ),
    (
        r"(?i)(?:can|may)\s+(?:be\s+)?(?:disabled|cleared|turned\s+off)\s+"
        r"with\s+CS_OPT_OFF",
        "Claims detail/options can be disabled with CS_OPT_OFF",
    ),
    (
        r"(?i)\bbuild(?:ing)?\s+(?:Capstone\s+)?with\s+Meson\b",
        "Claims Meson is a supported Capstone build path",
    ),
    (
        r"(?i)\benable\s+CS_MODE_RISCV_BITMANIP\b",
        "Recommends dead CS_MODE_RISCV_BITMANIP",
    ),
]


class Reporter:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def load_json(path: Path, rep: Reporter) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        rep.error(f"missing JSON: {path}")
    except json.JSONDecodeError as exc:
        rep.error(f"invalid JSON {path}: {exc}")
    return None


def json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "null":
        return value is None
    return True


def validate_against_schema(
    data: Any,
    schema: Dict[str, Any],
    loc: str,
    rep: Reporter,
) -> None:
    """Minimal JSON Schema subset (stdlib only)."""
    if "const" in schema and data != schema["const"]:
        rep.error(f"{loc}: expected const {schema['const']!r}, got {data!r}")
        return

    if "enum" in schema and data not in schema["enum"]:
        rep.error(f"{loc}: value {data!r} not in enum {schema['enum']}")
        return

    expected_type = schema.get("type")
    if expected_type is not None:
        types = (
            expected_type
            if isinstance(expected_type, list)
            else [expected_type]
        )
        if not any(_type_matches(data, t) for t in types):
            rep.error(
                f"{loc}: expected type {expected_type}, got {json_type_name(data)}"
            )
            return

    if isinstance(data, str):
        if "minLength" in schema and len(data) < int(schema["minLength"]):
            rep.error(f"{loc}: string shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], data):
            rep.error(f"{loc}: string does not match pattern {schema['pattern']}")

    if isinstance(data, list):
        if "minItems" in schema and len(data) < int(schema["minItems"]):
            rep.error(f"{loc}: array shorter than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(data):
                validate_against_schema(item, item_schema, f"{loc}[{i}]", rep)

    if isinstance(data, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in data:
                rep.error(f"{loc}: missing required property {key!r}")
        props = schema.get("properties") or {}
        additional = schema.get("additionalProperties", True)
        for key, value in data.items():
            if key in props and isinstance(props[key], dict):
                validate_against_schema(
                    value, props[key], f"{loc}.{key}", rep
                )
            elif additional is False:
                rep.error(f"{loc}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                validate_against_schema(
                    value, additional, f"{loc}.{key}", rep
                )


def load_schema(root: Path, rel: str, rep: Reporter) -> Optional[Dict[str, Any]]:
    path = root / rel
    if not path.is_file():
        return None
    data = load_json(path, rep)
    if not isinstance(data, dict):
        if data is not None:
            rep.error(f"{rel}: schema root must be object")
        return None
    return data


def apply_document_schema(
    root: Path, rel_doc: str, data: Any, rep: Reporter
) -> None:
    schema_rel = SCHEMA_FILES.get(rel_doc)
    if not schema_rel:
        return
    schema = load_schema(root, schema_rel, rep)
    if schema is None:
        # Temp packages used in unit tests may omit schemas/.
        return
    validate_against_schema(data, schema, rel_doc, rep)


def resolve_under(root: Path, rel: str) -> Tuple[Optional[Path], Optional[str]]:
    """Resolve rel under root; return (path, None) or (None, error)."""
    if not isinstance(rel, str) or not rel.strip():
        return None, "empty relative path"
    if Path(rel).is_absolute() or rel.startswith(("/", "\\")):
        return None, "absolute path not allowed"
    root_res = root.resolve()
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root_res)
    except ValueError:
        return None, "path escapes package root"
    return candidate, None


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, str]], str]:
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, text
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1 :])
    data: Dict[str, str] = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest in (">", ">-", "|", "|-", "|+", ">+"):
            block: List[str] = []
            i += 1
            while i < len(fm_lines):
                nxt = fm_lines[i]
                if nxt.startswith("  ") or nxt.startswith("\t"):
                    block.append(nxt[2:] if nxt.startswith("  ") else nxt[1:])
                    i += 1
                elif nxt.strip() == "" and block:
                    block.append("")
                    i += 1
                else:
                    break
            data[key] = " ".join(part.strip() for part in block if part.strip())
        else:
            if (rest.startswith('"') and rest.endswith('"')) or (
                rest.startswith("'") and rest.endswith("'")
            ):
                rest = rest[1:-1]
            data[key] = rest
            i += 1
    return data, body


def count_lines(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def is_external_link(target: str) -> bool:
    t = target.strip()
    return (
        t.startswith("http://")
        or t.startswith("https://")
        or t.startswith("mailto:")
        or t.startswith("#")
    )


def link_is_one_level(target: str) -> bool:
    """Relative markdown links may be same-dir or one ../segment."""
    t = target.strip().split("#", 1)[0]
    if not t or is_external_link(t):
        return True
    norm = t.replace("\\", "/")
    if norm.startswith("/"):
        return False
    if "://" in norm:
        return True
    if "../.." in norm or norm.startswith("../../"):
        return False
    parts = [p for p in norm.split("/") if p not in ("", ".")]
    up = 0
    rest: List[str] = []
    for p in parts:
        if p == "..":
            up += 1
        else:
            rest.append(p)
    if up > 1:
        return False
    # same-dir file, or ../skill/file.md
    if up == 0:
        return len(rest) <= 1
    return len(rest) <= 2


def discover_skill_dirs(skills_root: Path) -> List[Path]:
    if not skills_root.is_dir():
        return []
    return sorted(
        p
        for p in skills_root.iterdir()
        if p.is_dir() and not p.name.startswith(".") and (p / "SKILL.md").is_file()
    )


def category_for(skill_id: str) -> str:
    if skill_id == "capstone-skill-router":
        return "router"
    if skill_id.startswith("capstone-arch-"):
        return "arch"
    if skill_id in {
        "capstone-cmake-build",
        "capstone-cross-platform",
        "capstone-size-optimized-builds",
        "capstone-custom-memory-embedding",
    }:
        return "build"
    if skill_id in {
        "capstone-cstool",
        "capstone-cstest-yaml",
        "capstone-fuzzing-crash-repro",
        "capstone-language-bindings",
    }:
        return "tooling"
    return "api"


def validate_skill_dir(skill_dir: Path, rep: Reporter) -> Dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    info: Dict[str, Any] = {
        "id": skill_dir.name,
        "path": skill_dir,
        "files": sorted(p.name for p in skill_dir.iterdir() if p.is_file()),
        "fm": fm or {},
        "text": text,
        "body": body,
    }
    if fm is None:
        rep.error(f"{skill_dir.name}: missing/invalid YAML frontmatter")
        return info

    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        rep.error(f"{skill_dir.name}: frontmatter missing name")
    else:
        if name != skill_dir.name:
            rep.error(
                f"{skill_dir.name}: name '{name}' != directory '{skill_dir.name}'"
            )
        if len(name) > MAX_NAME_LEN:
            rep.error(f"{skill_dir.name}: name length {len(name)} > {MAX_NAME_LEN}")
        if not NAME_RE.match(name):
            rep.error(f"{skill_dir.name}: name must be lowercase-hyphen: {name!r}")

    if not desc:
        rep.error(f"{skill_dir.name}: frontmatter missing description")
    else:
        if len(desc) > MAX_DESC_LEN:
            rep.error(
                f"{skill_dir.name}: description length {len(desc)} > {MAX_DESC_LEN}"
            )
        if not USE_WHEN_RE.search(desc):
            rep.error(f"{skill_dir.name}: description missing WHEN ('Use when')")
        # WHAT: leading clause before Use when should exist
        what = USE_WHEN_RE.split(desc, maxsplit=1)[0].strip()
        if len(what) < 20:
            rep.error(f"{skill_dir.name}: description missing WHAT before 'Use when'")

    if "disable-model-invocation" in fm:
        val = str(fm.get("disable-model-invocation", "")).strip().lower()
        if val in {"true", "yes", "1"}:
            rep.error(
                f"{skill_dir.name}: auto-invoke required; "
                "disable-model-invocation must not be true"
            )

    lines = count_lines(text)
    if lines >= MAX_SKILL_LINES:
        rep.error(f"{skill_dir.name}: SKILL.md has {lines} lines (>= {MAX_SKILL_LINES})")

    for match in MD_LINK_RE.finditer(text):
        target = match.group(2).strip()
        if is_external_link(target):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        if not link_is_one_level(path_part):
            rep.error(f"{skill_dir.name}: link deeper than one level: {target}")
            continue
        resolved = (skill_dir / path_part).resolve()
        try:
            resolved.relative_to(skill_dir.parent.resolve())
        except ValueError:
            rep.error(f"{skill_dir.name}: link escapes skills tree: {target}")
            continue
        if not resolved.is_file():
            rep.error(f"{skill_dir.name}: broken local link: {target}")

    for pattern, label in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            rep.error(f"{skill_dir.name}: forbidden hallucination pattern: {label}")

    return info


def validate_manifest(
    root: Path, skill_infos: Dict[str, Dict[str, Any]], rep: Reporter
) -> Any:
    path = root / "skills.manifest.json"
    data = load_json(path, rep)
    if data is None:
        return None
    if not isinstance(data, dict):
        rep.error("skills.manifest.json: root must be object")
        return None
    apply_document_schema(root, "skills.manifest.json", data, rep)

    if data.get("version") != 1:
        rep.warn("skills.manifest.json: unexpected version (expected 1)")

    source = data.get("source")
    if not isinstance(source, dict):
        rep.error("skills.manifest.json: missing source metadata object")
    else:
        for key in ("upstream_url", "branch", "commit", "api"):
            if not source.get(key):
                rep.error(f"skills.manifest.json: source.{key} required")
        if source.get("branch") != "next":
            rep.error("skills.manifest.json: source.branch must be 'next'")
        if str(source.get("commit", "")).lower() != "1c1f6f4e":
            rep.error("skills.manifest.json: source.commit must be '1c1f6f4e'")
        api = str(source.get("api", "")).lower()
        if "6" not in api or "alpha" not in api:
            rep.error("skills.manifest.json: source.api must describe API 6 alpha")

    policy = data.get("auto_invoke_policy")
    if not isinstance(policy, dict):
        rep.error("skills.manifest.json: missing auto_invoke_policy")
    else:
        if policy.get("default") is not True:
            rep.error("skills.manifest.json: auto_invoke_policy.default must be true")
        if policy.get("forbid_disable_model_invocation") is not True:
            rep.error(
                "skills.manifest.json: "
                "auto_invoke_policy.forbid_disable_model_invocation must be true"
            )

    skills = data.get("skills")
    if not isinstance(skills, list) or not skills:
        rep.error("skills.manifest.json: skills[] empty or missing")
        return data

    seen = set()
    for entry in skills:
        if not isinstance(entry, dict):
            rep.error("skills.manifest.json: skill entry must be object")
            continue
        sid = entry.get("id")
        if not sid:
            rep.error("skills.manifest.json: skill missing id")
            continue
        if sid in seen:
            rep.error(f"skills.manifest.json: duplicate id {sid}")
        seen.add(sid)
        if sid not in skill_infos:
            rep.error(f"skills.manifest.json: unknown skill id {sid}")
            continue
        rel = entry.get("path")
        expected = f"skills/{sid}"
        if rel != expected and Path(str(rel)).as_posix() != expected:
            rep.error(
                f"skills.manifest.json: {sid} path {rel!r} expected {expected!r}"
            )
        if entry.get("auto_invoke") is not True:
            rep.error(f"skills.manifest.json: {sid} auto_invoke must be true")
        expected_cat = category_for(sid)
        got_cat = entry.get("category")
        if got_cat != expected_cat:
            rep.error(
                f"skills.manifest.json: {sid} category {got_cat!r} "
                f"expected {expected_cat!r}"
            )
        listed = entry.get("files")
        actual = set(skill_infos[sid]["files"])
        if isinstance(listed, list):
            listed_set = set(listed)
            for fname in listed:
                if fname not in actual:
                    rep.error(
                        f"skills.manifest.json: {sid} lists missing file {fname}"
                    )
            if "SKILL.md" not in listed:
                rep.error(f"skills.manifest.json: {sid} must list SKILL.md")
            extra_files = sorted(actual - listed_set)
            if extra_files:
                rep.error(
                    f"skills.manifest.json: {sid} files incomplete, missing from "
                    f"manifest: {', '.join(extra_files)}"
                )
        else:
            rep.error(f"skills.manifest.json: {sid} files must be a list")

    disk_ids = set(skill_infos)
    missing = sorted(disk_ids - seen)
    extra = sorted(seen - disk_ids)
    if missing:
        rep.error(
            "skills.manifest.json: incomplete inventory, missing: "
            + ", ".join(missing)
        )
    if extra:
        rep.error(
            "skills.manifest.json: lists non-existent skills: " + ", ".join(extra)
        )
    return data


def validate_triggers(
    root: Path, skill_infos: Dict[str, Dict[str, Any]], rep: Reporter
) -> Any:
    path = root / "triggers.json"
    data = load_json(path, rep)
    if data is None:
        return None
    if isinstance(data, dict):
        apply_document_schema(root, "triggers.json", data, rep)
    triggers = data.get("triggers") if isinstance(data, dict) else None
    if not isinstance(triggers, list) or not triggers:
        rep.error("triggers.json: triggers[] empty or missing")
        return data

    by_skill: Dict[str, Dict[str, Any]] = {}
    term_owners: Dict[str, List[str]] = {}
    for entry in triggers:
        if not isinstance(entry, dict):
            rep.error("triggers.json: entry must be object")
            continue
        sid = entry.get("skill")
        if not sid:
            rep.error("triggers.json: entry missing skill")
            continue
        if sid in by_skill:
            rep.error(f"triggers.json: duplicate skill entry {sid}")
        by_skill[sid] = entry
        if sid not in skill_infos:
            rep.error(f"triggers.json: unknown skill {sid}")
            continue
        terms = entry.get("required_terms")
        prompts = entry.get("blind_prompts")
        if not isinstance(terms, list) or not terms:
            rep.error(f"triggers.json: {sid} required_terms must be non-empty list")
            terms = []
        if not isinstance(prompts, list) or not prompts:
            rep.error(f"triggers.json: {sid} blind_prompts must be non-empty list")
        desc = skill_infos[sid]["fm"].get("description", "")
        desc_l = desc.lower()
        for term in terms:
            if not isinstance(term, str) or not term.strip():
                rep.error(f"triggers.json: {sid} has empty required term")
                continue
            if term.lower() not in desc_l:
                rep.error(
                    f"triggers.json: {sid} required term {term!r} "
                    "not found in description"
                )
            term_owners.setdefault(term.lower(), []).append(sid)

    disk_ids = set(skill_infos)
    missing = sorted(disk_ids - set(by_skill))
    if missing:
        rep.error("triggers.json: missing coverage for: " + ", ".join(missing))

    # Collision: identical required_terms sets across skills.
    sets: Dict[Tuple[str, ...], List[str]] = {}
    for sid, entry in by_skill.items():
        terms = entry.get("required_terms") or []
        key = tuple(sorted(t.lower() for t in terms if isinstance(t, str)))
        sets.setdefault(key, []).append(sid)
    for key, owners in sets.items():
        if key and len(owners) > 1:
            rep.error(
                "triggers.json: colliding required_terms set for "
                + ", ".join(owners)
                + f" -> {list(key)}"
            )

    # Soft collision: exact same single exclusive term used by many skills.
    for term, owners in term_owners.items():
        uniq = sorted(set(owners))
        if len(uniq) > 8:
            rep.warn(
                f"triggers.json: term {term!r} shared by {len(uniq)} skills"
            )
    return data


def validate_claims(root: Path, capstone: Optional[Path], rep: Reporter) -> Any:
    path = root / "claims.json"
    data = load_json(path, rep)
    if data is None:
        return None
    if isinstance(data, dict):
        apply_document_schema(root, "claims.json", data, rep)
    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list) or not claims:
        rep.error("claims.json: claims[] empty or missing")
        return data
    if capstone is None:
        rep.warn("claims.json: skipped source checks (--capstone not provided)")
        return data
    if not capstone.is_dir():
        rep.error(f"--capstone path is not a directory: {capstone}")
        return data

    seen_ids = set()
    for claim in claims:
        if not isinstance(claim, dict):
            rep.error("claims.json: claim must be object")
            continue
        cid = claim.get("id") or "<missing-id>"
        if cid in seen_ids:
            rep.error(f"claims.json: duplicate claim id {cid}")
        seen_ids.add(cid)
        source_path = claim.get("source_path")
        regex = claim.get("regex")
        if not source_path or not regex:
            rep.error(f"claims.json: {cid} needs source_path and regex")
            continue
        try:
            cre = re.compile(regex, re.MULTILINE)
        except re.error as exc:
            rep.error(f"claims.json: {cid} invalid regex: {exc}")
            continue
        target = (capstone / source_path).resolve()
        try:
            target.relative_to(capstone.resolve())
        except ValueError:
            rep.error(f"claims.json: {cid} source_path escapes capstone tree")
            continue
        if not target.is_file():
            rep.error(f"claims.json: {cid} missing source file {source_path}")
            continue
        text = target.read_text(encoding="utf-8", errors="replace")
        if not cre.search(text):
            rep.error(
                f"claims.json: {cid} regex did not match {source_path}"
            )
    return data


def parse_hex_file(path: Path) -> bytes:
    raw = path.read_text(encoding="utf-8")
    # allow comments
    cleaned_lines = []
    for line in raw.splitlines():
        if "#" in line:
            line = line.split("#", 1)[0]
        cleaned_lines.append(line)
    cleaned = "".join(cleaned_lines)
    cleaned = re.sub(r"0x", "", cleaned, flags=re.I)
    cleaned = re.sub(r"[^0-9a-fA-F]", "", cleaned)
    if len(cleaned) % 2 != 0:
        raise ValueError(f"odd number of hex digits in {path}")
    return bytes.fromhex(cleaned)


def validate_expected_fixture(
    expected: Any, pid: str, root: Path, rep: Reporter
) -> None:
    if not isinstance(expected, dict):
        rep.error(f"pointers.json: {pid} expected root must be object")
        return
    schema = load_schema(root, SCHEMA_FILES["expected"], rep)
    if schema is not None:
        validate_against_schema(
            expected, schema, f"fixtures/expected[{pid}]", rep
        )
    has_insns = "insns" in expected
    has_cases = "cases" in expected
    if not has_insns and not has_cases:
        rep.error(f"pointers.json: {pid} expected needs insns or cases")
        return
    if has_insns:
        insns = expected.get("insns")
        if not isinstance(insns, list):
            rep.error(f"pointers.json: {pid} expected.insns must be a list")
        else:
            for i, item in enumerate(insns):
                if not isinstance(item, dict):
                    rep.error(
                        f"pointers.json: {pid} expected.insns[{i}] must be object"
                    )
    if has_cases:
        cases = expected.get("cases")
        if not isinstance(cases, list):
            rep.error(f"pointers.json: {pid} expected.cases must be a list")
        else:
            for i, case in enumerate(cases):
                if not isinstance(case, dict):
                    rep.error(
                        f"pointers.json: {pid} expected.cases[{i}] must be object"
                    )
                    continue
                nested = case.get("insns")
                if nested is None:
                    continue
                if not isinstance(nested, list):
                    rep.error(
                        f"pointers.json: {pid} expected.cases[{i}].insns "
                        "must be a list"
                    )
                    continue
                for j, item in enumerate(nested):
                    if not isinstance(item, dict):
                        rep.error(
                            f"pointers.json: {pid} "
                            f"expected.cases[{i}].insns[{j}] must be object"
                        )


def validate_fixtures(
    root: Path,
    skill_infos: Dict[str, Dict[str, Any]],
    rep: Reporter,
) -> Any:
    path = root / "fixtures" / "pointers.json"
    data = load_json(path, rep)
    if data is None:
        return None
    if isinstance(data, dict):
        apply_document_schema(root, "fixtures/pointers.json", data, rep)
    pointers = data.get("pointers") if isinstance(data, dict) else None
    if not isinstance(pointers, list) or not pointers:
        rep.error("fixtures/pointers.json: pointers[] empty or missing")
        return data

    required_ids = {
        "x86-batch",
        "x86-skipdata",
        "aarch64-smoke",
        "alias-detail",
        "riscv-regs",
    }
    seen = set()
    for entry in pointers:
        if not isinstance(entry, dict):
            rep.error("pointers.json: entry must be object")
            continue
        pid = entry.get("id")
        if not pid:
            rep.error("pointers.json: entry missing id")
            continue
        seen.add(pid)
        skill = entry.get("skill")
        if not skill:
            rep.error(f"pointers.json: {pid} missing skill")
        elif skill not in skill_infos:
            rep.error(f"pointers.json: {pid} unknown skill {skill!r}")
        hex_rel = entry.get("hex")
        exp_rel = entry.get("expected")
        if not hex_rel or not exp_rel:
            rep.error(f"pointers.json: {pid} needs hex and expected")
            continue

        hex_path, hex_err = resolve_under(root, str(hex_rel))
        if hex_err:
            rep.error(f"pointers.json: {pid} hex {hex_err}: {hex_rel}")
        elif hex_path is None or not hex_path.is_file():
            rep.error(f"pointers.json: {pid} missing hex file {hex_rel}")
        else:
            try:
                blob = parse_hex_file(hex_path)
                if not blob:
                    rep.error(f"pointers.json: {pid} hex file empty")
            except ValueError as exc:
                rep.error(f"pointers.json: {pid} hex parse error: {exc}")

        exp_path, exp_err = resolve_under(root, str(exp_rel))
        if exp_err:
            rep.error(f"pointers.json: {pid} expected {exp_err}: {exp_rel}")
        elif exp_path is None or not exp_path.is_file():
            rep.error(f"pointers.json: {pid} missing expected file {exp_rel}")
        else:
            try:
                expected = json.loads(exp_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                rep.error(f"pointers.json: {pid} expected JSON invalid: {exc}")
                continue
            validate_expected_fixture(expected, pid, root, rep)
            if not entry.get("upstream"):
                rep.warn(f"pointers.json: {pid} missing upstream pointer")
    missing = sorted(required_ids - seen)
    if missing:
        rep.error(
            "pointers.json: missing required scenarios: " + ", ".join(missing)
        )
    return data


def print_report(rep: Reporter, skill_count: int) -> None:
    print(f"skills scanned: {skill_count}")
    print(f"warnings: {len(rep.warnings)}")
    print(f"failures: {len(rep.errors)}")
    for w in rep.warnings:
        print(f"WARNING: {w}")
    for e in rep.errors:
        print(f"ERROR: {e}")
    if rep.ok:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


def run_validation(root: Path, capstone: Optional[Path]) -> int:
    rep = Reporter()
    skills_root = root / "skills"
    skill_dirs = discover_skill_dirs(skills_root)
    if not skill_dirs:
        rep.error(f"no skill directories with SKILL.md under {skills_root}")
        print_report(rep, 0)
        return 1

    skill_infos: Dict[str, Dict[str, Any]] = {}
    for d in skill_dirs:
        info = validate_skill_dir(d, rep)
        skill_infos[d.name] = info

    validate_manifest(root, skill_infos, rep)
    validate_triggers(root, skill_infos, rep)
    validate_claims(root, capstone, rep)
    validate_fixtures(root, skill_infos, rep)

    print_report(rep, len(skill_infos))
    return 0 if rep.ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate capstone-agent-skills package integrity."
    )
    p.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Skills repo root (default: parent of scripts/)",
    )
    p.add_argument(
        "--capstone",
        type=Path,
        default=None,
        help="Path to Capstone source tree for claims checks",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        return code if code else 0

    root = (args.root or repo_root_from_script()).resolve()
    if not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 2
    capstone = args.capstone.resolve() if args.capstone else None
    try:
        return run_validation(root, capstone)
    except OSError as exc:
        print(f"ERROR: I/O failure: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
