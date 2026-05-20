# SPDX-License-Identifier: MIT
import numpy as np

from ctios.agents import LearnedAgent
from ctios.env import Environment
from ctios.neural_agent import NeuralTemporalAgent


def _post_shift_mae(preds: np.ndarray, obs: np.ndarray, t_star: int) -> float:
    e = np.abs(obs - preds)
    return float(np.mean(e[t_star + 1 :]))


def test_neural_agent_scalar_baseline_comparison_is_finite():
    env = Environment(tau0=10.0, tau1=17.0, t_star=150, sigma=1.0, n_steps=300, seed=0)
    obs = np.asarray([env.step().observed_interval for _ in range(300)], dtype=float)

    n = NeuralTemporalAgent(seed=0)
    n_preds = np.asarray([d.prediction for d in n.run(obs)], dtype=float)

    l = LearnedAgent(prior=1.0)
    l_preds = []
    for x in obs:
        l_preds.append(float(l.predict()))
        l.update(float(x))
    l_preds = np.asarray(l_preds, dtype=float)

    n_mae = _post_shift_mae(n_preds, obs, env.t_star)
    l_mae = _post_shift_mae(l_preds, obs, env.t_star)
    assert np.isfinite(n_mae)
    assert np.isfinite(l_mae)
