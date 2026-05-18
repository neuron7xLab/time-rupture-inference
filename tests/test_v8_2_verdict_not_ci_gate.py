# SPDX-License-Identifier: MIT
"""The scientific verdict must NOT be encoded as a pytest assertion: a
legitimate RED/PARTIAL_RED keeps CI green. This test asserts that the
diagnostic source contains no pytest-style threshold gate and that no CI
workflow invokes the v8.2 diagnostic."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_diagnostic_not_in_ci_workflows():
    for wf in (ROOT / ".github" / "workflows").glob("*.yml"):
        assert "run_v8_2_trigger_scoped_diagnostic" not in wf.read_text()


def test_no_test_asserts_v8_2_verdict():
    here = Path(__file__).name
    for tf in (ROOT / "tests").glob("test_v8_2_*.py"):
        if tf.name == here:  # this guard names the forbidden patterns itself
            continue
        src = tf.read_text()
        assert "trigger_context_gap_ratio >=" not in src
        assert 'verdict == "GREEN"' not in src
