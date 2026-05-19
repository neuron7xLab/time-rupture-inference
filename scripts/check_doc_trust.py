# SPDX-License-Identifier: MIT
"""Documentation trust gate. Fails closed if the doc trust layer is
incomplete or self-inconsistent. Stdlib + yaml only (yaml is already a
runtime dep and is used by scripts/claims_lint.py).

This script intentionally holds the forbidden-phrase lexicon as data,
exactly like scripts/claims_lint.py; it is therefore on the
claims.yaml `exempt` list by the same rationale (it is the enforcement
mechanism, not outward positioning).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[1]
_MATRIX = _ROOT / "docs" / "CLAIM_SOURCE_MATRIX.md"
_REG_YAML = _ROOT / "evidence" / "SOURCE_REGISTRY.yaml"
_AUDIT = _ROOT / "evidence" / "DOC_TRUST_AUDIT.json"
_README = _ROOT / "README.md"
_NOTES = _ROOT / "docs" / "MANUAL_AUTHOR_NOTES.md"

_REQUIRED = [
    "evidence/SOURCE_REGISTRY.yaml",
    "docs/SOURCE_REGISTRY.md",
    "docs/CLAIM_SOURCE_MATRIX.md",
    "docs/PRIOR_ART_BOUNDARY_MAP.md",
    "docs/TRUST_LAYER.md",
    "docs/REVIEW_PATH.md",
    "docs/VALUE_POSITIONING.md",
    "docs/MANUAL_AUTHOR_NOTES.md",
    "docs/DOC_STYLE_CONTRACT.md",
    "evidence/DOC_TRUST_AUDIT.json",
    "evidence/CLAIM_DOWNGRADE_LEDGER.jsonl",
]

# External-facing positive assertions that must never appear outside an
# explicit disclaimer block. Stored as data (this file is exempt).
_FORBIDDEN = [
    "proves intelligence",
    "models consciousness",
    "brain-equivalent",
    "brain-like intelligence",
    "agi",
    "biologically faithful",
    "real-world validity proven",
    "production ready",
    "product ready",
    "productizable",
    "validates neuroscience",
    "proves cognition",
]

_DISC_OPEN = "<!-- claims:disclaimer -->"
_DISC_CLOSE = "<!-- claims:end -->"

# Docs whose prose is outward positioning (scanned for _FORBIDDEN).
_SCANNED_DOCS = [
    "docs/TRUST_LAYER.md",
    "docs/REVIEW_PATH.md",
    "docs/VALUE_POSITIONING.md",
    "docs/SOURCE_REGISTRY.md",
    "docs/PRIOR_ART_BOUNDARY_MAP.md",
    "docs/CLAIM_SOURCE_MATRIX.md",
    "docs/MANUAL_AUTHOR_NOTES.md",
    "docs/DOC_STYLE_CONTRACT.md",
]


class Row:
    __slots__ = ("cid", "text", "cls", "loc", "evidence", "sources")

    def __init__(
        self, cid: str, text: str, cls: str, loc: str,
        evidence: str, sources: str,
    ) -> None:
        self.cid = cid
        self.text = text
        self.cls = cls
        self.loc = loc
        self.evidence = evidence
        self.sources = sources


def _matrix_rows() -> list[Row]:
    rows: list[Row] = []
    for ln in _MATRIX.read_text().splitlines():
        s = ln.strip()
        if not s.startswith("| TRI-CLAIM-"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        # cid | text | class | location | evidence | source | fals | status
        if len(cells) < 6:
            continue
        rows.append(
            Row(cells[0], cells[1], cells[2], cells[3], cells[4], cells[5])
        )
    return rows


def _registry_ids() -> set[str]:
    doc = yaml.safe_load(_REG_YAML.read_text())
    return {s["id"] for s in doc.get("sources", [])}


def _registry_claim_ids() -> set[str]:
    doc = yaml.safe_load(_REG_YAML.read_text())
    out: set[str] = set()
    for s in doc.get("sources", []):
        out.update(s.get("supports_claim_ids", []) or [])
    return out


def _word_count(p: Path) -> int:
    return len(re.findall(r"\S+", p.read_text()))


# A forbidden phrase is an OVERCLAIM only when asserted. If the line
# also carries a negation / boundary / definitional token (or sits in a
# disclaimer block) it is enumerating the boundary, not claiming it —
# same rationale as claims.yaml qualifier_tokens.
_BOUNDARY = (
    " not ", "never", "no ", "without", "blocked", "block ", "blocks",
    "forbid", "refuse", "absent", "cannot", "does not", "is not",
    "claims:", "must not", "non-claim", "not claim", "downgrad",
)


def _forbidden_hits(text: str) -> list[str]:
    """Forbidden phrases asserted outside a disclaimer/boundary line."""
    hits: list[str] = []
    in_disc = False
    for i, raw in enumerate(text.splitlines(), 1):
        low = raw.lower()
        if _DISC_OPEN in raw:
            in_disc = True
        if _DISC_CLOSE in raw:
            in_disc = False
            continue
        if in_disc or any(b in low for b in _BOUNDARY):
            continue
        for phrase in _FORBIDDEN:
            if phrase in low:
                hits.append(f"L{i}: {phrase!r}")
    return hits


def audit() -> list[str]:
    problems: list[str] = []

    for rel in _REQUIRED:
        if not (_ROOT / rel).exists():
            problems.append(f"required trust-layer file missing: {rel}")
    if problems:
        return problems

    reg_ids = _registry_ids()
    reg_claim_ids = _registry_claim_ids()
    rows = _matrix_rows()
    if not rows:
        return ["CLAIM_SOURCE_MATRIX has no parseable claim rows"]

    for r in rows:
        # check 3: every referenced source_id exists in the registry
        for sid in re.findall(r"[A-Z][A-Z0-9_]+", r.sources):
            if sid not in reg_ids:
                problems.append(
                    f"{r.cid}: source_id {sid!r} absent from "
                    f"SOURCE_REGISTRY.yaml"
                )
        # check 2: claim is registry-mapped OR has in-repo evidence
        has_evidence = bool(r.evidence) and r.evidence not in ("-", "n/a")
        if r.cid not in reg_claim_ids and not has_evidence:
            problems.append(
                f"{r.cid}: neither registry-mapped nor IN_REPO_EVIDENCE"
            )
        # check 4: inspiration carries the biological-fidelity boundary
        if r.cls == "INSPIRATION_ONLY" and (
            "does not imply biological fidelity" not in r.text.lower()
        ):
            problems.append(
                f"{r.cid}: INSPIRATION_ONLY without "
                "'does not imply biological fidelity'"
            )
        # check 5: supply-chain carries its ceiling
        if r.cls == "SUPPLY_CHAIN_TRUST":
            t = r.text.lower()
            if "not hermetic" not in t or "not slsa l3" not in t:
                problems.append(
                    f"{r.cid}: SUPPLY_CHAIN_TRUST without "
                    "not-hermetic / not-SLSA-L3 boundary"
                )
        # check 6: open gaps link the register
        if r.cls == "OPEN_GAP" and "OPEN_STRUCTURAL_GAPS" not in (
            r.loc + r.evidence + r.text
        ):
            problems.append(
                f"{r.cid}: OPEN_GAP not linked to OPEN_STRUCTURAL_GAPS.md"
            )

    # check 7: forbidden phrases outside disclaimer in scanned docs
    for rel in _SCANNED_DOCS:
        for h in _forbidden_hits((_ROOT / rel).read_text()):
            problems.append(f"{rel}: forbidden external phrase {h}")

    # check 8: README has the Reviewer map, not a bibliography
    rd = _README.read_text()
    if "## Reviewer map" not in rd:
        problems.append("README.md missing '## Reviewer map' section")
    if re.search(r"(?im)^#+\s*(bibliography|references)\b", rd):
        problems.append("README.md must not carry a bibliography section")

    # check 9: author notes under 900 words
    wc = _word_count(_NOTES)
    if wc >= 900:
        problems.append(f"MANUAL_AUTHOR_NOTES.md too long: {wc} words (>=900)")

    # check 10: audit JSON valid with nonzero claim_count
    try:
        a = json.loads(_AUDIT.read_text())
    except json.JSONDecodeError as e:
        problems.append(f"DOC_TRUST_AUDIT.json unparseable: {e}")
    else:
        if not isinstance(a.get("claim_count"), int) or a["claim_count"] <= 0:
            problems.append("DOC_TRUST_AUDIT.json claim_count must be > 0")

    return problems


def main() -> int:
    problems = audit()
    if problems:
        print("DOC TRUST — FAIL")
        for p in problems:
            print("  " + p)
        return 1
    print(
        f"DOC TRUST — OK ({len(_matrix_rows())} claims mapped; "
        f"{len(_registry_ids())} sources; forbidden-phrase scan clean)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
