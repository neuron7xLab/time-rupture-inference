import numpy as np

from ctios.agents import InjectedAgent, LearnedAgent, OracleAgent
from ctios.env import Environment


def _post_mae(agent, env, n, t_star):
    env.reset()
    errs = []
    for k in range(n):
        p = agent.predict()
        o = env.step()
        errs.append(abs(o.observed_interval - p))
        agent.update(o.observed_interval)
    return float(np.mean(errs[t_star : t_star + 250]))


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
