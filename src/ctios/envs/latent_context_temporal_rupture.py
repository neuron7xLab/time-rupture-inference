# SPDX-License-Identifier: MIT
"""Latent-context temporal-rupture environment (v8).

Scalar-inexpressible by construction: outside triggers both contexts
emit the same Normal(mu, sigma); the (short, short, long) window is
identical across contexts, yet the step right after it is shifted by
sign(z)*delta with z hidden and flipped once mid-run. Identical recent
observation, opposite correct future — a single scalar cannot resolve
it; only history can. No model is trained here; only oracles read it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class LatentContextRun:
    obs: np.ndarray          # observed intervals (the only public signal)
    is_trigger: np.ndarray   # bool: this step received the signed jump
    z_sign: np.ndarray       # +1 (context A) / -1 (context B), HIDDEN
    true_mean: np.ndarray    # noiseless expected interval (regime oracle)
    t_z: int                 # hidden context-flip step


def _cat(x: float, short_t: float, long_t: float) -> int:
    return 0 if x < short_t else (2 if x > long_t else 1)  # short/mid/long


def generate(seed: int, cfg: dict[str, Any]) -> LatentContextRun:
    rng = np.random.default_rng(seed)
    mu = float(cfg["mu"])
    sigma = float(cfg["sigma"])
    delta = float(cfg["delta"])
    n = int(cfg["n_steps"])
    short_t = float(cfg["short_thresh"])
    long_t = float(cfg["long_thresh"])
    t_z = n // 2
    z0 = 1 if rng.integers(0, 2) == 0 else -1

    obs = np.empty(n)
    is_trig = np.zeros(n, dtype=bool)
    z_sign = np.empty(n, dtype=int)
    true_mean = np.empty(n)
    cats: list[int] = []
    for k in range(n):
        z = z0 if k < t_z else -z0
        z_sign[k] = z
        trigger = len(cats) >= 3 and cats[-3:] == [0, 0, 2]
        shift = z * delta if trigger else 0.0
        true_mean[k] = mu + shift
        obs[k] = mu + shift + rng.normal(0.0, sigma)
        is_trig[k] = trigger
        cats.append(_cat(obs[k], short_t, long_t))
    return LatentContextRun(obs, is_trig, z_sign, true_mean, t_z)
