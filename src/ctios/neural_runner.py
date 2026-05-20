# SPDX-License-Identifier: MIT
from __future__ import annotations

import numpy as np

from ctios.env import Environment
from ctios.neural_agent import NeuralTemporalAgent


def run_neural_demo(seed: int = 0, steps: int = 600, delta: float = 7.0) -> dict:
    env = Environment(tau0=10.0, tau1=10.0 + delta, t_star=max(1, steps // 2), sigma=1.0, n_steps=steps, seed=seed)
    obs = np.asarray([env.step().observed_interval for _ in range(steps)], dtype=float)
    agent = NeuralTemporalAgent(seed=seed)
    out = agent.run(obs)
    errs = np.asarray([d.error for d in out], dtype=float)
    post = errs[env.t_star + 1 :]
    return {
        "seed": seed,
        "steps": steps,
        "delta": delta,
        "post_shift_mae": float(np.mean(np.abs(post))),
        "uncertainty_final": float(out[-1].uncertainty),
    }
