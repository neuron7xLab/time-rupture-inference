# SPDX-License-Identifier: MIT
"""Complementary doc-claim-source consistency gate (stdlib-only).

Distinct from scripts/check_doc_trust.py (which parses the matrix and
binds claims to the registry). This one enforces a narrower invariant:
if a major external-facing document name-drops a prior-art / standards
TERM, that term must be accounted for in docs/REFERENCES.md — a term
cannot float in positioning prose without a mapped source. It also
fails on forbidden phrases asserted outside a disclaimer / forbidden-
wording context. Holds the lexicon as data -> claims.yaml-exempt, same
rationale as scripts/claims_lint.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_REFERENCES = _ROOT / "docs" / "REFERENCES.md"

_REQUIRED = [
    "docs/REFERENCES.md",
    "docs/PRIOR_ART_BOUNDARY_MAP.md",
    "docs/CLAIM_SOURCE_MATRIX.md",
]
_DOCS = [
    "README.md",
    "docs/SYSTEM_CARD.md",
    "docs/CONTRIBUTION_CLAIMS.md",
    "docs/REPRODUCIBILITY_CONTRACT.md",
]
# A flagged term in a positioning doc must be accounted for in
# REFERENCES.md (so it is mapped to a real source, not floating).
_TERMS = [
    "predictive coding",
    "page-hinkley",
    "falsification",
    "slsa",
    "spdx",
    "model card",
    "nist",
]
_FORBIDDEN = [
    "proves intelligence",
    "models consciousness",
    "brain-equivalent",
    "agi",
    "biologically faithful",
    "real-world validity proven",
    "production ready",
    "productizable",
]
_DISC_OPEN = "<!-- claims:disclaimer -->"
_DISC_CLOSE = "<!-- claims:end -->"
_BOUNDARY = (
    " not ", "never", "no ", "without", "blocked", "blocks", "forbid",
    "refuse", "cannot", "does not", "is not", "must not", "non-claim",
)


def audit() -> list[str]:
    errs: list[str] = []
    for rel in _REQUIRED:
        if not (_ROOT / rel).exists():
            errs.append(f"missing required doc: {rel}")
    if errs:
        return errs

    ref_low = _REFERENCES.read_text().lower()
    for rel in _DOCS:
        p = _ROOT / rel
        if not p.exists():
            continue
        text = p.read_text()
        low = text.lower()
        for term in _TERMS:
            if term in low and term not in ref_low:
                errs.append(
                    f"term {term!r} in {rel} but absent from "
                    "docs/REFERENCES.md (unmapped to a source)"
                )
        in_disc = False
        for i, raw in enumerate(text.splitlines(), 1):
            lo = raw.lower()
            if _DISC_OPEN in raw:
                in_disc = True
            if _DISC_CLOSE in raw:
                in_disc = False
                continue
            if in_disc or any(b in lo for b in _BOUNDARY):
                continue
            for bad in _FORBIDDEN:
                if re.search(rf"\b{re.escape(bad)}\b", lo):
                    errs.append(
                        f"forbidden phrase {bad!r} in {rel}:{i}"
                    )
    return errs


def main() -> int:
    errs = audit()
    if errs:
        print("DOC CLAIM SOURCE — FAIL")
        for e in errs:
            print("  " + e)
        return 1
    print(
        f"DOC CLAIM SOURCE — OK ({len(_DOCS)} docs; flagged terms "
        f"mapped to docs/REFERENCES.md; forbidden-phrase scan clean)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
