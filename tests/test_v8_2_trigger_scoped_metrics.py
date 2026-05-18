# SPDX-License-Identifier: MIT
"""Contract: channel MAE + gap helpers behave; NOT a verdict."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.trigger_scoped_metrics import (  # noqa: E402
    channel_mae,
    gap_ratio,
    history_to_regime_distance,
)


def test_channel_mae_partitions():
    obs = np.zeros(6)
    pred = np.array([1.0, 1.0, 0.0, 0.0, 2.0, 2.0])
    masks = {
        "trigger": np.array([1, 1, 0, 0, 0, 0], dtype=bool),
        "carrier": np.array([0, 0, 1, 1, 0, 0], dtype=bool),
        "background": np.array([0, 0, 0, 0, 1, 1], dtype=bool),
    }
    r = channel_mae(pred, obs, masks)
    assert r["trigger"] == 1.0 and r["carrier"] == 0.0 and r["background"] == 2.0
    assert abs(r["total"] - 1.0) < 1e-9


def test_gap_ratio_and_distance():
    g, ratio = gap_ratio(2.0, 0.5)
    assert g == 1.5 and abs(ratio - 0.75) < 1e-9
    assert abs(history_to_regime_distance(1.0, 0.5) - 1.0) < 1e-9
    assert history_to_regime_distance(0.5, 0.0) == 0.0
