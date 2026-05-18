# SPDX-License-Identifier: MIT
"""Correctly-specified causal history oracle (v8.3).

Bayes-optimal for a sign that is piecewise-constant with one hidden
flip: the current-sign estimate is the MOST RECENT observed post-trigger
sign. No access to z / future / schedule / trigger labels — trigger
detectability is exactly the scalar's (the (short,short,long) observed
window). This is the causal optimum for the sign channel; it cannot beat
the analytic causal lower bound (one hidden flip + cold prior force
unavoidable errors).
"""

from __future__ import annotations

import numpy as np


def _cat(x: float, st: float, lt: float) -> int:
    return 0 if x < st else (2 if x > lt else 1)


def predict_series(
    obs: np.ndarray, st: float, lt: float, mu: float, delta: float
) -> tuple[np.ndarray, np.ndarray]:
    n = len(obs)
    pred = np.empty(n)
    inferred = np.zeros(n, dtype=int)
    cats: list[int] = []
    run_sum = 0.0
    run_cnt = 0
    last_sign = 1            # cold prior (its error is part of the bound)
    for k in range(n):
        mean = run_sum / run_cnt if run_cnt else mu
        trig = len(cats) >= 3 and cats[-3:] == [0, 0, 2]
        if trig:
            pred[k] = mu + last_sign * delta
            inferred[k] = last_sign
        else:
            pred[k] = mean
        x = float(obs[k])
        if trig:
            # Bayes-optimal update: the realized post-trigger deviation
            # is a near-noiseless sign read (delta >> sigma). Lock to it.
            last_sign = 1 if (x - mu) >= 0.0 else -1
        run_sum += x
        run_cnt += 1
        cats.append(_cat(x, st, lt))
    return pred, inferred
