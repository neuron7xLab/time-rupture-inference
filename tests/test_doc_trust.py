# SPDX-License-Identifier: MIT
"""Doc-trust gate contract — adversarial. Every negative case fails
closed; the live repo passes. tests/ is outside claims_lint scan
scope, so the crafted forbidden-phrase fixtures here do not trip the
lexicon gate.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_doc_trust as cdt  # noqa: E402

_HDR = (
    "| claim_id | exact_claim_text | claim_class | location | "
    "evidence_path | source_id | falsifier | status |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


def _matrix(tmp_path, monkeypatch, row: str) -> None:
    m = tmp_path / "CLAIM_SOURCE_MATRIX.md"
    m.write_text(_HDR + row + "\n")
    monkeypatch.setattr(cdt, "_MATRIX", m)


# ---- live repo ----
def test_live_repo_passes():
    assert cdt.audit() == []


def test_live_repo_has_at_least_20_claims():
    assert len(cdt._matrix_rows()) >= 20


# ---- required files / dedupe ----
def test_missing_required_file_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(cdt, "_ROOT", tmp_path)
    assert any("required trust-layer file missing" in p
               for p in cdt.audit())


def test_duplicate_manual_note_docs_fail(tmp_path, monkeypatch):
    legacy = tmp_path / "MANUAL_AUTHOR_NOTES.md"
    legacy.write_text("# stray duplicate\n")
    monkeypatch.setattr(cdt, "_LEGACY_NOTES", legacy)
    assert any("duplicate manual-note doc" in p for p in cdt.audit())


def test_missing_source_registry_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(cdt, "_REG_YAML", tmp_path / "absent.yaml")
    # required-file scan keys off _ROOT, but the registry read happens
    # after; force the required check to see it missing too:
    monkeypatch.setattr(cdt, "_ROOT", tmp_path)
    assert any("missing" in p for p in cdt.audit())


# ---- per-row class contracts ----
def test_unknown_source_id_fails(tmp_path, monkeypatch):
    _matrix(tmp_path, monkeypatch,
            "| TRI-CLAIM-001 | x | ENGINEERING_MECHANISM | docs/SPEC.md "
            "| src/ctios/env.py | NOT_A_REAL_SOURCE | f | ACTIVE |")
    assert any("absent from registry" in p for p in cdt.audit())


def test_missing_evidence_path_fails(tmp_path, monkeypatch):
    _matrix(tmp_path, monkeypatch,
            "| TRI-CLAIM-001 | x | EMPIRICAL_RESULT | README "
            "|  | POPPER_FALSIFIABILITY | f | ACTIVE |")
    assert any("empty evidence_path" in p for p in cdt.audit())


def test_empirical_without_runnable_path_fails(tmp_path, monkeypatch):
    _matrix(tmp_path, monkeypatch,
            "| TRI-CLAIM-001 | x | EMPIRICAL_RESULT | README "
            "| just prose | POPPER_FALSIFIABILITY | f | ACTIVE |")
    assert any("without a runnable/artifact path" in p
               for p in cdt.audit())


def test_inspiration_without_bio_boundary_fails(tmp_path, monkeypatch):
    _matrix(tmp_path, monkeypatch,
            "| TRI-CLAIM-019 | prediction-error framing | "
            "INSPIRATION_ONLY | README | src/ctios/agents.py | "
            "RAO_BALLARD_1999 | f | ACTIVE |")
    assert any("does not imply biological fidelity" in p
               for p in cdt.audit())


def test_supply_chain_without_ceiling_fails(tmp_path, monkeypatch):
    _matrix(tmp_path, monkeypatch,
            "| TRI-CLAIM-015 | supply chain hardened | "
            "SUPPLY_CHAIN_TRUST | docs/SUPPLY_CHAIN_TRUST.md | "
            "scripts/check.py | SLSA_SPEC | f | ACTIVE |")
    assert any("not-hermetic / not-SLSA-L3" in p for p in cdt.audit())


def test_open_gap_without_link_fails(tmp_path, monkeypatch):
    _matrix(tmp_path, monkeypatch,
            "| TRI-CLAIM-017 | breadth open | OPEN_GAP | docs/SPEC.md "
            "| evidence/ sealed | LAKATOS_RESEARCH_PROGRAMMES | f | ACTIVE |")
    assert any("not linked to OPEN_STRUCTURAL_GAPS" in p
               for p in cdt.audit())


def test_thin_matrix_fails(tmp_path, monkeypatch):
    _matrix(tmp_path, monkeypatch,
            "| TRI-CLAIM-001 | x | GOVERNANCE_MECHANISM | claims.yaml "
            "| scripts/claims_lint.py | POPPER_FALSIFIABILITY | f | ACTIVE |")
    assert any("matrix too thin" in p for p in cdt.audit())


# ---- forbidden-phrase scanner ----
def test_forbidden_phrase_detected_outside_disclaimer():
    hits = cdt._forbidden_hits("This artifact is productizable today.\n")
    assert hits and "productizable" in hits[0]


def test_agi_phrase_detected_outside_disclaimer():
    hits = cdt._forbidden_hits("It achieves AGI on this benchmark.\n")
    assert hits and "agi" in hits[0]


def test_forbidden_phrase_exempt_inside_disclaimer():
    txt = (
        "<!-- claims:disclaimer -->\n"
        "Not productizable; AGI is not claimed.\n"
        "<!-- claims:end -->\n"
    )
    assert cdt._forbidden_hits(txt) == []


def test_forbidden_phrase_exempt_on_boundary_line():
    assert cdt._forbidden_hits(
        "Product readiness is blocked while a gap is OPEN.\n"
    ) == []


# ---- README discipline ----
def test_readme_bibliography_bloat_fails(tmp_path, monkeypatch):
    rd = tmp_path / "README.md"
    rd.write_text("## Reviewer map\n\n## References\n\n- a\n- b\n")
    monkeypatch.setattr(cdt, "_README", rd)
    assert any("must not carry a bibliography" in p for p in cdt.audit())


def test_review_notes_word_cap_enforced(tmp_path, monkeypatch):
    big = tmp_path / "MANUAL_REVIEW_NOTES.md"
    big.write_text(" ".join(["word"] * 950))
    monkeypatch.setattr(cdt, "_NOTES", big)
    assert any("too long" in p for p in cdt.audit())
