# SPDX-License-Identifier: MIT
"""Per-channel MAE and the v8.2 gap hierarchy."""

from __future__ import annotations

import numpy as np


def channel_mae(
    pred: np.ndarray, obs: np.ndarray, masks: dict[str, np.ndarray]
) -> dict[str, float]:
    out: dict[str, float] = {"total": float(np.mean(np.abs(pred - obs)))}
    for name, m in masks.items():
        out[name] = float(np.mean(np.abs(pred[m] - obs[m]))) if m.any() else float("nan")
    return out


def gap_ratio(scalar_mae: float, history_mae: float) -> tuple[float, float]:
    gap = scalar_mae - history_mae
    ratio = gap / scalar_mae if scalar_mae > 0 else 0.0
    return gap, ratio


def history_to_regime_distance(history_mae: float, regime_mae: float) -> float:
    """Relative distance of history above the regime floor (0 = on floor)."""
    if regime_mae <= 0:
        return 0.0
    return (history_mae - regime_mae) / regime_mae
