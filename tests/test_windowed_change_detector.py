# SPDX-License-Identifier: MIT
"""Windowed-change-detector contract (verdict-isolation, V7).

The scientific verdict is NOT hard-asserted GREEN (a future legitimate
shift must not red CI on a science result). Asserted: disjoint
calib/eval seeds, determinism, the fixed-quantile rule, and the pinned
kill test — the 'detect-everything' fake MUST be rejected by the
false-alarm check, and the falsifier MUST be discriminative."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.windowed_change_detector import (  # noqa: E402
    _CAL_NULL,
    _EVAL_NULL,
    _EVAL_RUPT,
    AlwaysFireDetector,
    NeverFireDetector,
    calibrate_lambda,
    run_verdict_metrics,
    verdict,
)


def test_calibration_and_evaluation_seeds_disjoint():
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


def test_calibrate_lambda_fixed_quantile_rule():
    assert calibrate_lambda(0.10) == calibrate_lambda(0.10)
    assert calibrate_lambda(0.01) >= calibrate_lambda(0.20)


def test_kill_test_detect_everything_is_rejected():
    m = run_verdict_metrics()
    assert m["always_fake_blocked"] == 1.0
    assert m["never_fake_blocked"] == 1.0
    import numpy as np

    assert AlwaysFireDetector().detect(np.zeros(600)) >= 0
    assert NeverFireDetector().detect(np.zeros(600)) == -1


def test_pinned_verdict_well_formed_and_discriminative():
    v = verdict()
    assert v.status in ("GREEN", "PARTIAL", "RED")  # isolation
    assert v.battery["negative_control_fails"] is True
    assert v.battery["deterministic"] and v.battery["finite"]
    assert v.battery["thresholds_load_bearing"] is True
    assert v.spec_sha256
