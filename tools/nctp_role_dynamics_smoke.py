# SPDX-License-Identifier: MIT
"""Smoke-check deterministic NCTP role dynamics."""

from __future__ import annotations

from ctios.nctp_state.role_dynamics import NCTPRole, RoleSignals, decide_role, role_from_packet
from ctios.nctp_state.runtime import build_prototype_inference_packet


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_signal_decisions() -> None:
    observe = decide_role(
        RoleSignals(
            drift_score=0.10,
            reset_probability=0.10,
            uncertainty=0.10,
            memory_conflict=0.10,
        )
    )
    _assert(observe.role is NCTPRole.OBSERVE, "low signals must observe")
    _assert(not observe.update_allowed, "observe must not update")

    adapt = decide_role(
        RoleSignals(
            drift_score=0.80,
            reset_probability=0.20,
            uncertainty=0.20,
            memory_conflict=0.10,
        )
    )
    _assert(adapt.role is NCTPRole.ADAPT, "high drift must adapt")
    _assert(adapt.update_allowed, "adapt must allow update")
    _assert(adapt.memory_write_allowed, "adapt must allow memory write")

    stabilize = decide_role(
        RoleSignals(
            drift_score=0.80,
            reset_probability=0.90,
            uncertainty=0.20,
            memory_conflict=0.10,
        )
    )
    _assert(stabilize.role is NCTPRole.STABILIZE, "high reset must stabilize")
    _assert(stabilize.update_allowed, "stabilize must allow update")
    _assert(not stabilize.memory_write_allowed, "stabilize must block memory write")

    quarantine = decide_role(
        RoleSignals(
            drift_score=0.80,
            reset_probability=0.20,
            uncertainty=0.90,
            memory_conflict=0.90,
        )
    )
    _assert(quarantine.role is NCTPRole.QUARANTINE, "high uncertainty/conflict must quarantine")
    _assert(not quarantine.update_allowed, "quarantine must block update")
    _assert(quarantine.escalation_required, "quarantine must escalate")


def test_packet_decision() -> None:
    x = [[[1.0], [1.1], [3.0]]]
    dt = [[1.0, 1.0, 1.0]]
    y_true = [[[3.5], [4.0], [4.5]]]
    sigma = [[[0.2], [0.2], [0.2]]]
    packet = build_prototype_inference_packet(x, dt, y_true, sigma, [1, 4, 8])
    decision = role_from_packet(packet)
    _assert(decision.role in set(NCTPRole), "packet decision must return a valid role")


def test_invalid_signal_rejected() -> None:
    try:
        decide_role(
            RoleSignals(
                drift_score=1.5,
                reset_probability=0.0,
                uncertainty=0.0,
                memory_conflict=0.0,
            )
        )
    except ValueError:
        return
    raise AssertionError("out-of-range signal must fail")


def main() -> int:
    test_signal_decisions()
    test_packet_decision()
    test_invalid_signal_rejected()
    print("NCTP_ROLE_DYNAMICS_SMOKE — PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
