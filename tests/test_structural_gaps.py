# SPDX-License-Identifier: MIT
"""PR M — structural gaps are machine-guarded: cannot be CLOSED
without committed evidence; READY impossible while OPEN."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.external_validation import real_external_run_attested  # noqa: E402
from ctios.readiness_score import compute_readiness  # noqa: E402

GAPS = ROOT / "docs" / "OPEN_STRUCTURAL_GAPS.md"


def _gap_status(name: str) -> str:
    blk = re.search(
        rf"## {name}\b(.*?)(?=\n## |\Z)", GAPS.read_text(), re.S
    )
    assert blk, f"{name} missing"
    m = re.search(r"status:\s*(\w+)", blk.group(1))
    return m.group(1) if m else "MISSING"


def test_gaps_file_exists_with_both_gaps():
    t = GAPS.read_text()
    assert "GAP_1: INDEPENDENT_REPRODUCTION" in t
    assert "GAP_2: DOMAIN_BREADTH" in t
    assert t.count("acceptance_criteria:") >= 2
    assert "evidence_to_close:" in t


def test_both_gaps_are_open():
    assert _gap_status("GAP_1: INDEPENDENT_REPRODUCTION") == "OPEN"
    assert _gap_status("GAP_2: DOMAIN_BREADTH") == "OPEN"


def test_gap1_close_evidence_absent_so_must_stay_open():
    # GAP_1 closes only with a valid external bundle; it does not exist.
    assert not (ROOT / "evidence" / "EXTERNAL_VALIDATION_BUNDLE.json").exists()
    assert real_external_run_attested() is False
    assert _gap_status("GAP_1: INDEPENDENT_REPRODUCTION") == "OPEN"


def test_gap2_close_evidence_absent():
    assert not (ROOT / "evidence" / "DOMAIN_BREADTH_BUNDLE.json").exists()
    assert _gap_status("GAP_2: DOMAIN_BREADTH") == "OPEN"


def test_ready_impossible_while_gaps_open():
    r = compute_readiness(gates_all_pass=True)
    assert r.status not in ("READY", "PRODUCTIZABLE")
    assert any("real_external" in b for b in r.blocking_facts)
