# SPDX-License-Identifier: MIT
"""Runner helpers for the experimental attention adapter."""

from __future__ import annotations

import numpy as np

from ctios.experimental.neural_attention_adapter import NeuralAttentionAdapter
from ctios.learners.echo_state_learner import EchoStateLearner


def validate_stream(stream: np.ndarray) -> np.ndarray:
    obs = np.asarray(stream, dtype=float)
    if obs.ndim != 1:
        raise ValueError("stream must be a 1D array")
    if obs.size == 0:
        raise ValueError("stream must be non-empty")
    if not np.isfinite(obs).all():
        raise ValueError("stream must contain only finite values")
    return obs


def run_neural_attention_adapter(
    stream: np.ndarray,
    seed: int = 0,
    max_history: int = 256,
) -> dict[str, float | bool]:
    obs = validate_stream(stream)
    if max_history < 1:
        raise ValueError("max_history must be >= 1")

    model = NeuralAttentionAdapter(seed=seed, max_history=max_history)
    baseline = EchoStateLearner(dim=32, seed=seed)
    preds: list[float] = []
    errors: list[float] = []
    uncertainties: list[float] = []
    baseline_preds: list[float] = []

    for x in obs:
        step = model.step(float(x))
        preds.append(step.prediction)
        errors.append(step.error)
        uncertainties.append(step.uncertainty)
        baseline_preds.append(float(baseline.predict()))
        baseline.update(float(x))

    post = max(1, len(obs) // 2)
    post_slice = slice(post, len(obs))
    pred_arr = np.asarray(preds, dtype=float)
    baseline_arr = np.asarray(baseline_preds, dtype=float)
    error_arr = np.asarray(errors, dtype=float)
    unc_arr = np.asarray(uncertainties, dtype=float)
    neural_mae = float(np.mean(np.abs(pred_arr[post_slice] - obs[post_slice])))
    scalar_mae = float(np.mean(np.abs(baseline_arr[post_slice] - obs[post_slice])))
    mean_uncertainty = float(np.mean(unc_arr))
    return {
        "post_shift_mae": neural_mae,
        "scalar_baseline_post_shift_mae": scalar_mae,
        "neural_minus_scalar_mae": neural_mae - scalar_mae,
        "predictions_finite": bool(np.isfinite(pred_arr).all()),
        "errors_finite": bool(np.isfinite(error_arr).all()),
        "uncertainty_finite": bool(np.isfinite(unc_arr).all()),
        "mean_uncertainty": mean_uncertainty,
        "uncertainty_calibration_ratio": float(neural_mae / (mean_uncertainty + 1e-12)),
    }
