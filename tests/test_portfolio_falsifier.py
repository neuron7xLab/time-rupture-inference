# SPDX-License-Identifier: MIT
"""Portfolio-falsifier contract (verdict-isolation, V7).

Not hard-asserted GREEN. Asserted: determinism, the 7-family map,
in-scope rupture replication, and the pinned kill test (the
detect-everything fake MUST fail the no-rupture false-alarm gates)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.carrier_robust_observable import (  # noqa: E402
    CarrierRobustDetector,  # noqa: E402
    _AlwaysFire,
    _NeverFire,
)
from ctios.portfolio_falsifier import (  # noqa: E402
    _metrics,
    _scan,
    calibrate_lambda,
    run_verdict_metrics,
    verdict,
)


def test_metrics_deterministic_and_preregistered_set():
    a = run_verdict_metrics()
    b = run_verdict_metrics()
    assert a == b
    assert {
        "gaussian_detect_rate", "heavytail_detect_rate",
        "carrier_detect_rate", "null_false_alarm", "multimodal_false_alarm",
        "always_fake_blocked", "never_fake_blocked", "leakage",
        "portfolio_map_emitted", "calib_lambda",
    } == set(a)
    assert a["leakage"] == 0.0
    assert a["portfolio_map_emitted"] == 1.0


def test_scan_covers_seven_families():
    full = _scan(CarrierRobustDetector(calibrate_lambda()))
    assert len(full) == 7
    for v in full.values():
        assert {"fire_rate", "detect_rate", "is_rupture"} <= set(v)


def test_in_scope_rupture_families_replicate():
    m = run_verdict_metrics()
    assert m["gaussian_detect_rate"] >= 0.50
    assert m["heavytail_detect_rate"] >= 0.50
    assert m["carrier_detect_rate"] >= 0.50


def test_kill_test_always_fire_fails_norupture_gates():
    am = _metrics(_AlwaysFire())
    assert am["null_false_alarm"] > 0.10 or am["multimodal_false_alarm"] > 0.10
    nm = _metrics(_NeverFire())
    assert nm["gaussian_detect_rate"] < 0.50
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
