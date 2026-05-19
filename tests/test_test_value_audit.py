# SPDX-License-Identifier: MIT
"""WP5 meta — no weak/decorative test is counted as proof; the audit
itself fires on a planted smoke-only file."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.test_value_audit import WEAK, audit, classify, weak_files  # noqa: E402


def test_no_weak_or_decorative_tests_in_suite():
    assert weak_files() == [], f"weak tests: {weak_files()}"


def test_classifier_detects_a_smoke_only_body():
    smoke = "def test_x():\n    r = run()\n    assert r\n"
    assert classify(smoke) == WEAK


def test_classifier_recognizes_kill_and_artifact():
    assert classify("with pytest.raises(X): f()") == "KILL_TEST"
    assert classify("assert (p / 'a.json').exists()") == "ARTIFACT_TEST"


def test_every_test_file_classified():
    a = audit()
    assert len(a) >= 60
    assert all(v for v in a.values())
