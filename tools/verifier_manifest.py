#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate / verify verifier_manifest.lock.

The manifest is NOT the only verifier of itself: the independent
stdlib-only checker (tools/check_verifier_manifest_static.py) is the
root, this generator is convenience + the change-gate. Critical
verifier files are pinned by sha256; any change to a verifier requires
a manifest update AND a docs/reports/VERIFIER_CHANGE_REPORT.md.

    python tools/verifier_manifest.py --write    # regenerate the lock
    python tools/verifier_manifest.py            # verify + change-gate
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_LOCK = _ROOT / "verifier_manifest.lock"
_CHANGE_REPORT = _ROOT / "docs" / "reports" / "VERIFIER_CHANGE_REPORT.md"

# Files whose mutation could silently weaken protection. Only those
# that exist are pinned (a missing one is a hard error, not skipped).
CRITICAL = [
    "scripts/claims_lint.py",
    "scripts/provenance_attest.py",
    "scripts/reviewer_attack.sh",
    "scripts/deep_mechanism_audit.sh",
    "src/ctios/readiness_score.py",
    "src/ctios/external_validation.py",
    "src/ctios/artifact_assertions.py",
    "src/ctios/code_quality_audit.py",
    "src/ctios/mechanism_inventory.py",
    "src/ctios/test_value_audit.py",
    "src/ctios/deep_adversarial_probes.py",
    "tools/check_verifier_manifest_static.py",
    ".github/workflows/ci.yml",
]


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def current_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in CRITICAL:
        f = _ROOT / rel
        if not f.exists():
            raise SystemExit(f"FAIL: critical verifier missing: {rel}")
        out[rel] = _sha256(f)
    return out


def locked_hashes() -> dict[str, str]:
    if not _LOCK.exists():
        return {}
    out: dict[str, str] = {}
    for line in _LOCK.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        h, rel = line.split(None, 1)
        out[rel] = h
    return out


def write() -> None:
    cur = current_hashes()
    body = (
        "# verifier manifest — sha256␠␠path (sha256sum-compatible)\n"
        "# Pins files whose silent mutation would weaken protection.\n"
        "# Change requires docs/reports/VERIFIER_CHANGE_REPORT.md.\n"
    )
    for rel in CRITICAL:
        body += f"{cur[rel]}  {rel}\n"
    _LOCK.write_text(body)


def verify() -> list[str]:
    cur = current_hashes()
    lock = locked_hashes()
    problems: list[str] = []
    if not lock:
        return ["verifier_manifest.lock missing — run --write"]
    changed = [r for r in CRITICAL if lock.get(r) != cur[r]]
    missing_in_lock = [r for r in CRITICAL if r not in lock]
    problems += [f"verifier changed but lock not updated: {r}" for r in changed]
    problems += [f"verifier not pinned in lock: {r}" for r in missing_in_lock]
    # change-gate: if anything changed, a rationale report must exist
    # and reference the new hash.
    if changed:
        if not _CHANGE_REPORT.exists():
            problems.append(
                "verifier(s) changed without docs/reports/"
                "VERIFIER_CHANGE_REPORT.md"
            )
        else:
            rep = _CHANGE_REPORT.read_text()
            for r in changed:
                if cur[r][:16] not in rep:
                    problems.append(
                        f"VERIFIER_CHANGE_REPORT missing new hash for {r}"
                    )
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    if a.write:
        write()
        print(f"verifier_manifest.lock written ({len(CRITICAL)} files)")
        return 0
    problems = verify()
    if problems:
        print("VERIFIER MANIFEST (gate) — FAIL\n" + "\n".join(problems))
        return 1
    print(f"VERIFIER MANIFEST (gate) — OK ({len(CRITICAL)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
