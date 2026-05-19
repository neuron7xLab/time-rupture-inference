# SPDX-License-Identifier: MIT
"""Release trust audit (PR N). Stdlib-only. Fails closed if the
release workflow is missing, lacks build-provenance attestation, lacks
the required permissions, builds/attests BEFORE the test+runner gate,
skips SBOM generation, uploads assets before attestation, or if the
SLSA declaration overclaims a level above what the mechanism proves.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_REL = _ROOT / ".github" / "workflows" / "release.yml"
_SLSA = _ROOT / "docs" / "SLSA_LEVEL_DECLARATION.md"


def _idx(lines: list[str], pat: str) -> int:
    for i, ln in enumerate(lines):
        if re.search(pat, ln):
            return i
    return -1


def audit() -> list[str]:
    problems: list[str] = []
    if not _REL.exists():
        return ["release workflow .github/workflows/release.yml missing"]
    text = _REL.read_text()
    lines = text.splitlines()

    for perm in (
        r"contents:\s*write",
        r"id-token:\s*write",
        r"attestations:\s*write",
    ):
        if not re.search(perm, text):
            problems.append(f"release.yml missing permission: {perm}")

    i_tests = _idx(lines, r"pytest tests")
    i_runner = _idx(lines, r"ctios\.runner --mode full")
    i_build = _idx(lines, r"python -m build")
    i_sbom = _idx(lines, r"generate_sbom\.py")
    i_attest = _idx(lines, r"attest-build-provenance@[0-9a-f]{40}")
    i_upload = _idx(lines, r"gh release create")

    if i_attest < 0:
        problems.append("no build-provenance attestation step")
    if i_sbom < 0:
        problems.append("no SBOM generation step")
    if i_tests < 0 or i_runner < 0:
        problems.append("gate (pytest + ctios.runner) not both present")
    if i_build < 0:
        problems.append("no build step")

    # MANDATORY ORDER: tests+runner BEFORE build & attest; upload LAST.
    if i_tests >= 0 and i_build >= 0 and i_tests > i_build:
        problems.append("tests run AFTER build (gate must precede build)")
    if i_runner >= 0 and i_build >= 0 and i_runner > i_build:
        problems.append("runner runs AFTER build (gate must precede build)")
    if i_tests >= 0 and i_attest >= 0 and i_tests > i_attest:
        problems.append("attestation BEFORE the test gate")
    if i_attest >= 0 and i_upload >= 0 and i_upload < i_attest:
        problems.append("assets uploaded BEFORE attestation")
    if i_build >= 0 and i_attest >= 0 and i_attest < i_build:
        problems.append("attestation BEFORE build")

    # SLSA honesty: default L2 with GitHub artifact attestation.
    if _SLSA.exists():
        low = _SLSA.read_text().lower()
        if re.search(r"slsa[\s_-]*(build[\s_-]*)?l?3|level\s*3", low):
            if "not l3" not in low and "not level 3" not in low:
                problems.append(
                    "SLSA_LEVEL_DECLARATION overclaims L3 without negation"
                )
        if "build l2" not in low and "slsa build l2" not in low:
            problems.append(
                "SLSA_LEVEL_DECLARATION does not state achieved Build L2"
            )
    else:
        problems.append("docs/SLSA_LEVEL_DECLARATION.md missing")
    return problems


def main() -> int:
    problems = audit()
    out = _ROOT / "evidence" / "RELEASE_TRUST_AUDIT.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "status": "PASS" if not problems else "FAIL",
                "slsa_level_claimed": "L2",
                "problems": problems,
            },
            indent=2,
        )
    )
    if problems:
        print("RELEASE TRUST — FAIL")
        for p in problems:
            print("  " + p)
        return 1
    print("RELEASE TRUST — OK (gate-before-attest, SBOM, SLSA Build L2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
