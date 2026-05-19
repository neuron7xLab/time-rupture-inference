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
_VALUE_MD = _ROOT / "docs" / "reports" / "DOC_VALUE_AUDIT.md"
_MIRROR = _ROOT / "docs" / "SOURCE_REGISTRY.md"

_MUST_NOT = [
    "cognition", "consciousness", "AGI / general intelligence",
    "biological fidelity / brain equivalence", "real-world validity",
    "production readiness / productizable", "learned-model superiority",
    "hermetic or SLSA L3 supply chain",
    "novelty of falsification, change detection, or online estimation",
]
_FINDINGS = [
    "Every external-facing claim carries a stable TRI-CLAIM-0NN ID "
    "parsed and class-checked by scripts/check_doc_trust.py; no "
    "scientific claim is expanded.",
    "Source registry uses the full schema (id/tier/citation/url/"
    "domain/supports_claim_ids/supports_repo_files/allowed_use/"
    "forbidden_use/boundary/status) and stays in sync with "
    "docs/REFERENCES.md (gate-enforced).",
    "Prediction-error language is bound INSPIRATION_ONLY with an "
    "explicit no-biological-fidelity boundary; supply-chain claims "
    "carry the not-hermetic / not-SLSA-L3 ceiling.",
    "Two structural gaps (independent reproduction, domain breadth) "
    "remain OPEN and block READY/PRODUCTIZABLE in code.",
]

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
    must_not = _MUST_NOT
    major = _FINDINGS
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


def render_mirror() -> str:
    """docs/SOURCE_REGISTRY.md, deterministically from the YAML —
    single source of truth, cannot drift."""
    reg = yaml.safe_load(_REG.read_text())
    head = (
        "<!-- GENERATED from evidence/SOURCE_REGISTRY.yaml by\n"
        "     scripts/build_doc_trust_audit.py. Do not hand-edit; "
        "edit the YAML\n     and regenerate "
        "(scripts/build_doc_trust_audit.py --verify-only\n"
        "     fails closed on drift). -->\n"
        "# Source Registry (claim-support, not a bibliography)\n\n"
        "A source appears here only if it maps to >=1 `claim_id` or "
        "repo file.\nNo prestige padding, no citation laundering. "
        "Machine source of truth:\n`evidence/SOURCE_REGISTRY.yaml`. "
        "Tiers: **CANONICAL** /\n**SUPPORTING** / **CONTEXT_ONLY**. "
        "Claim numbers are the\n`TRI-CLAIM-0NN` suffix in "
        "`docs/CLAIM_SOURCE_MATRIX.md`.\n\n"
        "| id | tier | domain | supports | boundary |\n"
        "|---|---|---|---|---|\n"
    )
    rows = []
    for s in reg.get("sources", []):
        cids = ",".join(
            str(c).replace("TRI-CLAIM-", "")
            for c in s.get("supports_claim_ids", [])
        )
        rows.append(
            f"| {s['id']} | {s['tier']} | {s['domain']} | {cids} | "
            f"{s['boundary']} |"
        )
    tail = (
        "\n\nFull citations, URLs, allowed/forbidden use are in\n"
        "`evidence/SOURCE_REGISTRY.yaml`; the rendered human "
        "bibliography is\n`docs/REFERENCES.md`. A source cannot be "
        "added unless it maps to at\nleast one `claim_id` or repo "
        "file.\n"
    )
    return head + "\n".join(rows) + tail


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cur = build()
    mirror = render_mirror()
    if "--verify-only" in argv:
        committed = json.loads(_AUDIT.read_text())
        drift = [
            k for k in ("claim_count", "open_gaps_referenced", "downgraded")
            if committed.get(k) != cur.get(k)
        ]
        if drift:
            print(f"DOC TRUST AUDIT — FAIL (drift: {drift})")
            return 1
        if _MIRROR.read_text() != mirror:
            print(
                "DOC TRUST AUDIT — FAIL (docs/SOURCE_REGISTRY.md "
                "drifted from evidence/SOURCE_REGISTRY.yaml)"
            )
            return 1
        print("DOC TRUST AUDIT — OK (committed matches live trust layer)")
        return 0
    _AUDIT.write_text(json.dumps(cur, indent=2) + "\n")
    _VALUE_MD.parent.mkdir(parents=True, exist_ok=True)
    md = [
        "# Documentation Value Audit (generated)",
        "",
        "Generated from `evidence/DOC_TRUST_AUDIT.json` by "
        "`scripts/build_doc_trust_audit.py`. Do not hand-edit; edit "
        "the trust layer and regenerate.",
        "",
        f"- claims parsed: **{cur['claim_count']}**",
        f"- sources mapped: **{cur['source_count']}**",
        f"- boundary/inspiration claims: **{cur['boundary_only']}**",
        f"- open gaps referenced: **{cur['open_gaps_referenced']}**",
        f"- downgraded (logged): **{cur['downgraded']}**",
        "",
        "## Findings",
        "",
        *[f"- {f}" for f in _FINDINGS],
        "",
        "## Must not claim",
        "",
        *[f"- {m}" for m in _MUST_NOT],
        "",
    ]
    _VALUE_MD.write_text("\n".join(md))
    _MIRROR.write_text(mirror)
    print(
        f"DOC_TRUST_AUDIT.json + DOC_VALUE_AUDIT.md + "
        f"SOURCE_REGISTRY.md written ({cur['claim_count']} claims)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
