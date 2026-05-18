# SPDX-License-Identifier: MIT
"""v8.4 latent-context rupture — env re-derived from first principles.

Same Construction-B alias schedule as v8.1, with two principled
corrections proven before the run (see the v8.4 pre-registration):
  * the forced marker is set `marker_sep` (≥3σ) clear of the
    categorization thresholds so trigger DETECTION is essentially
    deterministic (kills the v8.3 empirical≫analytic gap);
  * `n_steps`/`period` are sized so the single unavoidable post-flip
    error amortizes below the (unchanged) h2r gate.
No model is trained here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class LatentContextRunV84:
    obs: np.ndarray
    is_trigger: np.ndarray
    z_sign: np.ndarray
    true_mean: np.ndarray
    t_z: int


def generate(seed: int, cfg: dict[str, Any]) -> LatentContextRunV84:
    rng = np.random.default_rng(seed)
    mu = float(cfg["mu"])
    sigma = float(cfg["sigma"])
    delta = float(cfg["delta"])
    n = int(cfg["n_steps"])
    period = int(cfg["period"])
    sep = float(cfg["marker_sep"])
    short_v = mu - sep        # clearly below short_thresh
    long_v = mu + sep         # clearly above long_thresh
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
        if slot in (0, 1):
            base = short_v
        elif slot == 2:
            base = long_v
        elif slot == 3:
            base = mu + z * delta
            is_trig[k] = True
        else:
            base = mu
        true_mean[k] = base
        obs[k] = base + rng.normal(0.0, sigma)
    return LatentContextRunV84(obs, is_trig, z_sign, true_mean, t_z)
