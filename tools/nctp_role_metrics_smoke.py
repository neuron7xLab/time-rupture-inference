# SPDX-License-Identifier: MIT
from __future__ import annotations

from ctios.nctp_state.role_dynamics import NCTPRole, RoleDecision
from ctios.nctp_state.role_metrics import assert_role_policy_invariants, evaluate_role_policy


def d(role: NCTPRole) -> RoleDecision:
    return RoleDecision(
        role=role,
        update_allowed=role in {NCTPRole.ADAPT, NCTPRole.STABILIZE},
        memory_write_allowed=role is NCTPRole.ADAPT,
        escalation_required=role is NCTPRole.QUARANTINE,
        reason="test",
    )


def main() -> int:
    seq = [d(NCTPRole.OBSERVE), d(NCTPRole.ADAPT), d(NCTPRole.ADAPT)]
    m = evaluate_role_policy(seq)
    assert m.steps == 3
    assert m.adapt_rate == 2 / 3
    assert m.role_switch_rate == 0.5
    assert m.memory_write_rate == 2 / 3
    assert_role_policy_invariants(m)

    q = [d(NCTPRole.QUARANTINE), d(NCTPRole.QUARANTINE)]
    qm = evaluate_role_policy(q)
    assert qm.blocked_write_rate == 1.0
    assert qm.memory_write_rate == 0.0
    assert_role_policy_invariants(qm)

    flip = [
        d(NCTPRole.ADAPT),
        d(NCTPRole.OBSERVE),
        d(NCTPRole.ADAPT),
        d(NCTPRole.OBSERVE),
        d(NCTPRole.ADAPT),
    ]
    try:
        assert_role_policy_invariants(evaluate_role_policy(flip))
    except ValueError:
        print("NCTP_ROLE_METRICS_SMOKE — PASS")
        return 0
    raise AssertionError("frequent role flips must fail")


if __name__ == "__main__":
    raise SystemExit(main())
