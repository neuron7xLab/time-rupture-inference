# SPDX-License-Identifier: MIT
"""Carrier-robust-observable contract (verdict-isolation, V7).

Not hard-asserted GREEN. Asserted: determinism, fixed-quantile rule,
the pinned kill test (detect-everything MUST fail the OOD null-family
gate), and that the falsifier stays discriminative."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.carrier_robust_observable import (  # noqa: E402
    _AlwaysFire,
    _gates,
    _NeverFire,
    calibrate_lambda,
    run_verdict_metrics,
    verdict,
)


def test_metrics_deterministic_and_preregistered_set():
    a = run_verdict_metrics()
    b = run_verdict_metrics()
    assert a == b
    assert set(a) == {
        "calib_lambda", "carrier_detect_rate", "null_family_false_alarm",
        "gaussian_detect_rate", "always_fake_blocked",
        "never_fake_blocked", "leakage",
    }
    assert a["leakage"] == 0.0


def test_calibrate_lambda_fixed_quantile_rule():
    assert calibrate_lambda(0.10) == calibrate_lambda(0.10)
    assert calibrate_lambda(0.01) >= calibrate_lambda(0.20)


def test_kill_test_always_fire_fails_ood_null_gate():
    a_cdr, a_fa, a_gdr = _gates(_AlwaysFire())
    assert a_fa > 0.10  # detect-everything cannot hold the null bound
    n_cdr, n_fa, n_gdr = _gates(_NeverFire())
    assert n_cdr < 0.50 and n_gdr < 0.50  # detect-nothing cannot detect
    m = run_verdict_metrics()
    assert m["always_fake_blocked"] == 1.0
    assert m["never_fake_blocked"] == 1.0


def test_pinned_verdict_well_formed_and_discriminative():
    v = verdict()
    assert v.status in ("GREEN", "PARTIAL", "RED")
    assert v.battery["negative_control_fails"] is True
    assert v.battery["deterministic"] and v.battery["finite"]
    assert v.battery["thresholds_load_bearing"] is True
    assert v.spec_sha256
