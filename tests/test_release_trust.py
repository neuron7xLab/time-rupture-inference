# SPDX-License-Identifier: MIT
"""PR N — release trust: attestation present, gate precedes build/
attest, SLSA not overclaimed. Negatives fail closed; live repo passes.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_release_trust as art  # noqa: E402


def test_live_release_workflow_passes():
    assert art.audit() == []


def test_release_workflow_exists_with_perms():
    t = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    for p in (r"contents:\s*write", r"id-token:\s*write",
              r"attestations:\s*write"):
        assert re.search(p, t)
    assert "attest-build-provenance@" in t


def _mutate(monkeypatch, tmp_path, text):
    f = tmp_path / "release.yml"
    f.write_text(text)
    monkeypatch.setattr(art, "_REL", f)


GOOD = (ROOT / ".github" / "workflows" / "release.yml").read_text()


def test_missing_attestation_fails(monkeypatch, tmp_path):
    _mutate(monkeypatch, tmp_path,
            re.sub(r".*attest-build-provenance.*\n", "", GOOD))
    assert any("attestation" in p for p in art.audit())


def test_attest_before_gate_fails(monkeypatch, tmp_path):
    bad = ("permissions:\n  contents: write\n  id-token: write\n"
           "  attestations: write\n"
           "  - uses: actions/attest-build-provenance@"
           + "a" * 40 + " # v2\n"
           "  - run: python -m build\n"
           "  - run: PYTHONPATH=src pytest tests -q\n"
           "  - run: PYTHONPATH=src python -m ctios.runner --mode full\n"
           "  - run: python scripts/generate_sbom.py\n"
           "  - run: gh release create x\n")
    _mutate(monkeypatch, tmp_path, bad)
    probs = art.audit()
    assert any("BEFORE" in p or "AFTER" in p for p in probs)


def test_missing_id_token_fails(monkeypatch, tmp_path):
    _mutate(monkeypatch, tmp_path,
            GOOD.replace("id-token: write", "id-token: none"))
    assert any("id-token" in p for p in art.audit())


def test_missing_sbom_step_fails(monkeypatch, tmp_path):
    _mutate(monkeypatch, tmp_path,
            re.sub(r".*generate_sbom\.py.*\n", "", GOOD))
    assert any("SBOM" in p for p in art.audit())


def test_slsa_l3_overclaim_fails(monkeypatch, tmp_path):
    doc = tmp_path / "slsa.md"
    doc.write_text("This release is SLSA Build L3 fully isolated.\n")
    monkeypatch.setattr(art, "_SLSA", doc)
    assert any("L3" in p for p in art.audit())
