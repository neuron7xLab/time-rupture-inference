# SPDX-License-Identifier: MIT
"""v8.1 latent-context rupture — Construction B (generator-guaranteed
alias schedule).

The v8 parent RED proved that a *rare* trigger makes latent structure
decorative. v8.1 removes the chance: at every `period` steps a 4-step
block is FORCED to the observable window (short, short, long, SHIFTED).
The first three steps are distributionally identical across both hidden
contexts z ∈ {A, B}; only the 4th (the trigger) is shifted by
sign(z)·delta. z is hidden and flips once at n//2. Same observable
window, opposite future, at exact non-negligible frequency — by
construction, quantified before any run. No model is trained here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class LatentContextRunV81:
    obs: np.ndarray
    is_trigger: np.ndarray
    z_sign: np.ndarray
    true_mean: np.ndarray
    t_z: int


def generate(seed: int, cfg: dict[str, Any]) -> LatentContextRunV81:
    rng = np.random.default_rng(seed)
    mu = float(cfg["mu"])
    sigma = float(cfg["sigma"])
    delta = float(cfg["delta"])
    n = int(cfg["n_steps"])
    period = int(cfg["period"])
    short_lo = float(cfg["short_thresh"]) - 1.0   # forced clearly-short value
    long_hi = float(cfg["long_thresh"]) + 1.0     # forced clearly-long value
    t_z = n // 2
    z0 = 1 if rng.integers(0, 2) == 0 else -1

    obs = np.empty(n)
    is_trig = np.zeros(n, dtype=bool)
    z_sign = np.empty(n, dtype=int)
    true_mean = np.empty(n)

    for k in range(n):
        z = z0 if k < t_z else -z0
        z_sign[k] = z
        slot = k % period
        if slot == 0:        # forced "short"
            base = short_lo
        elif slot == 1:      # forced "short"
            base = short_lo
        elif slot == 2:      # forced "long"
            base = long_hi
        elif slot == 3:      # TRIGGER: aliased window -> z-dependent future
            base = mu + z * delta
            is_trig[k] = True
        else:                # neutral filler ~ Normal(mu, sigma)
            base = mu
        true_mean[k] = base
        obs[k] = base + rng.normal(0.0, sigma)
    return LatentContextRunV81(obs, is_trig, z_sign, true_mean, t_z)
