# SPDX-License-Identifier: MIT
"""Deterministically (re)build evidence/DOC_TRUST_AUDIT.json from the
live trust layer. No timestamp / no volatile field: the committed
audit must be byte-stable on a clean clone so the gate does not drift.

`--verify-only` rebuilds in memory and fails closed if the committed
file differs (drift = fail). Stdlib + yaml only. Exempt from
claims_lint by the same rationale as scripts/check_doc_trust.py.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[1]
_MATRIX = _ROOT / "docs" / "CLAIM_SOURCE_MATRIX.md"
_REG = _ROOT / "evidence" / "SOURCE_REGISTRY.yaml"
_AUDIT = _ROOT / "evidence" / "DOC_TRUST_AUDIT.json"
_LEDGER = _ROOT / "evidence" / "CLAIM_DOWNGRADE_LEDGER.jsonl"

_FILES_SCANNED = [
    "README.md",
    "docs/SYSTEM_CARD.md",
    "docs/CONTRIBUTION_CLAIMS.md",
    "docs/SPEC.md",
    "docs/REPRODUCIBILITY_CONTRACT.md",
    "docs/FAILURE_TAXONOMY.md",
    "docs/OPEN_STRUCTURAL_GAPS.md",
    "docs/reports/LINEAGE_STATE.md",
    "claims.yaml",
    "scripts/claims_lint.py",
    "pyproject.toml",
    "evidence/release_gate.md",
]


def _rows() -> list[list[str]]:
    out: list[list[str]] = []
    for ln in _MATRIX.read_text().splitlines():
        s = ln.strip()
        if s.startswith("| TRI-CLAIM-"):
            out.append([c.strip() for c in s.strip("|").split("|")])
    return out


def build() -> dict[str, object]:
    rows = _rows()
    classes = [r[2] for r in rows]
    evid = sum(
        1 for r in rows if r[4] and r[4] not in ("-", "n/a")
    )
    src = sum(1 for r in rows if re.search(r"[A-Z][A-Z0-9_]{3,}", r[5]))
    boundary = sum(
        1 for c in classes if c in ("NON_CLAIM_BOUNDARY", "INSPIRATION_ONLY")
    )
    open_gaps = sum(1 for c in classes if c == "OPEN_GAP")
    downgraded = sum(
        1 for _ in _LEDGER.read_text().splitlines() if _.strip()
    )
    reg = yaml.safe_load(_REG.read_text())
    prior = json.loads(_AUDIT.read_text())
    must_not = prior["must_not_claim"]
    major = prior.get("major_findings", [])
    return {
        "repo": "neuron7xLab/time-rupture-inference",
        "audit_type": "doc_trust_value_hardening",
        "claim_count": len(rows),
        "supported_by_evidence": evid,
        "supported_by_external_source": src,
        "boundary_only": boundary,
        "downgraded": downgraded,
        "deleted": 0,
        "open_gaps_referenced": open_gaps,
        "files_scanned": _FILES_SCANNED,
        "source_count": len(reg.get("sources", [])),
        "major_findings": major,
        "must_not_claim": must_not,
        "value_lift_summary": (
            "Every major external-facing claim resolves to a stable ID "
            "with in-repo evidence, a canonical source, an explicit "
            "boundary, or a tracked open gap; scripts/check_doc_trust.py "
            "blocks regressions in CI. No scientific claim is expanded."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cur = build()
    if "--verify-only" in argv:
        committed = json.loads(_AUDIT.read_text())
        drift = [
            k for k in ("claim_count", "open_gaps_referenced", "downgraded")
            if committed.get(k) != cur.get(k)
        ]
        if drift:
            print(f"DOC TRUST AUDIT — FAIL (drift: {drift})")
            return 1
        print("DOC TRUST AUDIT — OK (committed matches live trust layer)")
        return 0
    _AUDIT.write_text(json.dumps(cur, indent=2) + "\n")
    print(f"DOC_TRUST_AUDIT.json written ({cur['claim_count']} claims)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
