# SPDX-License-Identifier: MIT
"""Windowed-detector OOD-transfer contract (verdict-isolation, V7).

Not hard-asserted GREEN. Asserted: determinism, the report-only
boundary map covers all 7 families, the in-scope Gaussian positive
replicates under the portfolio harness, and the pinned kill test (the
detect-everything fake MUST fail the OOD null-family false-alarm gate;
the falsifier MUST stay discriminative)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.windowed_change_detector import calibrate_lambda  # noqa: E402
from ctios.windowed_detector_ood import (  # noqa: E402
    _AlwaysFire,
    _boundary_map,
    _gated,
    _NeverFire,
    run_verdict_metrics,
    verdict,
)


def test_metrics_deterministic_and_preregistered_set():
    a = run_verdict_metrics()
    b = run_verdict_metrics()
    assert a == b
    assert set(a) == {
        "calib_lambda", "null_family_false_alarm", "gaussian_detect_rate",
        "always_fake_blocked", "never_fake_blocked", "leakage",
        "boundary_map_emitted",
    }
    assert a["leakage"] == 0.0


def test_boundary_map_covers_all_seven_families():
    bmap = _boundary_map(calibrate_lambda())
    assert len(bmap) == 7
    for v in bmap.values():
        assert {"fire_rate", "detect_rate"} <= set(v)


def test_in_scope_gaussian_positive_replicates():
    # The #26 result must survive an independent portfolio harness.
    m = run_verdict_metrics()
    assert m["gaussian_detect_rate"] >= 0.50


def test_kill_test_always_fire_fails_ood_null_gate():
    fa, dr = _gated(_AlwaysFire())
    assert fa > 0.10  # detect-everything cannot hold the null bound
    n_fa, n_dr = _gated(_NeverFire())
    assert n_dr < 0.50  # detect-nothing cannot meet detection
    m = run_verdict_metrics()
    assert m["always_fake_blocked"] == 1.0
    assert m["never_fake_blocked"] == 1.0


def test_pinned_verdict_well_formed_and_discriminative():
    v = verdict()
    assert v.status in ("GREEN", "PARTIAL", "RED")
    assert v.battery["negative_control_fails"] is True
    assert v.battery["deterministic"] and v.battery["finite"]
    assert v.spec_sha256
