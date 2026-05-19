# SPDX-License-Identifier: MIT
"""Complementary doc-claim-source gate contract. Every negative case
fails closed; the live repo passes."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_doc_claim_sources as dcs  # noqa: E402


def test_live_repo_passes():
    assert dcs.audit() == []


def test_missing_required_doc_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(dcs, "_ROOT", tmp_path)
    assert any("missing required doc" in e for e in dcs.audit())


def test_unmapped_term_fails(tmp_path, monkeypatch):
    refs = tmp_path / "REFERENCES.md"
    refs.write_text("# References\n(nothing relevant here)\n")
    doc = tmp_path / "README.md"
    doc.write_text("We rely on predictive coding throughout.\n")
    monkeypatch.setattr(dcs, "_REFERENCES", refs)
    monkeypatch.setattr(dcs, "_ROOT", tmp_path)
    monkeypatch.setattr(dcs, "_REQUIRED", [])
    monkeypatch.setattr(dcs, "_DOCS", ["README.md"])
    probs = dcs.audit()
    assert any("predictive coding" in p and "absent" in p for p in probs)


def test_forbidden_phrase_outside_disclaimer_fails(tmp_path, monkeypatch):
    refs = tmp_path / "REFERENCES.md"
    refs.write_text("predictive coding slsa spdx nist model card\n")
    doc = tmp_path / "README.md"
    doc.write_text("This system is productizable now.\n")
    monkeypatch.setattr(dcs, "_REFERENCES", refs)
    monkeypatch.setattr(dcs, "_ROOT", tmp_path)
    monkeypatch.setattr(dcs, "_REQUIRED", [])
    monkeypatch.setattr(dcs, "_DOCS", ["README.md"])
    assert any("forbidden phrase" in p for p in dcs.audit())


def test_forbidden_phrase_in_disclaimer_passes(tmp_path, monkeypatch):
    refs = tmp_path / "REFERENCES.md"
    refs.write_text("predictive coding slsa spdx nist model card\n")
    doc = tmp_path / "README.md"
    doc.write_text(
        "<!-- claims:disclaimer -->\n"
        "Not productizable; no AGI is claimed.\n"
        "<!-- claims:end -->\n"
    )
    monkeypatch.setattr(dcs, "_REFERENCES", refs)
    monkeypatch.setattr(dcs, "_ROOT", tmp_path)
    monkeypatch.setattr(dcs, "_REQUIRED", [])
    monkeypatch.setattr(dcs, "_DOCS", ["README.md"])
    assert dcs.audit() == []
