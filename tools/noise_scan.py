# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

ZONE_KEYS = ("src", "tests", "docs", "scripts", "other")
TEXT_EXT = {".py", ".md", ".yaml", ".yml", ".toml", ".json", ".sh", ".txt", ".cff"}
EXCLUDE_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
SELF_EXCLUDE_PREFIXES = ("docs/NOISE_HYGIENE_AUDIT_", "evidence/noise_hygiene_audit_")
TOP_FILE_LIMIT = 20


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: str
    rationale: str


RULES = (
    Rule(
        "todo_markers",
        r"\b(TODO|FIXME|HACK|XXX|TBD)\b",
        "unresolved implementation markers",
    ),
    Rule(
        "ai_disclaimer",
        r"(?i)(as an ai|language model|i can(?:not|\x27t))",
        "LLM disclaimer traces",
    ),
    Rule(
        "brand_mentions",
        r"(?i)\b(chatgpt|claude\.ai|copilot|anthropic|openai)\b",
        "vendor/model mentions requiring context",
    ),
    Rule(
        "pseudo_markers",
        r"(?i)\b(pseudocode|placeholder|dummy|stub|mock|temporary|temp)\b",
        "possible pseudo/non-production terms",
    ),
)


def classify_path(rel: str) -> str:
    if rel.startswith("tests/"):
        return "tests"
    if rel.startswith("docs/"):
        return "docs"
    if rel.startswith("src/"):
        return "src"
    if rel.startswith("scripts/"):
        return "scripts"
    return "other"


def iter_files(root: Path, self_exclude: set[str]) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        rel_s = str(rel)
        if any(part in EXCLUDE_PARTS for part in rel.parts):
            continue
        if rel_s in self_exclude or rel_s.startswith(SELF_EXCLUDE_PREFIXES):
            continue
        if p.suffix.lower() not in TEXT_EXT:
            continue
        files.append(p)
    return sorted(files, key=lambda x: str(x.relative_to(root)))


def scan_repository(root: Path, generated_at_utc: str, output_relpath: str) -> dict:
    self_exclude = {
        "tools/noise_audit.py",
        "tools/noise_scan.py",
        "tools/noise_policy.py",
        output_relpath,
    }
    files = iter_files(root, self_exclude)
    compiled = {r.name: re.compile(r.pattern) for r in RULES}
    summary = {
        "generated_at_utc": generated_at_utc,
        "files_scanned": len(files),
        "rules": [
            {"name": r.name, "pattern": r.pattern, "rationale": r.rationale}
            for r in RULES
        ],
        "matches": {},
    }
    for rule in RULES:
        per_file: dict[str, int] = {}
        by_zone = {k: 0 for k in ZONE_KEYS}
        total = 0
        rgx = compiled[rule.name]
        for f in files:
            rel = str(f.relative_to(root))
            count = len(list(rgx.finditer(f.read_text(encoding="utf-8", errors="ignore"))))
            if not count:
                continue
            per_file[rel] = count
            by_zone[classify_path(rel)] += count
            total += count
        files_with_matches = sorted(per_file.items(), key=lambda x: (-x[1], x[0]))
        summary["matches"][rule.name] = {
            "total": total,
            "by_zone": by_zone,
            "files": files_with_matches,
            "top_files": files_with_matches[:TOP_FILE_LIMIT],
        }
    return summary
