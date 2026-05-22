# SPDX-License-Identifier: MIT
"""Deterministic role dynamics for adaptive NCTP state control.

Roles are bounded control modes, not personas. The module turns measured
packet signals into a small policy decision that can be tested and rejected.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class NCTPRole(StrEnum):
    OBSERVE = "observe"
    ADAPT = "adapt"
    STABILIZE = "stabilize"
    QUARANTINE = "quarantine"


@dataclass(frozen=True)
class RoleSignals:
    drift_score: float
    reset_probability: float
    uncertainty: float
    memory_conflict: float


@dataclass(frozen=True)
class RoleDecision:
    role: NCTPRole
    update_allowed: bool
    memory_write_allowed: bool
    escalation_required: bool
    reason: str


def _finite_unit(name: str, value: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return value


def decide_role(signals: RoleSignals) -> RoleDecision:
    """Map bounded signals to a deterministic role decision.

    Rule order is fail-closed:

    1. high uncertainty plus memory conflict -> quarantine
    2. high reset probability -> stabilize
    3. high drift -> adapt
    4. otherwise observe
    """

    drift = _finite_unit("drift_score", signals.drift_score)
    reset = _finite_unit("reset_probability", signals.reset_probability)
    uncertainty = _finite_unit("uncertainty", signals.uncertainty)
    conflict = _finite_unit("memory_conflict", signals.memory_conflict)

    if uncertainty >= 0.80 and conflict >= 0.60:
        return RoleDecision(
            role=NCTPRole.QUARANTINE,
            update_allowed=False,
            memory_write_allowed=False,
            escalation_required=True,
            reason="high uncertainty and memory conflict",
        )

    if reset >= 0.70:
        return RoleDecision(
            role=NCTPRole.STABILIZE,
            update_allowed=True,
            memory_write_allowed=False,
            escalation_required=False,
            reason="reset probability above stabilize threshold",
        )

    if drift >= 0.55:
        return RoleDecision(
            role=NCTPRole.ADAPT,
            update_allowed=True,
            memory_write_allowed=True,
            escalation_required=False,
            reason="drift score above adapt threshold",
        )

    return RoleDecision(
        role=NCTPRole.OBSERVE,
        update_allowed=False,
        memory_write_allowed=False,
        escalation_required=False,
        reason="signals below adaptation thresholds",
    )


def role_from_packet(packet: dict[str, object]) -> RoleDecision:
    """Derive a deterministic role decision from an NCTP inference packet.

    Uncertainty is derived from precision, not from memory priority. Precision is
    the packet field that encodes confidence in the prediction-error channel;
    memory priority is an action hint, not an uncertainty measurement.
    """

    drift_section = packet.get("drift")
    memory_section = packet.get("memory")
    precision_section = packet.get("precision_error")
    if not isinstance(drift_section, dict):
        raise ValueError("packet requires drift section")
    if not isinstance(memory_section, dict):
        raise ValueError("packet requires memory section")
    if not isinstance(precision_section, dict):
        raise ValueError("packet requires precision_error section")

    drift_score = _mean_nested_unit(drift_section.get("drift_score"), "drift_score")
    reset_probability = _mean_nested_unit(
        drift_section.get("reset_probability"),
        "reset_probability",
    )
    memory_conflict = _mean_nested_unit(memory_section.get("memory_conflict"), "memory_conflict")
    uncertainty = _uncertainty_from_precision(precision_section.get("precision"))

    return decide_role(
        RoleSignals(
            drift_score=drift_score,
            reset_probability=reset_probability,
            uncertainty=uncertainty,
            memory_conflict=memory_conflict,
        )
    )


def _uncertainty_from_precision(value: object) -> float:
    precision = _mean_nested_positive(value, "precision")
    return 1.0 / (1.0 + precision)


def _mean_nested_unit(value: object, name: str) -> float:
    vals = _flatten_numeric(value, name)
    return _finite_unit(name, sum(vals) / float(len(vals)))


def _mean_nested_positive(value: object, name: str) -> float:
    vals = _flatten_numeric(value, name)
    mean_value = sum(vals) / float(len(vals))
    if mean_value < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return mean_value


def _flatten_numeric(value: object, name: str) -> list[float]:
    vals: list[float] = []

    def walk(node: object) -> None:
        if isinstance(node, list):
            if not node:
                raise ValueError(f"{name} contains empty list")
            for child in node:
                walk(child)
            return
        if not isinstance(node, (int, float)) or isinstance(node, bool):
            raise ValueError(f"{name} must contain only numeric values")
        scalar = float(node)
        if not math.isfinite(scalar):
            raise ValueError(f"{name} must contain finite values")
        vals.append(scalar)

    walk(value)
    if not vals:
        raise ValueError(f"{name} must contain at least one value")
    return vals
