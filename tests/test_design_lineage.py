# SPDX-License-Identifier: MIT
"""The design-lineage doc is a guard, not decoration: every brain-fact
row must point at a real, existing mechanism AND its test."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.design_lineage import MAPPINGS, missing_paths, write  # noqa: E402


def test_seven_mappings_present():
    assert len(MAPPINGS) == 7
    for m in MAPPINGS:
        assert m.fact and m.principle and m.mechanism and m.test
        assert m.not_claimed


def test_every_cited_mechanism_and_test_exists():
    assert missing_paths() == []
    for m in MAPPINGS:
        assert (ROOT / m.mechanism).exists()
        assert (ROOT / m.test).exists()


def test_doc_is_generated_with_boundary():
    p = write()
    txt = p.read_text()
    assert "Boundary" in txt and "NOT a brain" in txt
    assert "all_mechanisms_present: **True**" in txt


def test_guard_fails_if_a_mechanism_is_removed(monkeypatch):
    import ctios.design_lineage as dl

    broken = dl.Mapping(
        "f", "p", "src/ctios/_does_not_exist.py", "tests/_nope.py", "n"
    )
    monkeypatch.setattr(dl, "MAPPINGS", [broken])
    assert dl.missing_paths() == [
        "src/ctios/_does_not_exist.py",
        "tests/_nope.py",
    ]
