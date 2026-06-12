"""The seven power points must be proven fractal — each principle must
recur at two or more real scales. These tests are that proof; if a
principle stops recurring (an anchor is deleted, a scorer drops the law),
a test goes red.
"""

from __future__ import annotations

import pytest

from ctios import fractal_invariants as fi


def test_exactly_seven_power_points():
    assert len(fi.POINTS) == 7


def test_all_power_points_are_fractal():
    assert fi.validate() == []


def test_every_point_recurs_at_two_real_scales():
    for p in fi.POINTS:
        assert p.is_fractal(), f"{p.id} {p.name} is not fractal"
        assert len(p.live_scales()) >= fi.MIN_SCALES


def test_every_anchor_is_on_disk():
    dead = {p.id: [m.where for m in p.manifestations if not m.exists()]
            for p in fi.POINTS}
    dead = {k: v for k, v in dead.items() if v}
    assert not dead, f"dead anchors: {dead}"


def test_ids_unique_and_named():
    assert len(fi.IDS) == len(set(fi.IDS))
    for p in fi.POINTS:
        assert p.name and p.principle and p.deepening


def test_report_marks_all_fractal():
    rep = fi.report()
    assert rep["all_fractal"] is True
    assert len(rep["power_points"]) == 7
    assert all(pp["fractal"] for pp in rep["power_points"])


def test_get_round_trips_and_rejects_unknown():
    for pid in fi.IDS:
        assert fi.get(pid).id == pid
    with pytest.raises(KeyError):
        fi.get("P99")


def test_non_fractal_point_is_rejected(monkeypatch):
    lonely = fi.PowerPoint(
        id="PX", name="lonely", principle="x", deepening="x",
        manifestations=(fi.Manifestation("module", "CLAUDE.md", "only one"),),
    )
    monkeypatch.setattr(fi, "POINTS", (*fi.POINTS, lonely))
    viol = fi.validate()
    assert any("PX" in v for v in viol)
