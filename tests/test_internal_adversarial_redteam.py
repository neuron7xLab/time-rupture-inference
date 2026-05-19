# SPDX-License-Identifier: MIT
"""Internal adversarial red-team contract. The honesty invariant is
load-bearing: the artifact can NEVER self-declare independent
validation, and any role breach fails closed. Roles are stubbed (no
nested pytest) so this stays fast and deterministic."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import internal_adversarial_redteam as rt  # noqa: E402


def _clean(role):
    return lambda: {"role": role, "breach": False, "probe": "x",
                    "detail": "ok"}


def _breach(role):
    return lambda: {"role": role, "breach": True, "probe": "x",
                    "detail": "planted breach"}


def test_independence_is_a_hard_false_invariant(monkeypatch):
    monkeypatch.setattr(rt, "_ROLES", [_clean("A"), _clean("B")])
    rep = rt.run()
    assert rep["independent_validation"] is False
    assert rep["tier"] == "INTERNAL_ADVERSARIAL"
    assert "OPEN" in rep["gap_1_status"]
    assert rep["all_roles_clean"] is True


def test_any_role_breach_fails_closed(monkeypatch):
    monkeypatch.setattr(
        rt, "_ROLES", [_clean("A"), _breach("SKEPTIC")])
    rep = rt.run()
    assert rep["all_roles_clean"] is False
    assert "SKEPTIC" in rep["breached_roles"]
    # even on breach, independence is still never asserted
    assert rep["independent_validation"] is False


def test_main_exit_codes(monkeypatch, tmp_path):
    monkeypatch.setattr(rt, "_OUT", tmp_path / "rt.json")
    monkeypatch.setattr(rt, "_ROLES", [_clean("A")])
    assert rt.main() == 0
    monkeypatch.setattr(rt, "_ROLES", [_breach("A")])
    assert rt.main() == 1


def test_sealed_artifact_self_declares_non_independent(
    monkeypatch, tmp_path
):
    out = tmp_path / "rt.json"
    monkeypatch.setattr(rt, "_OUT", out)
    monkeypatch.setattr(rt, "_ROLES", [_clean("A")])
    rt.main()
    import json
    doc = json.loads(out.read_text())
    assert doc["independent_validation"] is False
    assert "cannot close it" in doc["gap_1_status"]
