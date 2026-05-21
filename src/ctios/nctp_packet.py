# SPDX-License-Identifier: MIT
"""NCTP-1 inference packet contract.

Strict, fail-closed schema and numeric guards for deterministic provenance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class NCTPTaskSpec:
    task_id: str
    name: str
    required_outputs: tuple[str, ...]


TASK_SPECS: tuple[NCTPTaskSpec, ...] = (
    NCTPTaskSpec("TASK-01", "multi_horizon_temporal_inference", ("Y_hat",)),
    NCTPTaskSpec(
        "TASK-02",
        "precision_weighted_error_inference",
        ("error", "precision", "weighted_error"),
    ),
    NCTPTaskSpec(
        "TASK-03",
        "drift_rupture_inference",
        ("drift_score", "rupture_label_hat", "update_gain", "reset_probability"),
    ),
    NCTPTaskSpec(
        "TASK-04",
        "causal_delay_inference",
        ("delay_distribution", "causal_credit", "effect_prediction"),
    ),
    NCTPTaskSpec(
        "TASK-05",
        "episodic_memory_retrieval_inference",
        ("retrieved_state", "retrieval_weights", "memory_conflict", "write_priority"),
    ),
    NCTPTaskSpec(
        "TASK-06",
        "regime_extrapolation",
        ("regime_probs", "future_regime_path", "regime_change_time", "extrapolated_state"),
    ),
    NCTPTaskSpec(
        "TASK-07",
        "counterfactual_temporal_extrapolation",
        (
            "Y_real_hat",
            "Y_counterfact_hat",
            "counterfactual_delta",
            "causal_effect_score",
        ),
    ),
)


SECTION_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "state": ("s_t",),
    "forecast": ("Y_hat", "horizons"),
    "precision_error": ("error", "precision", "weighted_error"),
    "drift": ("drift_score", "rupture_label_hat", "update_gain", "reset_probability"),
    "memory": ("retrieved_state", "retrieval_weights", "memory_conflict", "write_priority"),
    "causal_delay": ("delay_distribution", "causal_credit", "effect_prediction"),
    "regime_extrapolation": (
        "regime_probs",
        "future_regime_path",
        "regime_change_time",
        "extrapolated_state",
    ),
    "counterfactual": (
        "Y_real_hat",
        "Y_counterfact_hat",
        "counterfactual_delta",
        "causal_effect_score",
        "status",
    ),
    "runtime_boundary": ("task05_memory", "task06_regime", "task07_counterfactual"),
}


def _finite_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        numeric = float(value)
        if math.isfinite(numeric):
            return numeric
    return None


def _is_finite_number(value: object) -> bool:
    return _finite_float(value) is not None


def _same_shape(left: object, right: object) -> bool:
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            _same_shape(a, b) for a, b in zip(left, right, strict=True)
        )
    return not isinstance(left, list) and not isinstance(right, list)


def _delta_matches(
    y_counterfactual: object,
    y_real: object,
    delta: object,
    tol: float = 1e-9,
) -> bool:
    if isinstance(y_counterfactual, list) and isinstance(y_real, list) and isinstance(delta, list):
        return len(y_counterfactual) == len(y_real) == len(delta) and all(
            _delta_matches(a, b, c, tol)
            for a, b, c in zip(y_counterfactual, y_real, delta, strict=True)
        )
    y_counterfactual_value = _finite_float(y_counterfactual)
    y_real_value = _finite_float(y_real)
    delta_value = _finite_float(delta)
    if y_counterfactual_value is None or y_real_value is None or delta_value is None:
        return False
    return abs((y_counterfactual_value - y_real_value) - delta_value) <= tol


def validate_inference_packet(packet: dict[str, object]) -> list[str]:
    errors: list[str] = []
    expected_top = set(SECTION_REQUIREMENTS)

    packet_keys = set(packet)
    missing_top = sorted(expected_top - packet_keys)
    if missing_top:
        errors.append(f"missing top-level keys: {', '.join(missing_top)}")
    unknown_top = sorted(packet_keys - expected_top)
    if unknown_top:
        errors.append(f"unknown top-level keys: {', '.join(unknown_top)}")

    for section, required in SECTION_REQUIREMENTS.items():
        value = packet.get(section)
        if not isinstance(value, dict):
            errors.append(f"section '{section}' must be a dict")
            continue
        missing = [key for key in required if key not in value]
        if missing:
            errors.append(f"section '{section}' missing keys: {', '.join(missing)}")
        unknown = sorted(set(value) - set(required))
        if unknown:
            errors.append(f"section '{section}' has unknown keys: {', '.join(unknown)}")

    _validate_forecast(packet, errors)
    _validate_drift(packet, errors)
    _validate_causal_delay(packet, errors)
    _validate_counterfactual(packet, errors)
    _validate_runtime_boundary(packet, errors)

    return errors


def _validate_forecast(packet: dict[str, object], errors: list[str]) -> None:
    forecast = packet.get("forecast")
    if isinstance(forecast, dict):
        horizons = forecast.get("horizons")
        if not isinstance(horizons, list) or not horizons:
            errors.append("forecast.horizons must be a non-empty list")
        elif any((not isinstance(h, int)) or h <= 0 for h in horizons):
            errors.append("forecast.horizons must contain only positive integers")


def _validate_drift(packet: dict[str, object], errors: list[str]) -> None:
    drift = packet.get("drift")
    if isinstance(drift, dict):
        drift_score = drift.get("drift_score")
        if isinstance(drift_score, list):
            vals = [v for row in drift_score if isinstance(row, list) for v in row]
            if any(not _is_finite_number(v) for v in vals):
                errors.append("drift.drift_score must contain finite numeric values")


def _validate_causal_delay(packet: dict[str, object], errors: list[str]) -> None:
    causal_delay = packet.get("causal_delay")
    if not isinstance(causal_delay, dict):
        return
    delay_distribution = causal_delay.get("delay_distribution")
    if not isinstance(delay_distribution, list):
        return
    for row in delay_distribution:
        if not isinstance(row, list) or not row:
            continue
        numeric_row = [_finite_float(value) for value in row]
        if any(value is None for value in numeric_row):
            errors.append("causal_delay.delay_distribution must be finite")
            continue
        total = sum(value for value in numeric_row if value is not None)
        if abs(total - 1.0) > 1e-6:
            errors.append("causal_delay.delay_distribution rows must be normalized")


def _validate_counterfactual(packet: dict[str, object], errors: list[str]) -> None:
    counterfactual = packet.get("counterfactual")
    if not isinstance(counterfactual, dict):
        return
    status = counterfactual.get("status")
    y_real = counterfactual.get("Y_real_hat")
    y_counterfactual = counterfactual.get("Y_counterfact_hat")
    delta = counterfactual.get("counterfactual_delta")
    if status != "stub" and not _delta_matches(y_counterfactual, y_real, delta):
        errors.append(
            "counterfactual.counterfactual_delta must match "
            "Y_counterfact_hat - Y_real_hat or set status=stub"
        )


def _validate_runtime_boundary(packet: dict[str, object], errors: list[str]) -> None:
    runtime_boundary = packet.get("runtime_boundary")
    if not isinstance(runtime_boundary, dict):
        return
    values = [
        runtime_boundary.get("task05_memory"),
        runtime_boundary.get("task06_regime"),
        runtime_boundary.get("task07_counterfactual"),
    ]
    if any(value != "stub" for value in values):
        errors.append("runtime_boundary TASK-05..07 must be declared as stub")
