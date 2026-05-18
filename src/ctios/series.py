# SPDX-License-Identifier: MIT
"""Shared numeric helpers for aligned 1-D series metrics.

Single source of the rolling-mean used by recovery detection — kills the
duplicate `_rolling`/`_rolling_mean` copies that previously lived in both
metrics.py and causal_metrics.py (the same single-source-of-truth class
already enforced for eval_horizon).
"""

from __future__ import annotations

import numpy as np


def rolling_mean_prefix(x: np.ndarray, w: int) -> np.ndarray:
    """Rolling mean with prefix semantics for the first (w-1) samples."""
    if w <= 0:
        raise ValueError(f"window size must be > 0, got {w}")
    if x.size == 0:
        return x
    w = min(w, x.size)
    c = np.cumsum(np.insert(x, 0, 0.0))
    out = (c[w:] - c[:-w]) / w
    head = np.array([np.mean(x[: i + 1]) for i in range(w - 1)])
    return np.concatenate([head, out])
