# SPDX-License-Identifier: MIT
"""Deterministic role dynamics for adaptive NCTP state control.

The module converts measured runtime signals into a role state. Roles are not
personas. They are bounded control modes for dynamic environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math


class NCTPRole(str, Enum):
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

    Rule order is intentional and fail-closed:

    1. High uncertainty plus memory conflict enters quarantine.
    2. High reset probability enters stabilize.
    3. High drift enters adapt.
    4. Otherwise observe.
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
    """Derive a role decision from an NCTP inference packet."""

    drift_section = packet.get("drift")
    memory_section = packet.get("memory")
    if not isinstance(drift_section, dict) or not isinstance(memory_section, dict):
        raise ValueError("packet requires drift and memory sections")

    drift_score = _first_scalar(drift_section.get("drift_score"), "drift_score")
    reset_probability = _first_scalar(drift_section.get("reset_probability"), "reset_probability")
    uncertainty = _first_scalar(drift_section.get("memory_priority"), "memory_priority")
    memory_conflict = _first_scalar(memory_section.get("memory_conflict"), "memory_conflict")

    return decide_role(
        RoleSignals(
            drift_score=drift_score,
            reset_probability=reset_probability,
            uncertainty=uncertainty,
            memory_conflict=memory_conflict,
        )
    )


def _first_scalar(value: object, name: str) -> float:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a non-empty nested list")
    first = value[0]
    if not isinstance(first, list) or not first:
        raise ValueError(f"{name} must be a non-empty nested list")
    scalar = first[0]
    if not isinstance(scalar, (int, float)) or isinstance(scalar, bool):
        raise ValueError(f"{name} first value must be numeric")
    return float(scalar)
