# SPDX-License-Identifier: MIT
"""Calibrated-change-detector contract (verdict-isolation, V7).

The scientific verdict is NOT asserted GREEN: a legitimate PARTIAL/RED
keeps CI green. Asserted: determinism, disjoint calib/eval seeds, the
pinned kill test (the 'detect-everything' fake MUST be rejected by the
false-alarm check), and that the falsifier is discriminative."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.calibrated_change_detector import (  # noqa: E402
    _CAL_NULL,
    _EVAL_NULL,
    _EVAL_RUPT,
    AlwaysFireDetector,
    NeverFireDetector,
    calibrate_lambda,
    run_verdict_metrics,
    verdict,
)


def test_calibration_and_evaluation_seeds_are_disjoint():
    cal = set(_CAL_NULL)
    assert cal.isdisjoint(set(_EVAL_RUPT))
    assert cal.isdisjoint(set(_EVAL_NULL))
    assert set(_EVAL_RUPT).isdisjoint(set(_EVAL_NULL))


def test_metrics_deterministic_and_preregistered_set():
    a = run_verdict_metrics()
    b = run_verdict_metrics()
    assert a == b
    assert set(a) == {
        "calib_lambda", "eval_null_false_alarm", "detect_rate",
        "always_fake_blocked", "never_fake_blocked", "leakage",
    }
    assert a["leakage"] == 0.0


def test_calibrate_lambda_is_a_fixed_quantile_rule():
    assert calibrate_lambda(0.10) == calibrate_lambda(0.10)
    # stricter alpha -> higher (or equal) threshold
    assert calibrate_lambda(0.01) >= calibrate_lambda(0.20)


def test_kill_test_detect_everything_fake_is_rejected():
    # AlwaysFire would fool a detect-rate-only gate. The pinned
    # false-alarm check MUST block it.
    m = run_verdict_metrics()
    assert m["always_fake_blocked"] == 1.0
    assert m["never_fake_blocked"] == 1.0
    # structural: the always-fire fake fires on a null stream too
    import numpy as np
    assert AlwaysFireDetector().detect(np.zeros(600)) >= 0
    assert NeverFireDetector().detect(np.zeros(600)) == -1


def test_pinned_verdict_runs_well_formed_not_asserted_green():
    v = verdict()
    assert v.status in ("GREEN", "PARTIAL", "RED")
    assert v.battery["negative_control_fails"] is True  # discriminative
    assert v.battery["deterministic"] and v.battery["finite"]
    assert v.spec_sha256
