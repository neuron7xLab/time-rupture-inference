# SPDX-License-Identifier: MIT
"""Dependency trust gate (PR L). Stdlib-only. Fails closed if a CI
workflow installs dependencies loosely instead of from the pinned
lock, if mypy is undeclared, if the lock is missing or unconsumed, if
hash-locking is claimed without hashes, or if any doc overclaims
hermeticity. Honest level: LEVEL_1_PINNED_NO_HASHES.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_WF = _ROOT / ".github" / "workflows"
_LOCK = _ROOT / "requirements-ci.lock"
_PYPROJECT = _ROOT / "pyproject.toml"
_CONTRACT = _ROOT / "docs" / "DEPENDENCY_TRUST_CONTRACT.md"

_PIP = re.compile(r"pip install\b(.*)$")
# install forms that are deterministic / allowed
_ALLOWED = (
    "-r requirements-ci.lock",
    "-c requirements-ci.lock",
    "--upgrade pip",
    "-e . --no-deps",
)


def _lock_has_hashes() -> bool:
    """Real pip hash lines only — ignore comments (the lock's own
    header mentions the word '--hash' in prose)."""
    if not _LOCK.exists():
        return False
    for ln in _LOCK.read_text().splitlines():
        s = ln.strip()
        if s.startswith("#"):
            continue
        if re.search(r"--hash=sha256:[0-9a-f]{64}", s):
            return True
    return False


def _workflows() -> list[Path]:
    return sorted([*_WF.glob("*.yml"), *_WF.glob("*.yaml")])


def audit() -> list[str]:
    problems: list[str] = []

    if not _LOCK.exists():
        problems.append("requirements-ci.lock missing")

    pp = _PYPROJECT.read_text() if _PYPROJECT.exists() else ""
    dev_m = re.search(r"(?ms)^dev\s*=\s*\[(.*?)\]", pp)
    if not dev_m or "mypy" not in dev_m.group(1):
        problems.append("mypy not declared in pyproject [dev] deps")
    if dev_m and "types-PyYAML" not in dev_m.group(1):
        problems.append("types-PyYAML not declared in pyproject [dev] deps")


    consumes_lock = False
    for wf in _workflows():
        for ln in wf.read_text().splitlines():
            m = _PIP.search(ln)
            if not m:
                continue
            args = m.group(1).strip()
            if "requirements-ci.lock" in args:
                consumes_lock = True
            if any(tok in args for tok in _ALLOWED):
                continue
            problems.append(
                f"{wf.name}: loose pip install (not from "
                f"requirements-ci.lock / -e . --no-deps): "
                f"pip install {args}"
            )
    if _LOCK.exists() and not consumes_lock:
        problems.append("no workflow consumes requirements-ci.lock")

    doc = _CONTRACT.read_text() if _CONTRACT.exists() else ""
    low = doc.lower()
    has_hashes = _lock_has_hashes()
    if ("--require-hashes" in low or "hash-locked" in low) and not has_hashes:
        if "level_1_pinned_no_hashes" not in low:
            problems.append(
                "DEPENDENCY_TRUST_CONTRACT.md claims hash-locking "
                "without hashes and without the LEVEL_1 disclaimer"
            )
    if "hermetic" in low and "not hermetic" not in low:
        problems.append(
            "DEPENDENCY_TRUST_CONTRACT.md uses 'hermetic' without "
            "negating it (build is not hermetic)"
        )
    return problems


def main() -> int:
    problems = audit()
    out = _ROOT / "evidence" / "DEPENDENCY_TRUST_AUDIT.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "status": "PASS" if not problems else "FAIL",
                "hermeticity_level": "LEVEL_1_PINNED_NO_HASHES",
                "lock": "requirements-ci.lock",
                "problems": problems,
            },
            indent=2,
        )
    )
    if problems:
        print("DEPENDENCY TRUST — FAIL")
        for p in problems:
            print("  " + p)
        return 1
    print("DEPENDENCY TRUST — OK (LEVEL_1: pinned, no hashes; "
          "CI consumes requirements-ci.lock)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
