# SPDX-License-Identifier: MIT
"""Documentation trust gate — a real parser, fail-closed.

Parses docs/CLAIM_SOURCE_MATRIX.md row by row and binds every claim to
the registry, the evidence layer, and its class contract. Stdlib +
yaml only (yaml is already a runtime dep, used by claims_lint.py).

Fail conditions:
  * a required trust-layer file is missing;
  * BOTH manual-note docs present (duplication) or the canonical one
    absent;
  * a registry source lacks any of the required schema keys;
  * a matrix source_id is absent from SOURCE_REGISTRY.yaml;
  * a registry source_id maps to a claim_id absent from the matrix;
  * a matrix row has an empty evidence_path;
  * EMPIRICAL_RESULT / REPRODUCIBILITY_CONTRACT without a runnable /
    artifact evidence path;
  * ENGINEERING_MECHANISM without a script/test/CI path;
  * GOVERNANCE_MECHANISM without a gate/linter/check path;
  * INSPIRATION_ONLY without "does not imply biological fidelity";
  * OPEN_GAP without docs/OPEN_STRUCTURAL_GAPS.md;
  * SUPPLY_CHAIN_TRUST without "not hermetic" + "not slsa l3";
  * fewer than 20 stable claim rows;
  * a registry source absent from docs/REFERENCES.md (drift);
  * a forbidden phrase asserted outside a disclaimer/boundary line;
  * README missing the Reviewer map or carrying a bibliography;
  * the handcrafted author note >= 900 words;
  * DOC_TRUST_AUDIT.json invalid or claim_count <= 0.

This file holds the forbidden-phrase lexicon as data, exactly like
scripts/claims_lint.py; it is claims.yaml-exempt by the same rationale.
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
_REFERENCES = _ROOT / "docs" / "REFERENCES.md"
_AUDIT = _ROOT / "evidence" / "DOC_TRUST_AUDIT.json"
_README = _ROOT / "README.md"
_NOTES = _ROOT / "docs" / "MANUAL_REVIEW_NOTES.md"
_LEGACY_NOTES = _ROOT / "docs" / "MANUAL_AUTHOR_NOTES.md"

_REQUIRED = [
    "evidence/SOURCE_REGISTRY.yaml",
    "docs/SOURCE_REGISTRY.md",
    "docs/CLAIM_SOURCE_MATRIX.md",
    "docs/PRIOR_ART_BOUNDARY_MAP.md",
    "docs/TRUST_LAYER.md",
    "docs/REVIEW_PATH.md",
    "docs/VALUE_POSITIONING.md",
    "docs/MANUAL_REVIEW_NOTES.md",
    "docs/DOC_STYLE_CONTRACT.md",
    "docs/REFERENCES.md",
    "evidence/DOC_TRUST_AUDIT.json",
    "evidence/CLAIM_DOWNGRADE_LEDGER.jsonl",
]

_REGISTRY_KEYS = (
    "id", "tier", "canonical_citation", "url", "domain",
    "supports_claim_ids", "supports_repo_files", "allowed_use",
    "forbidden_use", "boundary", "status",
)

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

_SCANNED_DOCS = [
    "docs/TRUST_LAYER.md",
    "docs/REVIEW_PATH.md",
    "docs/VALUE_POSITIONING.md",
    "docs/SOURCE_REGISTRY.md",
    "docs/PRIOR_ART_BOUNDARY_MAP.md",
    "docs/CLAIM_SOURCE_MATRIX.md",
    "docs/MANUAL_REVIEW_NOTES.md",
    "docs/DOC_STYLE_CONTRACT.md",
    "docs/REFERENCES.md",
]

# A forbidden phrase is an OVERCLAIM only when asserted. A negation /
# boundary / definitional token (or a disclaimer block) means it is
# enumerating the boundary — same rationale as claims.yaml qualifiers.
_BOUNDARY = (
    " not ", "never", "no ", "without", "blocked", "block ", "blocks",
    "forbid", "refuse", "absent", "cannot", "does not", "is not",
    "claims:", "must not", "non-claim", "not claim", "downgrad",
)

# Evidence-path tokens by claim class.
_CODE_TOK = (".py", "tests/", "ctios.", "scripts/", "ci", ".github",
             "pytest", "python -m")
_GATE_TOK = ("lint", "gate", "check", "claims", "test", "ci",
             "scripts/", "human_gate", "readiness", "provenance",
             "evidence/", "tag", "ledger", "falsify")
_RUN_TOK = ("python -m", "pytest", "bash ", "scripts/", "evidence/",
            "runner", ".json", "release_gate")


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
        if len(cells) < 8:
            continue
        rows.append(
            Row(cells[0], cells[1], cells[2], cells[3], cells[4],
                cells[5])
        )
    return rows


def _registry() -> list[dict[str, object]]:
    doc = yaml.safe_load(_REG_YAML.read_text())
    srcs = doc.get("sources", []) if isinstance(doc, dict) else []
    return [s for s in srcs if isinstance(s, dict)]


def _word_count(p: Path) -> int:
    return len(re.findall(r"\S+", p.read_text())) if p.exists() else 0


def _forbidden_hits(text: str) -> list[str]:
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
    # dedupe: exactly one handcrafted author note
    if _LEGACY_NOTES.exists():
        problems.append(
            "duplicate manual-note doc: docs/MANUAL_AUTHOR_NOTES.md "
            "must be removed (canonical is docs/MANUAL_REVIEW_NOTES.md)"
        )
    if problems:
        return problems

    srcs = _registry()
    reg_ids: set[str] = set()
    reg_claim_ids: set[str] = set()
    for s in srcs:
        missing = [k for k in _REGISTRY_KEYS if k not in s]
        if missing:
            problems.append(
                f"registry {s.get('id', '?')!r} missing keys: {missing}"
            )
        sid = s.get("id")
        if isinstance(sid, str):
            reg_ids.add(sid)
        cids = s.get("supports_claim_ids") or []
        if isinstance(cids, list):
            reg_claim_ids.update(str(c) for c in cids)

    rows = _matrix_rows()
    if len(rows) < 20:
        problems.append(
            f"matrix too thin: {len(rows)} claim rows (>= 20 required)"
        )
    matrix_ids = {r.cid for r in rows}

    # registry<->matrix claim_id consistency (both directions matter)
    for cid in sorted(reg_claim_ids):
        if cid not in matrix_ids:
            problems.append(
                f"registry maps {cid} but it is absent from the matrix"
            )

    refs = _REFERENCES.read_text()
    for sid in sorted(reg_ids):
        if sid not in refs:
            problems.append(
                f"registry source {sid!r} missing from docs/REFERENCES.md"
            )

    for r in rows:
        srcs_in_row = re.findall(r"[A-Z][A-Z0-9_]{3,}", r.sources)
        for sid in srcs_in_row:
            if sid not in reg_ids:
                problems.append(
                    f"{r.cid}: source_id {sid!r} absent from registry"
                )
        if not srcs_in_row:
            problems.append(f"{r.cid}: no source_id")
        ev = r.evidence.lower()
        if not r.evidence or r.evidence in ("-", "n/a"):
            problems.append(f"{r.cid}: empty evidence_path")
            continue
        if r.cls in ("EMPIRICAL_RESULT", "REPRODUCIBILITY_CONTRACT") \
                and not any(t in ev for t in _RUN_TOK):
            problems.append(
                f"{r.cid}: {r.cls} without a runnable/artifact path"
            )
        if r.cls == "ENGINEERING_MECHANISM" \
                and not any(t in ev for t in _CODE_TOK):
            problems.append(
                f"{r.cid}: ENGINEERING_MECHANISM without script/test/CI"
            )
        if r.cls == "GOVERNANCE_MECHANISM" \
                and not any(t in ev for t in _GATE_TOK):
            problems.append(
                f"{r.cid}: GOVERNANCE_MECHANISM without gate/linter/check"
            )
        if r.cls == "INSPIRATION_ONLY" and (
            "does not imply biological fidelity" not in r.text.lower()
        ):
            problems.append(
                f"{r.cid}: INSPIRATION_ONLY without "
                "'does not imply biological fidelity'"
            )
        if r.cls == "SUPPLY_CHAIN_TRUST":
            t = r.text.lower()
            if "not hermetic" not in t or "not slsa l3" not in t:
                problems.append(
                    f"{r.cid}: SUPPLY_CHAIN_TRUST without "
                    "not-hermetic / not-SLSA-L3 boundary"
                )
        if r.cls == "OPEN_GAP" and "OPEN_STRUCTURAL_GAPS" not in (
            r.loc + r.evidence + r.text
        ):
            problems.append(
                f"{r.cid}: OPEN_GAP not linked to OPEN_STRUCTURAL_GAPS.md"
            )

    for rel in _SCANNED_DOCS:
        p = _ROOT / rel
        if p.exists():
            for h in _forbidden_hits(p.read_text()):
                problems.append(f"{rel}: forbidden external phrase {h}")

    rd = _README.read_text()
    if "## Reviewer map" not in rd:
        problems.append("README.md missing '## Reviewer map' section")
    if re.search(r"(?im)^#+\s*(bibliography|references)\b", rd):
        problems.append("README.md must not carry a bibliography section")

    wc = _word_count(_NOTES)
    if wc >= 900:
        problems.append(
            f"MANUAL_REVIEW_NOTES.md too long: {wc} words (>=900)"
        )

    try:
        a = json.loads(_AUDIT.read_text())
    except json.JSONDecodeError as e:
        problems.append(f"DOC_TRUST_AUDIT.json unparseable: {e}")
    else:
        if not isinstance(a.get("claim_count"), int) \
                or a["claim_count"] <= 0:
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
        f"DOC TRUST — OK ({len(_matrix_rows())} claims parsed; "
        f"{len(_registry())} sources; class contracts + references "
        f"consistent; forbidden-phrase scan clean)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
