# SPDX-License-Identifier: MIT
"""NCTP-1 inference packet contract.

Strict, fail-closed schema and numeric guards for deterministic provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class NCTPTaskSpec:
    task_id: str
    name: str
    required_outputs: tuple[str, ...]


TASK_SPECS: tuple[NCTPTaskSpec, ...] = (
    NCTPTaskSpec("TASK-01", "multi_horizon_temporal_inference", ("Y_hat",)),
    NCTPTaskSpec("TASK-02", "precision_weighted_error_inference", ("error", "precision", "weighted_error")),
    NCTPTaskSpec("TASK-03", "drift_rupture_inference", ("drift_score", "rupture_label_hat", "update_gain", "reset_probability")),
    NCTPTaskSpec("TASK-04", "causal_delay_inference", ("delay_distribution", "causal_credit", "effect_prediction")),
    NCTPTaskSpec("TASK-05", "episodic_memory_retrieval_inference", ("retrieved_state", "retrieval_weights", "memory_conflict", "write_priority")),
    NCTPTaskSpec("TASK-06", "regime_extrapolation", ("regime_probs", "future_regime_path", "regime_change_time", "extrapolated_state")),
    NCTPTaskSpec("TASK-07", "counterfactual_temporal_extrapolation", ("Y_real_hat", "Y_counterfact_hat", "counterfactual_delta", "causal_effect_score")),
)


SECTION_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "state": ("s_t",),
    "forecast": ("Y_hat", "horizons"),
    "precision_error": ("error", "precision", "weighted_error"),
    "drift": ("drift_score", "rupture_label_hat", "update_gain", "reset_probability"),
    "memory": ("retrieved_state", "retrieval_weights", "memory_conflict", "write_priority"),
    "causal_delay": ("delay_distribution", "causal_credit", "effect_prediction"),
    "regime_extrapolation": ("regime_probs", "future_regime_path", "regime_change_time", "extrapolated_state"),
    "counterfactual": ("Y_real_hat", "Y_counterfact_hat", "counterfactual_delta", "causal_effect_score", "status"),
    "runtime_boundary": ("task05_memory", "task06_regime", "task07_counterfactual"),
}


def _is_finite_number(x: object) -> bool:
    if isinstance(x, bool):
        return False
    if isinstance(x, (int, float)):
        return math.isfinite(float(x))
    return False




def _nested_numeric(x: object) -> bool:
    if isinstance(x, list):
        return all(_nested_numeric(v) for v in x)
    return _is_finite_number(x)

def _same_shape(a: object, b: object) -> bool:
    if isinstance(a, list) and isinstance(b, list):
        return len(a)==len(b) and all(_same_shape(x,y) for x,y in zip(a,b))
    return not isinstance(a, list) and not isinstance(b, list)

def _delta_matches(y_cf: object, y_real: object, delta: object, tol: float=1e-9) -> bool:
    if isinstance(y_cf, list) and isinstance(y_real, list) and isinstance(delta, list):
        return len(y_cf)==len(y_real)==len(delta) and all(_delta_matches(a,b,c,tol) for a,b,c in zip(y_cf,y_real,delta))
    if _is_finite_number(y_cf) and _is_finite_number(y_real) and _is_finite_number(delta):
        return abs((float(y_cf)-float(y_real)) - float(delta)) <= tol
    return False


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

    for section, req in SECTION_REQUIREMENTS.items():
        value = packet.get(section)
        if not isinstance(value, dict):
            errors.append(f"section '{section}' must be a dict")
            continue
        missing = [k for k in req if k not in value]
        if missing:
            errors.append(f"section '{section}' missing keys: {', '.join(missing)}")
        unknown = sorted(set(value) - set(req))
        if unknown:
            errors.append(f"section '{section}' has unknown keys: {', '.join(unknown)}")

    forecast = packet.get("forecast")
    if isinstance(forecast, dict):
        horizons = forecast.get("horizons")
        if not isinstance(horizons, list) or not horizons:
            errors.append("forecast.horizons must be a non-empty list")
        elif any((not isinstance(h, int)) or h <= 0 for h in horizons):
            errors.append("forecast.horizons must contain only positive integers")

    drift = packet.get("drift")
    if isinstance(drift, dict):
        ds = drift.get("drift_score")
        if isinstance(ds, list):
            vals = [v for row in ds if isinstance(row, list) for v in row]
            if any(not _is_finite_number(v) for v in vals):
                errors.append("drift.drift_score must contain finite numeric values")

    cdelay = packet.get("causal_delay")
    if isinstance(cdelay, dict):
        dd = cdelay.get("delay_distribution")
        if isinstance(dd, list):
            for row in dd:
                if isinstance(row, list) and row:
                    if any(not _is_finite_number(v) for v in row):
                        errors.append("causal_delay.delay_distribution must be finite")
                    s = 0.0
                    ok = True
                    for v in row:
                        if not _is_finite_number(v):
                            ok = False
                            break
                        s += float(v)
                    if not ok:
                        errors.append("causal_delay.delay_distribution must be finite")
                    elif abs(s - 1.0) > 1e-6:
                        errors.append("causal_delay.delay_distribution rows must be normalized")

    cf = packet.get("counterfactual")
    if isinstance(cf, dict):
        status = cf.get("status")
        y_real = cf.get("Y_real_hat")
        y_cf = cf.get("Y_counterfact_hat")
        delta = cf.get("counterfactual_delta")
        if status != "stub":
            if not _delta_matches(y_cf, y_real, delta):
                errors.append("counterfactual.counterfactual_delta must match Y_counterfact_hat - Y_real_hat or set status=stub")

    runtime_boundary = packet.get("runtime_boundary")
    if isinstance(runtime_boundary, dict):
        vals = [runtime_boundary.get("task05_memory"), runtime_boundary.get("task06_regime"), runtime_boundary.get("task07_counterfactual")]
        if any(v != "stub" for v in vals):
            errors.append("runtime_boundary TASK-05..07 must be declared as stub")

    return errors
