# SPDX-License-Identifier: MIT
"""The arc as one runnable (verdict-isolation, V7): structure only,
no scientific verdict asserted."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.change_detection_arc import ARC, run_arc  # noqa: E402


def test_arc_is_the_six_pinned_lineages_in_order():
    assert [n for n, _, _ in ARC] == ["24", "25", "26", "27", "28", "29"]


def test_run_arc_well_formed_and_deterministic():
    a = run_arc()
    b = run_arc()
    assert len(a) == 6
    assert [r["spec_sha256"] for r in a] == [r["spec_sha256"] for r in b]
    for r in a:
        assert r["status"] in ("GREEN", "PARTIAL", "RED")
        assert isinstance(r["spec_sha256"], str) and r["spec_sha256"]
        assert r["battery_clean"] is True  # every lineage is discriminative
        assert 0 < r["checks_total"] >= r["checks_passed"]
