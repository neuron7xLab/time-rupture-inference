# SPDX-License-Identifier: MIT
"""Carrier vs trigger-context vs background decomposition (v8.2).

The v8.1 carrier (short,short,long,mid...) is deterministic and fully
observable, so a fair carrier model uses ONLY observation-derived phase
(steps since the last observed short,short,long marker) — never z,
future, or the schedule period. Removing this scalar-accessible carrier
isolates the z-dependent trigger channel a scalar still cannot sign.
"""

from __future__ import annotations

import numpy as np


def channel_masks(
    obs: np.ndarray, is_trigger: np.ndarray, period: int
) -> dict[str, np.ndarray]:
    n = len(obs)
    k = np.arange(n)
    slot = k % period
    trigger = is_trigger.astype(bool)
    carrier = np.isin(slot, (0, 1, 2)) & ~trigger
    background = ~trigger & ~carrier
    return {"trigger": trigger, "carrier": carrier, "background": background}


def _cat(x: float, st: float, lt: float) -> int:
    return 0 if x < st else (2 if x > lt else 1)


def carrier_aware_predictions(
    obs: np.ndarray, st: float, lt: float, mu: float, delta: float
) -> tuple[np.ndarray, np.ndarray]:
    """Phase-conditional carrier model (obs-only) + the z channel.

    Returns (scalar_carrier_pred, history_carrier_pred). Both use the
    same observation-derived phase mean; they differ ONLY at a detected
    trigger: scalar must hedge to mu (sign unknowable from a scalar),
    history reuses the last observed post-trigger sign.
    """
    n = len(obs)
    sp = np.empty(n)
    hp = np.empty(n)
    cats: list[int] = []
    phase = 0
    psum: dict[int, float] = {}
    pcnt: dict[int, int] = {}
    g_sum = 0.0
    g_cnt = 0
    last_sign = 1
    for k in range(n):
        trig = len(cats) >= 3 and cats[-3:] == [0, 0, 2]
        ph_mean = psum[phase] / pcnt[phase] if pcnt.get(phase) else (
            g_sum / g_cnt if g_cnt else mu
        )
        if trig:
            sp[k] = mu                       # carrier removed; sign unknowable
            hp[k] = mu + last_sign * delta   # history signs the residual
        else:
            sp[k] = ph_mean
            hp[k] = ph_mean
        x = float(obs[k])
        if trig:
            last_sign = 1 if (x - mu) >= 0 else -1
            phase = 0
        else:
            phase += 1
        psum[phase] = psum.get(phase, 0.0) + x
        pcnt[phase] = pcnt.get(phase, 0) + 1
        g_sum += x
        g_cnt += 1
        cats.append(_cat(x, st, lt))
    return sp, hp
