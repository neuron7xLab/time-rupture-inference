# SPDX-License-Identifier: MIT
"""Minimal deterministic runner for neural temporal adapter."""

from __future__ import annotations

import numpy as np

from ctios.learners.echo_state_learner import EchoStateLearner
from ctios.neural_agent import NeuralTemporalAdapter


def _validate_stream(stream: np.ndarray) -> np.ndarray:
    obs = np.asarray(stream, dtype=float)
    if obs.ndim != 1:
        raise ValueError("stream must be a 1D array")
    if obs.size == 0:
        raise ValueError("stream must be non-empty")
    if not np.isfinite(obs).all():
        raise ValueError("stream must contain only finite values")
    return obs


def run_neural_temporal_adapter(stream: np.ndarray, seed: int = 0, max_history: int = 256) -> dict[str, float | bool]:
    obs = _validate_stream(stream)
    if max_history < 1:
        raise ValueError("max_history must be >= 1")
    model = NeuralTemporalAdapter(seed=seed, max_history=max_history)
    baseline = EchoStateLearner(dim=32, seed=seed)
    preds = []
    errs = []
    uncs = []
    bpreds = []
    for x in obs:
        step = model.step(float(x))
        preds.append(step.prediction)
        errs.append(step.error)
        uncs.append(step.uncertainty)
        bpreds.append(baseline.predict())
        baseline.update(float(x))

    post = max(1, len(obs) // 2)
    post_slice = slice(post, len(obs))
    neural_mae = float(np.mean(np.abs(np.asarray(preds)[post_slice] - obs[post_slice])))
    scalar_mae = float(np.mean(np.abs(np.asarray(bpreds)[post_slice] - obs[post_slice])))
    return {
        "post_shift_mae": neural_mae,
        "scalar_baseline_post_shift_mae": scalar_mae,
        "neural_minus_scalar_mae": neural_mae - scalar_mae,
        "predictions_finite": bool(np.isfinite(preds).all()),
        "errors_finite": bool(np.isfinite(errs).all()),
        "uncertainty_finite": bool(np.isfinite(uncs).all()),
    }
