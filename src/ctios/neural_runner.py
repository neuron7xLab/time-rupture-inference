# SPDX-License-Identifier: MIT
from __future__ import annotations

import numpy as np

from ctios.env import TemporalEnv
from ctios.neural_agent import NeuralTemporalAgent


def run_neural_demo(seed: int = 0, steps: int = 600, delta: float = 7.0) -> dict:
    env = TemporalEnv(seed=seed, delta=delta)
    s = env.sample(steps=steps)
    agent = NeuralTemporalAgent(seed=seed)
    out = agent.run(np.asarray(s.x, dtype=float))
    errs = np.asarray([d.error for d in out], dtype=float)
    post = errs[s.t_star + 1 :]
    return {
        "seed": seed,
        "steps": steps,
        "delta": delta,
        "post_shift_mae": float(np.mean(np.abs(post))),
        "uncertainty_final": float(out[-1].uncertainty),
    }
