# SPDX-License-Identifier: MIT
"""Engine contract (synthetic probes — fast, deterministic). The
scientific verdict of the bundled demo is NOT asserted here
(verdict-isolation, V7): a legitimate RED keeps CI green."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.falsify import HypothesisSpec, falsify  # noqa: E402

SPEC = HypothesisSpec(
    hid="t",
    claim="m below g",
    null="m not below g",
    thresholds={"g": 1.0},
    checks=[{"metric": "m", "op": "<=", "threshold_key": "g"}],
)


def _good(_t):
    return {"m": 0.5}


def _bad(_t):
    return {"m": 9.0}


def test_green_when_check_and_battery_pass(tmp_path):
    v = falsify(SPEC, _good, negative_control=_bad, evidence_dir=tmp_path)
    assert v.status == "GREEN"
    assert v.battery["deterministic"] and v.battery["finite"]
    assert v.battery["thresholds_load_bearing"]
    assert v.battery["negative_control_fails"]
    assert not (tmp_path / "NEGATIVE_FALSIFY_t.json").exists()


def test_red_when_check_fails_and_sealed(tmp_path):
    v = falsify(SPEC, _bad, negative_control=_good, evidence_dir=tmp_path)
    assert v.status == "RED"
    assert any("check failed" in r for r in v.reasons)
    assert (tmp_path / "NEGATIVE_FALSIFY_t.md").exists()  # sealed negative


def test_battery_catches_nondeterministic_probe():
    import itertools

    c = itertools.count()

    def flaky(_t):
        return {"m": 0.5 + 1e-3 * next(c)}

    v = falsify(SPEC, flaky)
    assert v.battery["deterministic"] is False
    assert v.status != "GREEN"


def test_battery_catches_pseudo_green_negative_control():
    # negative control ALSO passes the checks -> gate is not discriminative
    v = falsify(SPEC, _good, negative_control=_good)
    assert v.battery["negative_control_fails"] is False
    assert v.status != "GREEN"


def test_spec_sha_stable_and_threshold_mutation_changes_it():
    a = SPEC.sha()
    b = HypothesisSpec("t", "c", "n", {"g": 2.0}, SPEC.checks).sha()
    assert a == SPEC.sha() and a != b


def test_bundled_demo_runs_and_returns_well_formed_verdict(tmp_path):
    # structural only — does NOT assert GREEN (verdict isolation)
    from ctios.falsify import HypothesisSpec as HS
    from ctios.falsify_cli import _candidate, _negative_control

    spec = HS.load(ROOT / "prereg" / "demo_temporal_causal_floor.yaml")
    v = falsify(spec, _candidate, negative_control=_negative_control,
                evidence_dir=tmp_path)
    assert v.status in ("GREEN", "PARTIAL", "RED")
    assert "h2r" in v.metrics and set(v.battery) >= {
        "deterministic", "finite", "thresholds_load_bearing",
        "negative_control_fails",
    }
    assert (tmp_path / "FALSIFY_temporal_causal_floor.json").exists()
