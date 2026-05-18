import numpy as np
import pytest

from ctios.agents import InjectedAgent, LearnedAgent, OracleAgent
from ctios.contract import EVAL_HORIZON
from ctios.env import Environment


def _post_mae(agent, env, n, t_star):
    env.reset()
    errs = []
    for _k in range(n):
        p = agent.predict()
        o = env.step()
        errs.append(abs(o.observed_interval - p))
        agent.update(o.observed_interval)
    return float(np.mean(errs[t_star : t_star + EVAL_HORIZON]))


def test_injected_fails_post_shift():
    env = Environment(10.0, 17.0, 300, 1.0, 600, 0)
    mae = _post_mae(InjectedAgent(10.0), env, 600, 300)
    assert mae > 5.0  # stuck at 10 while truth is 17


def test_learned_adapts_post_shift():
    env = Environment(10.0, 17.0, 300, 1.0, 600, 0)
    mae = _post_mae(LearnedAgent(prior=1.0), env, 600, 300)
    assert mae < 3.0  # must recover near the new regime


def test_oracle_is_upper_bound():
    env = Environment(10.0, 17.0, 300, 1.0, 600, 0)
    mae = _post_mae(OracleAgent(env.oracle_view()), env, 600, 300)
    assert mae < 1.3  # ~ sigma * sqrt(2/pi)


def test_no_update_does_not_adapt():
    env = Environment(10.0, 17.0, 300, 1.0, 600, 0)
    mae = _post_mae(LearnedAgent(prior=1.0, use_update=False), env, 600, 300)
    assert mae > 5.0


def test_anti_divergence_reduces_post_shift_overshoot():
    def late_regime_peak(agent, seed):
        env = Environment(10.0, 25.0, 300, 0.5, 700, seed)
        env.reset()
        errs = []
        for _ in range(700):
            p = agent.predict()
            o = env.step()
            errs.append(abs(o.observed_interval - p))
            agent.update(o.observed_interval)
        return float(max(errs[500:700]))

    seeds = range(8)
    guarded = [late_regime_peak(LearnedAgent(prior=1.0, anti_divergence=True), s) for s in seeds]
    unguarded = [
        late_regime_peak(LearnedAgent(prior=1.0, anti_divergence=False), s) for s in seeds
    ]
    assert float(np.median(guarded)) <= float(np.median(unguarded))


@pytest.mark.parametrize(
    ("kwargs", "msg"),
    [
        ({"base_gain": 0.0}, "base_gain"),
        ({"boost_gain": 0.0}, "boost_gain"),
        ({"boost_steps": -1}, "boost_steps"),
        ({"warmup": -1}, "warmup"),
        ({"min_gain_scale": 0.0}, "min_gain_scale"),
    ],
)
def test_learned_agent_rejects_invalid_hyperparameters(kwargs, msg):
    with pytest.raises(ValueError, match=msg):
        LearnedAgent(**kwargs)
