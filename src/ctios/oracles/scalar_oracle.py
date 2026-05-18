# SPDX-License-Identifier: MIT
"""Best scalar-only predictor. State is one scalar (running mean). It may
detect the trigger pattern from observations, but the jump SIGN depends
on hidden z (orthogonal to anything observable), so the optimal
scalar action at a trigger is to hedge to the mean. This is the honest
scalar upper bound — it cannot be beaten by any single-scalar state."""

from __future__ import annotations

import numpy as np


def predict_series(obs: np.ndarray, short_t: float, long_t: float, mu: float) -> np.ndarray:
    n = len(obs)
    preds = np.empty(n)
    run_sum = 0.0
    run_cnt = 0
    cats: list[int] = []
    for k in range(n):
        mean = run_sum / run_cnt if run_cnt else mu
        trigger = len(cats) >= 3 and cats[-3:] == [0, 0, 2]
        preds[k] = mu if trigger else mean  # sign unknowable from a scalar
        x = float(obs[k])
        run_sum += x
        run_cnt += 1
        cats.append(0 if x < short_t else (2 if x > long_t else 1))
    return preds
