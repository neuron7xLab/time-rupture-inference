# SPDX-License-Identifier: MIT
"""Smoke-check deterministic NCTP role dynamics."""

from __future__ import annotations

from copy import deepcopy

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


def _packet() -> dict[str, object]:
    x = [[[1.0], [1.1], [3.0]]]
    dt = [[1.0, 1.0, 1.0]]
    y_true = [[[3.5], [4.0], [4.5]]]
    sigma = [[[0.2], [0.2], [0.2]]]
    return build_prototype_inference_packet(x, dt, y_true, sigma, [1, 4, 8])


def test_packet_decision() -> None:
    decision = role_from_packet(_packet())
    _assert(isinstance(decision.role, NCTPRole), "packet decision must return a valid role")


def test_packet_uncertainty_comes_from_precision() -> None:
    packet = _packet()
    packet["drift"]["drift_score"] = [[0.20]]
    packet["drift"]["reset_probability"] = [[0.20]]
    packet["memory"]["memory_conflict"] = [[0.90, 0.90, 0.90]]
    packet["drift"]["memory_priority"] = [[1.0]]

    high_precision = deepcopy(packet)
    high_precision["precision_error"]["precision"] = [[[100.0], [100.0], [100.0]]]
    high_precision_decision = role_from_packet(high_precision)
    _assert(
        high_precision_decision.role is not NCTPRole.QUARANTINE,
        "memory_priority alone must not drive quarantine",
    )

    low_precision = deepcopy(packet)
    low_precision["precision_error"]["precision"] = [[[0.01], [0.01], [0.01]]]
    low_precision_decision = role_from_packet(low_precision)
    _assert(
        low_precision_decision.role is NCTPRole.QUARANTINE,
        "low precision plus memory conflict must quarantine",
    )


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
    test_packet_uncertainty_comes_from_precision()
    test_invalid_signal_rejected()
    print("NCTP_ROLE_DYNAMICS_SMOKE — PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
