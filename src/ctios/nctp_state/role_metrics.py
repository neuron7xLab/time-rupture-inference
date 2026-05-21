# SPDX-License-Identifier: MIT
"""Trajectory metrics for NCTP role policy evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from ctios.nctp_state.role_dynamics import NCTPRole, RoleDecision


@dataclass(frozen=True)
class RolePolicyMetrics:
    steps: int
    role_switch_rate: float
    adapt_rate: float
    stabilize_rate: float
    quarantine_rate: float
    escalation_rate: float
    memory_write_rate: float
    blocked_write_rate: float
    unstable_flip_count: int


def evaluate_role_policy(decisions: list[RoleDecision]) -> RolePolicyMetrics:
    if not decisions:
        raise ValueError("decisions must be non-empty")

    steps = len(decisions)
    switches = sum(
        1
        for prev, cur in zip(decisions, decisions[1:], strict=False)
        if prev.role is not cur.role
    )
    flips = sum(
        1
        for left, mid, right in zip(decisions, decisions[1:], decisions[2:], strict=False)
        if left.role is right.role and left.role is not mid.role
    )
    adapt_steps = sum(1 for d in decisions if d.role is NCTPRole.ADAPT)
    stabilize_steps = sum(1 for d in decisions if d.role is NCTPRole.STABILIZE)
    quarantine_steps = sum(1 for d in decisions if d.role is NCTPRole.QUARANTINE)
    escalation_steps = sum(1 for d in decisions if d.escalation_required)
    memory_write_steps = sum(1 for d in decisions if d.memory_write_allowed)
    blocked_write_steps = sum(
        1 for d in decisions if d.role is NCTPRole.QUARANTINE and not d.memory_write_allowed
    )

    denom = float(steps)
    switch_denom = float(max(steps - 1, 1))
    return RolePolicyMetrics(
        steps=steps,
        role_switch_rate=switches / switch_denom,
        adapt_rate=adapt_steps / denom,
        stabilize_rate=stabilize_steps / denom,
        quarantine_rate=quarantine_steps / denom,
        escalation_rate=escalation_steps / denom,
        memory_write_rate=memory_write_steps / denom,
        blocked_write_rate=blocked_write_steps / denom,
        unstable_flip_count=flips,
    )


def assert_role_policy_invariants(metrics: RolePolicyMetrics) -> None:
    if metrics.steps < 1:
        raise ValueError("steps must be positive")
    for name, value in (
        ("role_switch_rate", metrics.role_switch_rate),
        ("adapt_rate", metrics.adapt_rate),
        ("stabilize_rate", metrics.stabilize_rate),
        ("quarantine_rate", metrics.quarantine_rate),
        ("escalation_rate", metrics.escalation_rate),
        ("memory_write_rate", metrics.memory_write_rate),
        ("blocked_write_rate", metrics.blocked_write_rate),
    ):
        if value < 0.0 or value > 1.0:
            raise ValueError(f"{name} must be in [0, 1]")
    if metrics.unstable_flip_count > max(1, metrics.steps // 3):
        raise ValueError("role policy flips too frequently")
