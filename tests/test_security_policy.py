# SPDX-License-Identifier: MIT
"""PR M — SECURITY.md is real, not placeholder theatre."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SEC = ROOT / "SECURITY.md"


def test_security_md_exists():
    assert SEC.exists()


def test_required_sections_present():
    t = SEC.read_text()
    for s in ("Supported versions", "Reporting a vulnerability",
              "Response", "security scope"):
        assert s in t, f"SECURITY.md missing section: {s}"
    assert "3.11" in t and "3.13" in t
    assert "14 days" in t


def test_no_placeholder_or_fake_contact():
    t = SEC.read_text()
    assert not re.search(r"\b(TODO|TBD|FIXME|XXX)\b", t)
    # no fabricated email / PGP block
    assert not re.search(
        r"[\w.]+@(example|test|your|email|company)\.", t, re.I
    )
    assert "BEGIN PGP" not in t
    assert "@" not in t or "no email address" in t.lower()


def test_states_honest_fallback_not_fake_sla():
    t = SEC.read_text().lower()
    assert "best effort" in t
    assert "private vulnerability reporting" in t
    assert "no email address or pgp key is published" in t
