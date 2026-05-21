# SPDX-License-Identifier: MIT
"""NCTP inference packet contract.

The validator is intentionally small and strict: missing sections fail before
reporting, storage, or later promotion work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
        "drift_shift_inference",
        (
            "drift_score",
            "shift_label_hat",
            "update_gain",
            "reset_probability",
            "state_adapted",
            "memory_priority",
        ),
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
        ("Y_real_hat", "Y_counterfact_hat", "counterfactual_delta", "causal_effect_score"),
    ),
)


def validate_inference_packet(packet: dict[str, Any]) -> list[str]:
    """Return deterministic validation errors for an NCTP packet."""

    errors: list[str] = []
    expected_top = {
        "state",
        "forecast",
        "precision_error",
        "drift",
        "memory",
        "causal_delay",
        "regime_extrapolation",
        "counterfactual",
    }
    missing_top = sorted(expected_top - set(packet))
    if missing_top:
        errors.append(f"missing top-level keys: {', '.join(missing_top)}")

    sections: dict[str, tuple[str, ...]] = {
        "state": ("s_t", "s_prev"),
        "forecast": ("Y_hat", "horizons"),
        "precision_error": ("error", "precision", "weighted_error"),
        "drift": (
            "drift_score",
            "shift_label_hat",
            "update_gain",
            "reset_probability",
            "state_adapted",
            "memory_priority",
        ),
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
        ),
    }

    for section, required in sections.items():
        value = packet.get(section)
        if not isinstance(value, dict):
            errors.append(f"section '{section}' must be a dict")
            continue
        missing = [key for key in required if key not in value]
        if missing:
            errors.append(f"section '{section}' missing keys: {', '.join(missing)}")

    forecast = packet.get("forecast")
    if isinstance(forecast, dict):
        horizons = forecast.get("horizons")
        if not isinstance(horizons, list) or not horizons:
            errors.append("forecast.horizons must be a non-empty list")

    return errors
