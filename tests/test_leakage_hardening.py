"""Doctoral-critique §1.2.4 / §5 closure: order/structure leakage controls."""

import inspect

import numpy as np

from ctios import agents
from ctios.agents import LearnedAgent
from ctios.env import Environment


def test_no_agent_takes_n_steps_or_tstar():
    forbidden = {"n_steps", "t_star", "T_star", "n", "horizon"}
    for cls in (
        agents.LearnedAgent,
        agents.MovingAverageAgent,
        agents.ExpSmoothingAgent,
        agents.LastIntervalAgent,
    ):
        params = set(inspect.signature(cls.__init__).parameters)
        assert not (params & forbidden), f"{cls.__name__} leaks {params & forbidden}"


def test_env_hidden_provenance_is_hashed_not_raw():
    env = Environment(10.0, 17.0, 300, 1.0, 600, 0)
    prov = env.hidden_provenance()
    blob = "".join(prov.values())
    assert "10.0" not in blob and "17.0" not in blob and "300" not in blob
    assert all(len(h) == 64 for h in prov.values())  # sha256 hex


def _post_mae_on_series(intervals: np.ndarray, t_star: int) -> float:
    a = LearnedAgent(prior=1.0)
    ae = []
    for x in intervals:
        p = a.predict()
        ae.append(abs(x - p))
        a.update(float(x))
    return float(np.mean(ae[t_star : t_star + 250]))


def test_shuffling_post_shift_order_does_not_help():
    """Kill condition: if destroying temporal order IMPROVES the learner,
    it was faking adaptation via leakage/autocorrelation, not modelling time."""
    env = Environment(10.0, 17.0, 300, 1.0, 600, 0)
    env.reset()
    seq = np.array([env.step().observed_interval for _ in range(600)])
    m_real = _post_mae_on_series(seq, 300)
    sh = seq.copy()
    post = sh[300:].copy()
    np.random.default_rng(9999).shuffle(post)
    sh[300:] = post
    m_shuf = _post_mae_on_series(sh, 300)
    assert m_shuf >= m_real, f"shuffle improved learner ({m_shuf:.3f}<{m_real:.3f})"
