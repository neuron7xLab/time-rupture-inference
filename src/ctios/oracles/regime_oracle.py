# SPDX-License-Identifier: MIT
"""Upper bound: predicts the noiseless expected interval (knows the
hidden context + trigger). Residual error is the irreducible sigma
noise floor — the information limit of the environment."""

from __future__ import annotations

import numpy as np


def predict_series(true_mean: np.ndarray) -> np.ndarray:
    return np.asarray(true_mean, dtype=float).copy()
