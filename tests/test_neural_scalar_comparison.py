# SPDX-License-Identifier: MIT
import numpy as np

from ctios.agents import LearnedAgent
from ctios.env import Environment
from ctios.neural_agent import NeuralTemporalAgent


def _post_shift_mae(preds: np.ndarray, obs: np.ndarray, t_star: int) -> float:
    errors = np.abs(obs - preds)
    return float(np.mean(errors[t_star + 1 :]))


def test_neural_agent_scalar_baseline_comparison_is_finite():
    env = Environment(
        tau0=10.0,
        tau1=17.0,
        t_star=150,
        sigma=1.0,
        n_steps=300,
        seed=0,
    )
    obs = np.asarray([env.step().observed_interval for _ in range(300)], dtype=float)

    neural = NeuralTemporalAgent(seed=0)
    neural_preds = np.asarray([d.prediction for d in neural.run(obs)], dtype=float)

    learned = LearnedAgent(prior=1.0)
    learned_preds = []
    for value in obs:
        learned_preds.append(float(learned.predict()))
        learned.update(float(value))
    learned_preds_array = np.asarray(learned_preds, dtype=float)

    neural_mae = _post_shift_mae(neural_preds, obs, env.t_star)
    learned_mae = _post_shift_mae(learned_preds_array, obs, env.t_star)
    assert np.isfinite(neural_mae)
    assert np.isfinite(learned_mae)
