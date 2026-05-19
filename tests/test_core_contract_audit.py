# SPDX-License-Identifier: MIT
"""WP1 closure — contract/kill tests for core modules the audit found
without direct coverage. Not "it runs": each asserts behaviour and a
kill case."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from ctios.drift import CUSUM, PageHinkley  # noqa: E402
from ctios.gates import evaluate_gate  # noqa: E402
from ctios.ledger import append, provenance  # noqa: E402
from ctios.utils import sha256_text  # noqa: E402


def test_drift_detectors_quiet_on_stationary_fire_on_step():
    rng = np.random.default_rng(0)
    for Det in (PageHinkley, CUSUM):
        d = Det()
        # stationary small noise -> must NOT fire
        assert not any(d.update(float(x)) for x in rng.normal(0, 0.1, 200))
        d.reset()
        fired = False
        for k in range(400):
            x = 0.1 if k < 200 else 6.0  # hard step at 200
            fired = d.update(float(x)) or fired
        assert fired, f"{Det.__name__} missed an obvious step change"


def test_drift_is_deterministic_and_reset_clears_state():
    a, b = PageHinkley(), PageHinkley()
    seq = [0.1, 0.2, 9.0, 9.0, 9.0]
    assert [a.update(v) for v in seq] == [b.update(v) for v in seq]
    a.reset()
    assert a._m == 0.0 and a._n == 0


def test_evaluate_gate_is_discriminative_kill_case():
    def _m(mae, aue):
        return {
            "post_shift_mae": mae,
            "area_under_post_shift_error": aue,
            "adaptation_time": 5.0,
            "detection_delay": 2.0,
            "false_alarm_rate": 0.0,
        }

    base = dict(
        agg={
            "learned_full": _m(0.9, 10.0),
            "injected": _m(8.0, 90.0),
            "moving_average_3": _m(1.1, 12.0),
        },
        prereg={
            "adaptation_time_max": 50.0,
            "detection_delay_max": 50.0,
            "false_alarm_rate_max": 0.1,
            "min_win_rate": 0.9,
        },
        win_rate_learned_vs_injected=1.0,
        win_rate_learned_vs_baseline=1.0,
        ablation_ok=True,
        no_leakage_ok=True,
        replay_ok=True,
        prereg_before_run=True,
        every_delta_pass=True,
        shuffle_no_gain=True,
        neuro_markers={
            "synaptic": True, "homeostatic": True,
            "neuromodulation": True, "extinction": True,
        },
        n_seeds=30,
        n_deltas=3,
        min_seeds=30,
        min_deltas=3,
    )
    good = evaluate_gate(**base)
    leaked = evaluate_gate(**{**base, "no_leakage_ok": False})
    # the gate must distinguish a leaking run from a clean one
    assert good.green is True
    assert leaked.green is False
    assert any("leakage" in r for r in leaked.reasons)


def test_ledger_append_is_appendonly_and_parseable(tmp_path):
    p = tmp_path / "l.jsonl"
    append(p, {"b": 2, "a": 1})
    append(p, {"c": 3})
    lines = p.read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"a": 1, "b": 2}  # sorted keys
    prov = provenance()
    assert {"git_commit", "prereg_hash", "config_source_hash"} <= set(prov)


def test_utils_hash_is_deterministic_and_sensitive():
    assert sha256_text("x") == sha256_text("x")
    assert sha256_text("x") != sha256_text("y")
    assert len(sha256_text("x")) == 64


def test_v6_precision_postmae_is_deterministic_preserved_lineage():
    # verdict-isolation: v6 is a preserved-RED lineage; assert the
    # measurement is reproducible, NOT that it is GREEN.
    from ctios.agents import OracleAgent
    from ctios.contract import N_STEPS, SIGMA, T_STAR, TAU0
    from ctios.env import Environment
    from ctios.v6_precision import _post_mae

    def _run() -> tuple[float, str]:
        env = Environment(TAU0, 2.0, T_STAR, SIGMA, N_STEPS, 0)
        return _post_mae(OracleAgent(env.oracle_view()), env)

    m1, h1 = _run()
    m2, h2 = _run()
    assert h1 == h2 and m1 == m2  # deterministic replay
