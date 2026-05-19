# SPDX-License-Identifier: MIT
"""ctios.test_value_audit — find weak tests, executably.

Classifies each tests/test_*.py by what it actually asserts. A file
that only asserts "it ran" (truthy / status-in-set with no kill case,
no ==, no artifact, no raises) is WEAK_OR_DECORATIVE and must not be
counted as proof of correctness.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_TESTS = _ROOT / "tests"

KILL = "KILL_TEST"
CONTRACT = "CONTRACT_TEST"
ARTIFACT = "ARTIFACT_TEST"
BOUNDARY = "CLAIM_BOUNDARY_TEST"
ISOLATION = "VERDICT_ISOLATION"
WEAK = "WEAK_OR_DECORATIVE"


def classify(text: str) -> str:
    if "pytest.raises" in text or re.search(r"assert .*is (False|None)\b", text):
        return KILL
    if re.search(r"claims_lint|_violations|surface|forbidden", text):
        return BOUNDARY
    if re.search(r"\.json|read_text\(\)|exists\(\)|REVIEWER_ATTACK|"
                 r"artifact|sha256|replay_hash", text):
        return ARTIFACT
    if re.search(r"verdict\.status in \(|battery\[", text):
        return ISOLATION
    if re.search(r"assert .+ == .+|assert .+ != .+|<=|>=|abs\(", text):
        return CONTRACT
    return WEAK


def audit() -> dict[str, str]:
    return {
        f.name: classify(f.read_text())
        for f in sorted(_TESTS.glob("test_*.py"))
    }


def weak_files() -> list[str]:
    return [n for n, c in audit().items() if c == WEAK]


def write() -> Path:
    a = audit()
    out = _ROOT / "docs" / "TEST_VALUE_AUDIT.md"
    lines = [
        "# Test Value Audit (generated)",
        "",
        "`python -m ctios.test_value_audit`. WEAK_OR_DECORATIVE tests "
        "must not be cited as proof of correctness.",
        "",
        "| test file | class |",
        "|---|---|",
    ]
    lines += [f"| {n} | {c} |" for n, c in a.items()]
    weak = [n for n, c in a.items() if c == WEAK]
    lines += ["", f"weak_or_decorative: {weak or '(none)'}"]
    out.write_text("\n".join(lines) + "\n")
    (_ROOT / "evidence" / "TEST_VALUE_AUDIT.json").write_text(
        json.dumps({"classes": a, "weak": weak}, indent=2)
    )
    return out


def main() -> int:
    weak = weak_files()
    write()
    print(f"test-value audit :: {len(audit())} files, weak={len(weak)}")
    return 0 if not weak else 1


if __name__ == "__main__":
    raise SystemExit(main())
