import json
import sys

import numpy as np

from ctios import causal_runner as CR
from ctios.causal_agents import CausalLearnedAgent, NoActionAgent
from ctios.causal_env import CausalEnvironment
from ctios.causal_gate import evaluate
from ctios.causal_metrics import causal_action_gain, run_metrics

THR = {
    "min_causal_action_gain": 0.05,
    "max_allowed_action_null_gap": 0.02,
    "min_win_rate_vs_no_action": 0.80,
    "min_win_rate_vs_random_action": 0.80,
}


def _post_mae(agent_factory, mode, seed, delta=8.0):
    env = CausalEnvironment(10.0, 10.0 + delta, 300, 1.0, 600, seed, mode=mode)
    r = CR._run(env, agent_factory(), 600)
    return run_metrics(r["errors"], r["actions"], 300, 250)["post_shift_mae"]


def test_runner_sanity_writes_ledger(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["causal_runner", "--mode", "sanity"])
    assert CR.main() == 0
    led = CR.ROOT / "evidence" / "v5_causal_ledger.jsonl"
    assert led.exists()
    rows = [json.loads(x) for x in led.read_text().splitlines()]
    assert rows and {"agent", "mode", "post_shift_mae"} <= set(rows[0])


def test_causal_action_gain_computed_from_raw():
    g = [
        causal_action_gain(
            _post_mae(CausalLearnedAgent, "action_null", s),
            _post_mae(CausalLearnedAgent, "interventional", s),
        )
        for s in range(3)
    ]
    assert float(np.mean(g)) > THR["min_causal_action_gain"]


def test_action_null_gap_bounded_controlled():
    gap = float(
        np.mean(
            [
                abs(
                    _post_mae(CausalLearnedAgent, "action_null", s)
                    - _post_mae(NoActionAgent, "action_null", s)
                )
                for s in range(3)
            ]
        )
    )
    assert gap <= THR["max_allowed_action_null_gap"]


def test_interventional_causal_beats_no_action_controlled():
    wins = sum(
        _post_mae(CausalLearnedAgent, "interventional", s)
        < _post_mae(NoActionAgent, "interventional", s)
        for s in range(4)
    )
    assert wins >= 3


def test_gate_red_when_action_effect_disabled():
    g = evaluate(
        v4_tests_pass=True,
        v4_runner_green=True,
        replay_ok=True,
        no_leakage_ok=True,
        action_null_gap=0.0,
        interventional_effect_present=False,  # effect disabled
        causal_gain=1.0,
        win_rate_vs_no_action=1.0,
        win_rate_vs_random=1.0,
        grid_reproduced=True,
        evidence_written=True,
        claim_boundary_ok=True,
        thr=THR,
    )
    assert g.green is False
    assert any("interventional_effect_present" in r for r in g.reasons)
