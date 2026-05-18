# SPDX-License-Identifier: MIT
"""History-based predictor. No access to hidden z. It infers the current
context sign from the most recent OBSERVED post-trigger deviation
(sign(obs_at_trigger - mu)) and reuses it at the next trigger. Correct
except a single-trigger transient after the hidden z-flip — which is
exactly the disambiguation a scalar cannot do."""

from __future__ import annotations

import numpy as np


def predict_series(
    obs: np.ndarray, short_t: float, long_t: float, mu: float, delta: float
) -> tuple[np.ndarray, np.ndarray]:
    n = len(obs)
    preds = np.empty(n)
    inferred_sign = np.zeros(n, dtype=int)
    run_sum = 0.0
    run_cnt = 0
    cats: list[int] = []
    last_sign = 1  # prior; corrected after the first observed trigger
    for k in range(n):
        mean = run_sum / run_cnt if run_cnt else mu
        trigger = len(cats) >= 3 and cats[-3:] == [0, 0, 2]
        preds[k] = mu + last_sign * delta if trigger else mean
        inferred_sign[k] = last_sign if trigger else 0
        x = float(obs[k])
        if trigger:  # observe realized deviation -> update context belief
            last_sign = 1 if (x - mu) >= 0 else -1
        run_sum += x
        run_cnt += 1
        cats.append(0 if x < short_t else (2 if x > long_t else 1))
    return preds, inferred_sign
