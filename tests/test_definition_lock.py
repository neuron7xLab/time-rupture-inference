"""The definition lock (STAGE 2) is admissible only if every term is
fully populated and anchored to a real falsifier. These tests are that
gate: a term that cannot be defined, observed, failed, and tested cannot
ship.
"""

from __future__ import annotations

import pytest

from ctios import definition_lock as dl


def test_lock_is_admissible():
    assert dl.validate() == []


def test_every_term_has_all_six_fields():
    for d in dl.LOCK:
        assert d.term.strip()
        assert d.definition.strip()
        assert d.not_this.strip()
        assert d.observable_signal.strip()
        assert d.failure_condition.strip()
        assert d.test.strip()


def test_every_anchor_resolves_to_a_real_file():
    missing = [d.term for d in dl.LOCK if not d.anchor_exists()]
    assert not missing, f"unanchored terms: {missing}"


def test_terms_are_unique():
    assert len(dl.TERMS) == len(set(dl.TERMS))


def test_get_round_trips():
    for term in dl.TERMS:
        assert dl.get(term).term == term


def test_get_unknown_raises():
    with pytest.raises(KeyError):
        dl.get("does-not-exist")


def test_bounded_non_claims_negate_the_system():
    # cognition/neural must be locked as NON-claims: not_this references
    # the system / biology so the term can never inflate.
    for term in ("cognition", "neural"):
        d = dl.get(term)
        assert any(w in d.not_this.lower() for w in ("not", "system", "biolog"))


def test_validate_detects_unanchored(monkeypatch):
    broken = dl.Definition(
        term="ghost", definition="x", not_this="x",
        observable_signal="x", failure_condition="x",
        test="tests/does_not_exist_zzz.py",
    )
    monkeypatch.setattr(dl, "LOCK", (*dl.LOCK, broken))
    assert any("ghost" in v for v in dl.validate())
