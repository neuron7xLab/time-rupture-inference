# SPDX-License-Identifier: MIT
"""Executable NCTP-1 runtime prototypes with structured contracts.

This module focuses on deterministic, fail-closed prototypes for TASK-01..04,
plus assembly of a validator-compatible inference packet.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import cast


@dataclass(frozen=True)
class RuntimeInputs:
    x: list[list[list[float]]]
    dt: list[list[float]]
    y_true: list[list[list[float]]]
    sigma: list[list[list[float]]]
    horizons: list[int]


@dataclass(frozen=True)
class DriftConfig:
    threshold: float = 0.5
    energy_weight: float = 1.0
    uncertainty_weight: float = 1.0
    ema_decay: float = 0.8


def _validate_finite_scalar(name: str, value: object) -> None:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{name} must be a finite numeric scalar")


def _validate_btc(name: str, x: list[list[list[float]]]) -> tuple[int, int, int]:
    if not x or not x[0] or not x[0][0]:
        raise ValueError(f"{name} must be non-empty [B][T][C]")
    b, t, c = len(x), len(x[0]), len(x[0][0])
    for bi in x:
        if len(bi) != t:
            raise ValueError(f"{name}: ragged T dimension")
        for ti in bi:
            if len(ti) != c:
                raise ValueError(f"{name}: ragged C dimension")
            for vi, v in enumerate(ti):
                _validate_finite_scalar(f"{name}[*][*][{vi}]", v)
    return b, t, c


def _validate_bt(name: str, x: list[list[float]], b: int, t: int) -> None:
    if len(x) != b or any(len(row) != t for row in x):
        raise ValueError(f"{name} must match [B][T]")
    for r, row in enumerate(x):
        for c, v in enumerate(row):
            _validate_finite_scalar(f"{name}[{r}][{c}]", v)


def _validate_horizons(horizons: list[int]) -> None:
    if not horizons:
        raise ValueError("horizons must be non-empty")
    if any(h <= 0 for h in horizons):
        raise ValueError("horizons must be positive integers")


def _ema(values: list[float], decay: float) -> float:
    ema = values[0]
    for v in values[1:]:
        ema = decay * ema + (1.0 - decay) * v
    return ema


def task01_multi_horizon_inference(
    x: list[list[list[float]]],
    dt: list[list[float]],
    horizons: list[int],
) -> dict[str, list[list[float]]]:
    b, t, c = _validate_btc("x", x)
    _validate_bt("dt", dt, b, t)
    _validate_horizons(horizons)
    if t < 2:
        raise ValueError("x requires at least T>=2 for delta projection")

    out: dict[str, list[list[float]]] = {}
    for h in horizons:
        key = f"h{h}"
        preds: list[list[float]] = []
        for bi in range(b):
            mean_dt = sum(dt[bi]) / float(t)
            row = [x[bi][t - 1][ci] + float(h) * (x[bi][t - 1][ci] - x[bi][t - 2][ci]) * mean_dt for ci in range(c)]
            preds.append(row)
        out[key] = preds
    return out


def task02_precision_weighted_error(
    y_hat: list[list[list[float]]],
    y_true: list[list[list[float]]],
    sigma: list[list[list[float]]],
    epsilon: float = 1e-6,
) -> dict[str, list[list[list[float]]]]:
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
                e = y_true[bi][hi][yi] - y_hat[bi][hi][yi]
                s = max(sigma[bi][hi][yi], 0.0)
                p = 1.0 / (s * s + epsilon)
                e_h.append(e)
                p_h.append(p)
                we_h.append(p * e)
                c_h.append(1.0 / (1.0 + math.exp(s)))
            e_b.append(e_h)
            p_b.append(p_h)
            we_b.append(we_h)
            c_b.append(c_h)
        error.append(e_b)
        precision.append(p_b)
        weighted_error.append(we_b)
        confidence.append(c_b)
    return {"error": error, "precision": precision, "weighted_error": weighted_error, "confidence": confidence}


def task03_drift_rupture_inference(
    weighted_error: list[list[list[float]]],
    sigma: list[list[list[float]]],
    config: DriftConfig = DriftConfig(),
) -> dict[str, list[list[float]] | list[list[bool]]]:
    b, h, y = _validate_btc("weighted_error", weighted_error)
    if _validate_btc("sigma", sigma) != (b, h, y):
        raise ValueError("sigma shape must match weighted_error")
    if not (0.0 <= config.ema_decay < 1.0):
        raise ValueError("ema_decay must be in [0, 1)")

    drift_score: list[list[float]] = []
    rupture: list[list[bool]] = []
    gain: list[list[float]] = []
    reset: list[list[float]] = []
    mem_prio: list[list[float]] = []
    for bi in range(b):
        # flatten per-horizon energies
        energies = [weighted_error[bi][hi][yi] ** 2 for hi in range(h) for yi in range(y)]
        uncs = [sigma[bi][hi][yi] for hi in range(h) for yi in range(y)]
        energy_ema = _ema(energies, config.ema_decay)
        uncertainty_ema = _ema(uncs, config.ema_decay)
        z = config.energy_weight * energy_ema - config.uncertainty_weight * uncertainty_ema
        score = 1.0 / (1.0 + math.exp(-z))
        drift_score.append([score])
        rupture.append([score > config.threshold])
        gain.append([score])
        reset.append([min(max(score * 0.5, 0.0), 1.0)])
        mem_prio.append([score])
    return {
        "drift_score": drift_score,
        "rupture_label_hat": rupture,
        "update_gain": gain,
        "reset_probability": reset,
        "memory_priority": mem_prio,
    }


def task04_causal_delay_inference(
    state_t: list[list[float]],
    horizons: list[int],
) -> dict[str, list[list[float]] | list[list[list[float]]]]:
    if not state_t or not state_t[0]:
        raise ValueError("state_t must be non-empty [B][D]")
    _validate_horizons(horizons)
    b, d = len(state_t), len(state_t[0])
    for row in state_t:
        if len(row) != d:
            raise ValueError("state_t ragged D dimension")

    delay: list[list[float]] = []
    credit: list[list[float]] = []
    effects: list[list[list[float]]] = []
    for bi in range(b):
        inv = [1.0 / float(h) for h in horizons]
        norm = sum(inv)
        probs = [v / norm for v in inv]
        delay.append(probs)
        state_strength = min(max(abs(sum(state_t[bi])) / (d * 10.0), 0.0), 1.0)
        credit.append([state_strength] * len(horizons))
        effects.append([[state_t[bi][j % d] * probs[hi] for j in range(d)] for hi in range(len(horizons))])
    return {"delay_distribution": delay, "causal_credit": credit, "effect_prediction": effects}


def _pack_memory_section(state_last: list[list[float]], memory_priority: list[list[float]]) -> dict[str, object]:
    b = len(state_last)
    retrieval = [[1.0] for _ in range(b)]
    return {
        "retrieved_state": state_last,
        "retrieval_weights": retrieval,
        "memory_conflict": [[0.0] for _ in range(b)],
        "write_priority": memory_priority,
    }


def build_prototype_inference_packet(inputs: RuntimeInputs) -> dict[str, object]:
    y_hat_by_h = task01_multi_horizon_inference(inputs.x, inputs.dt, inputs.horizons)

    ordered_h_keys = [f"h{h}" for h in inputs.horizons]
    b = len(inputs.x)
    y = len(inputs.x[0][0])
    y_hat_tensor = [[[0.0 for _ in range(y)] for _ in inputs.horizons] for _ in range(b)]
    for hi, hk in enumerate(ordered_h_keys):
        for bi in range(b):
            y_hat_tensor[bi][hi] = y_hat_by_h[hk][bi]

    p2 = task02_precision_weighted_error(y_hat_tensor, inputs.y_true, inputs.sigma)
    p3 = task03_drift_rupture_inference(p2["weighted_error"], inputs.sigma)
    memory_priority = cast(list[list[float]], p3["memory_priority"])
    state_last = [row[-1] for row in inputs.x]
    p4 = task04_causal_delay_inference(state_last, inputs.horizons)

    return {
        "state": {"s_t": state_last},
        "forecast": {"Y_hat": y_hat_by_h, "horizons": inputs.horizons},
        "precision_error": {"error": p2["error"], "precision": p2["precision"], "weighted_error": p2["weighted_error"]},
        "drift": {
            "drift_score": p3["drift_score"],
            "rupture_label_hat": p3["rupture_label_hat"],
            "update_gain": p3["update_gain"],
            "reset_probability": p3["reset_probability"],
        },
        "memory": _pack_memory_section(state_last, memory_priority),
        "causal_delay": {
            "delay_distribution": p4["delay_distribution"],
            "causal_credit": p4["causal_credit"],
            "effect_prediction": p4["effect_prediction"],
        },
        "regime_extrapolation": {
            "regime_probs": [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0] for _ in range(b)],
            "future_regime_path": [[[1.0, 0.0, 0.0, 0.0, 0.0, 0.0] for _ in inputs.horizons] for _ in range(b)],
            "regime_change_time": [[0.0] for _ in range(b)],
            "extrapolated_state": y_hat_tensor,
        },
        "counterfactual": {
            "Y_real_hat": y_hat_tensor,
            "Y_counterfact_hat": y_hat_tensor,
            "counterfactual_delta": [[[0.0 for _ in range(y)] for _ in inputs.horizons] for _ in range(b)],
            "causal_effect_score": [[0.0 for _ in inputs.horizons] for _ in range(b)],
            "status": "stub",
        },
        "runtime_boundary": {
            "task05_memory": "stub",
            "task06_regime": "stub",
            "task07_counterfactual": "stub",
        },
    }
