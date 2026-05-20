# SPDX-License-Identifier: MIT
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import json
import re

RULE_NAMES = {"todo_markers", "ai_disclaimer", "brand_mentions", "pseudo_markers"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_allowlist_schema(entries: list[dict]) -> list[str]:
    errors: list[str] = []
    for i, e in enumerate(entries):
        keys = {"path", "rule", "reason", "owner", "expires_utc"}
        if set(e) != keys:
            errors.append(f"allowlist[{i}] keys mismatch")
            continue
        if e["rule"] not in RULE_NAMES:
            errors.append(f"allowlist[{i}] invalid rule")
        if len(e["reason"]) < 10:
            errors.append(f"allowlist[{i}] reason too short")
        if not EMAIL_RE.match(e["owner"]):
            errors.append(f"allowlist[{i}] owner must be email")
        if not DATE_RE.match(e["expires_utc"]):
            errors.append(f"allowlist[{i}] expires_utc bad format")
    return errors


def load_policy_file(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("policy file must be JSON array")
    if not all(isinstance(x, dict) for x in data):
        raise ValueError("policy file entries must be objects")
    errs = _validate_allowlist_schema(data)
    if errs:
        raise ValueError("; ".join(errs))
    return data


def evaluate_policy(summary: dict, allowlist: list[dict], current_date: str | None = None) -> dict:
    now = current_date or datetime.now(UTC).strftime("%Y-%m-%d")
    violations: list[str] = []
    for e in allowlist:
        if e["expires_utc"] < now:
            violations.append(f"expired allowlist: {e['path']}:{e['rule']} ({e['expires_utc']})")

    allowances = {(e["path"], e["rule"]) for e in allowlist}

    for rule in ("todo_markers", "ai_disclaimer"):
        unauthorized_files = []
        for rel, _count in summary["matches"][rule]["top_files"]:
            if not rel.startswith("src/"):
                continue
            if (rel, rule) not in allowances:
                unauthorized_files.append(rel)
        if unauthorized_files:
            violations.append(f"unsanctioned {rule} in src files: {sorted(set(unauthorized_files))}")

    return {"status": "RED" if violations else "GREEN", "violations": violations, "allowlist_entries": len(allowlist)}
