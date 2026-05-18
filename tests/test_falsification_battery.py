"""The 7-rung battery from the doctrine, run as fast unit-scale checks."""

import numpy as np

from ctios.agents import InjectedAgent, LastIntervalAgent, LearnedAgent
from ctios.contract import EVAL_HORIZON
from ctios.env import Environment


def _post_mae(agent, seed, tau1=17.0, t_star=300):
    env = Environment(10.0, tau1, t_star, 1.0, 600, seed)
    errs = []
    for _k in range(600):
        p = agent.predict()
        o = env.step()
        errs.append(abs(o.observed_interval - p))
        agent.update(o.observed_interval)
    return float(np.mean(errs[t_star : t_star + EVAL_HORIZON]))


def test_rung1_survives_time_shift():
    assert _post_mae(LearnedAgent(prior=1.0), 0) < 3.0


def test_rung2_survives_unseen_shift_size():
    assert _post_mae(LearnedAgent(prior=1.0), 0, tau1=23.0) < 4.0


def test_rung3_works_without_injected_solution():
    # learned never receives tau0/tau1 — already enforced; here: it still wins
    assert _post_mae(LearnedAgent(prior=1.0), 1) < _post_mae(InjectedAgent(10.0), 1)


def test_rung4_beats_simple_baseline():
    assert _post_mae(LearnedAgent(prior=1.0), 2) < _post_mae(LastIntervalAgent(1.0), 2)


def test_rung5_explains_failure_no_update():
    assert _post_mae(LearnedAgent(prior=1.0, use_update=False), 0) > 5.0


def test_rung6_negative_control_no_shift():
    # no regime change: learned must not destabilise (low error throughout)
    assert _post_mae(LearnedAgent(prior=1.0), 0, tau1=10.0) < 2.0


def test_rung7_multi_seed_consistency():
    wins = sum(
        _post_mae(LearnedAgent(prior=1.0), s) < _post_mae(InjectedAgent(10.0), s)
        for s in range(8)
    )
    assert wins >= 7
