# SPDX-License-Identifier: MIT
"""Executable NCTP prototype runtime for TASK-01..TASK-03.

This module provides a deterministic prototype slice:

- TASK-01: multi-horizon projection
- TASK-02: precision-weighted error
- TASK-03: adaptive state update under abrupt stream changes

It is intentionally nested under ``ctios.nctp_state`` until promotion. It does
not replace the canonical CTI-OS release gate or v9 neural path.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True)
class DriftStateUpdate:
    drift_score: list[list[float]]
    shift_label_hat: list[list[bool]]
    update_gain: list[list[float]]
    reset_probability: list[list[float]]
    state_adapted: list[list[float]]
    memory_priority: list[list[float]]


def _validate_btc(name: str, x: list[list[list[float]]]) -> tuple[int, int, int]:
    if not x or not x[0] or not x[0][0]:
        raise ValueError(f"{name} must be non-empty [B][T][C]")
    b = len(x)
    t = len(x[0])
    c = len(x[0][0])
    for bi in x:
        if len(bi) != t:
            raise ValueError(f"{name}: ragged T dimension")
        for ti in bi:
            if len(ti) != c:
                raise ValueError(f"{name}: ragged C dimension")
            if any(not math.isfinite(v) for v in ti):
                raise ValueError(f"{name}: non-finite value")
    return b, t, c


def _validate_bt(name: str, x: list[list[float]], b: int, t: int) -> None:
    if len(x) != b or any(len(row) != t for row in x):
        raise ValueError(f"{name} must match [B][T]")
    if any(not math.isfinite(v) for row in x for v in row):
        raise ValueError(f"{name}: non-finite value")


def _sigmoid(x: float) -> float:
    z = max(min(x, 40.0), -40.0)
    return 1.0 / (1.0 + math.exp(-z))


def _mean_abs(values: list[float]) -> float:
    return sum(abs(v) for v in values) / float(len(values))


def task01_multi_horizon_inference(
    x: list[list[list[float]]],
    dt: list[list[float]],
    horizons: list[int],
) -> dict[str, list[list[float]]]:
    """Prototype TASK-01.

    Uses a simple deterministic projection:

    ``y_hat(h) = last_observation + h * last_delta * mean_dt``
    """

    b, t, c = _validate_btc("x", x)
    _validate_bt("dt", dt, b, t)
    if t < 2:
        raise ValueError("x requires at least T>=2")
    if not horizons or any(h < 1 for h in horizons):
        raise ValueError("horizons must be positive")

    out: dict[str, list[list[float]]] = {}
    for h in horizons:
        rows: list[list[float]] = []
        for bi in range(b):
            mean_dt = sum(dt[bi]) / float(t)
            row: list[float] = []
            for ci in range(c):
                last_v = x[bi][t - 1][ci]
                delta = x[bi][t - 1][ci] - x[bi][t - 2][ci]
                row.append(last_v + float(h) * delta * mean_dt)
            rows.append(row)
        out[f"h{h}"] = rows
    return out


def task02_precision_weighted_error(
    y_hat: list[list[list[float]]],
    y_true: list[list[list[float]]],
    sigma: list[list[list[float]]],
    epsilon: float = 1e-6,
) -> dict[str, list[list[list[float]]]]:
    """Prototype TASK-02 with strict shape checks and safe precision."""

    b, h, y = _validate_btc("y_hat", y_hat)
    if _validate_btc("y_true", y_true) != (b, h, y):
        raise ValueError("y_true shape must match y_hat")
    if _validate_btc("sigma", sigma) != (b, h, y):
        raise ValueError("sigma shape must match y_hat")

    error: list[list[list[float]]] = []
    precision: list[list[list[float]]] = []
    weighted_error: list[list[list[float]]] = []
    confidence: list[list[list[float]]] = []

    for bi in range(b):
        e_b: list[list[float]] = []
        p_b: list[list[float]] = []
        we_b: list[list[float]] = []
        c_b: list[list[float]] = []
        for hi in range(h):
            e_h: list[float] = []
            p_h: list[float] = []
            we_h: list[float] = []
            c_h: list[float] = []
            for yi in range(y):
                err = y_true[bi][hi][yi] - y_hat[bi][hi][yi]
                s = max(sigma[bi][hi][yi], 0.0)
                prec = 1.0 / (s * s + epsilon)
                e_h.append(err)
                p_h.append(prec)
                we_h.append(prec * err)
                c_h.append(_sigmoid(-s))
            e_b.append(e_h)
            p_b.append(p_h)
            we_b.append(we_h)
            c_b.append(c_h)
        error.append(e_b)
        precision.append(p_b)
        weighted_error.append(we_b)
        confidence.append(c_b)

    return {
        "error": error,
        "precision": precision,
        "weighted_error": weighted_error,
        "confidence": confidence,
    }


def task03_drift_shift_inference(
    weighted_error: list[list[list[float]]],
    state_t: list[list[float]],
    state_prev: list[list[float]],
    sigma: list[list[list[float]]],
    dt: list[list[float]],
    memory_conflict: list[list[float]],
    threshold: float = 0.55,
) -> DriftStateUpdate:
    """TASK-03 adaptive state update.

    The function estimates a bounded drift score from weighted error magnitude,
    state delta, uncertainty, elapsed time, and memory conflict. It returns
    update gain, reset probability, memory priority, and an adapted state.

    This is a deterministic prototype, not a promoted scientific claim.
    """

    b, h, y = _validate_btc("weighted_error", weighted_error)
    if _validate_btc("sigma", sigma) != (b, h, y):
        raise ValueError("sigma shape must match weighted_error")
    if len(state_t) != b or len(state_prev) != b:
        raise ValueError("state_t/state_prev must match batch")
    state_dim = len(state_t[0])
    if state_dim == 0:
        raise ValueError("state vectors must be non-empty")
    for row in (*state_t, *state_prev):
        if len(row) != state_dim:
            raise ValueError("state vectors must have consistent dimension")
        if any(not math.isfinite(v) for v in row):
            raise ValueError("state vectors must be finite")
    _validate_bt("dt", dt, b, h)
    _validate_bt("memory_conflict", memory_conflict, b, h)

    drift_score: list[list[float]] = []
    shift_label_hat: list[list[bool]] = []
    update_gain: list[list[float]] = []
    reset_probability: list[list[float]] = []
    state_adapted: list[list[float]] = []
    memory_priority: list[list[float]] = []

    for bi in range(b):
        err_mag = sum(_mean_abs(weighted_error[bi][hi]) for hi in range(h)) / float(h)
        unc = sum(_mean_abs(sigma[bi][hi]) for hi in range(h)) / float(h)
        mean_dt = sum(dt[bi]) / float(h)
        mem = sum(memory_conflict[bi]) / float(h)
        state_delta = _mean_abs([state_t[bi][i] - state_prev[bi][i] for i in range(state_dim)])

        # Smooth bounded score. Large weighted error dominates, but state delta,
        # uncertainty, memory conflict, and dt all contribute.
        raw = 0.45 * err_mag + 0.25 * state_delta + 0.15 * unc + 0.10 * mem + 0.05 * mean_dt
        score = _sigmoid(raw - 1.0)
        gain = 0.05 + 0.90 * score
        reset = max(0.0, min(1.0, score * score))
        priority = max(0.0, min(1.0, 0.70 * score + 0.30 * mem))
        label = score >= threshold

        adapted_row: list[float] = []
        for i in range(state_dim):
            damped = (1.0 - reset) * state_t[bi][i]
            corrective = gain * (state_t[bi][i] - state_prev[bi][i])
            adapted_row.append(damped + corrective)

        drift_score.append([score])
        shift_label_hat.append([label])
        update_gain.append([gain])
        reset_probability.append([reset])
        memory_priority.append([priority])
        state_adapted.append(adapted_row)

    return DriftStateUpdate(
        drift_score=drift_score,
        shift_label_hat=shift_label_hat,
        update_gain=update_gain,
        reset_probability=reset_probability,
        state_adapted=state_adapted,
        memory_priority=memory_priority,
    )


def build_prototype_inference_packet(
    x: list[list[list[float]]],
    dt: list[list[float]],
    y_true: list[list[list[float]]],
    sigma: list[list[list[float]]],
    horizons: list[int],
) -> dict[str, Any]:
    """Build a validator-compatible packet using working TASK-01..TASK-03."""

    y_hat_by_h = task01_multi_horizon_inference(x=x, dt=dt, horizons=horizons)
    ordered = [f"h{h}" for h in horizons]
    b = len(x)
    y = len(x[0][0])
    y_hat_tensor = [[[0.0 for _ in range(y)] for _ in horizons] for _ in range(b)]
    for hi, key in enumerate(ordered):
        for bi in range(b):
            y_hat_tensor[bi][hi] = y_hat_by_h[key][bi]

    p2 = task02_precision_weighted_error(y_hat_tensor, y_true, sigma)
    state_prev = [row[-2] for row in x]
    state_t = [row[-1] for row in x]
    conflict = [[0.0 for _ in horizons] for _ in range(b)]
    p3 = task03_drift_shift_inference(
        weighted_error=p2["weighted_error"],
        state_t=state_t,
        state_prev=state_prev,
        sigma=sigma,
        dt=[[1.0 for _ in horizons] for _ in range(b)],
        memory_conflict=conflict,
    )

    return {
        "state": {"s_t": state_t, "s_prev": state_prev},
        "forecast": {"Y_hat": y_hat_by_h, "horizons": horizons},
        "precision_error": {
            "error": p2["error"],
            "precision": p2["precision"],
            "weighted_error": p2["weighted_error"],
        },
        "drift": {
            "drift_score": p3.drift_score,
            "shift_label_hat": p3.shift_label_hat,
            "update_gain": p3.update_gain,
            "reset_probability": p3.reset_probability,
            "state_adapted": p3.state_adapted,
            "memory_priority": p3.memory_priority,
        },
        "memory": {
            "retrieved_state": state_prev,
            "retrieval_weights": [[1.0] for _ in range(b)],
            "memory_conflict": conflict,
            "write_priority": p3.memory_priority,
        },
        "causal_delay": {
            "delay_distribution": [[1.0] + [0.0] * (len(horizons) - 1) for _ in range(b)],
            "causal_credit": [[0.0] * len(horizons) for _ in range(b)],
            "effect_prediction": y_hat_tensor,
        },
        "regime_extrapolation": {
            "regime_probs": [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0] for _ in range(b)],
            "future_regime_path": [[[1.0, 0.0, 0.0, 0.0, 0.0, 0.0] for _ in horizons] for _ in range(b)],
            "regime_change_time": [[0.0] for _ in range(b)],
            "extrapolated_state": y_hat_tensor,
        },
        "counterfactual": {
            "Y_real_hat": y_hat_tensor,
            "Y_counterfact_hat": y_hat_tensor,
            "counterfactual_delta": [[[0.0 for _ in range(y)] for _ in horizons] for _ in range(b)],
            "causal_effect_score": [[0.0 for _ in horizons] for _ in range(b)],
        },
    }
