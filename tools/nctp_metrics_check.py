# SPDX-License-Identifier: MIT
from __future__ import annotations

from ctios.nctp_state.role_dynamics import NCTPRole, RoleDecision
from ctios.nctp_state.role_metrics import assert_role_policy_invariants, evaluate_role_policy


def make(role: NCTPRole) -> RoleDecision:
    return RoleDecision(
        role=role,
        update_allowed=role in {NCTPRole.ADAPT, NCTPRole.STABILIZE},
        memory_write_allowed=role is NCTPRole.ADAPT,
        escalation_required=role is NCTPRole.QUARANTINE,
        reason="check",
    )


def main() -> int:
    seq = [make(NCTPRole.OBSERVE), make(NCTPRole.ADAPT), make(NCTPRole.ADAPT)]
    metrics = evaluate_role_policy(seq)
    assert metrics.steps == 3
    assert metrics.adapt_rate == 2 / 3
    assert metrics.role_switch_rate == 0.5
    assert metrics.memory_write_rate == 2 / 3
    assert_role_policy_invariants(metrics)

    blocked = [make(NCTPRole.QUARANTINE), make(NCTPRole.QUARANTINE)]
    blocked_metrics = evaluate_role_policy(blocked)
    assert blocked_metrics.blocked_write_rate == 1.0
    assert blocked_metrics.memory_write_rate == 0.0
    assert_role_policy_invariants(blocked_metrics)

    print("NCTP_METRICS_CHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
