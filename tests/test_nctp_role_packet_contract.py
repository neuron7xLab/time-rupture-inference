# SPDX-License-Identifier: MIT
"""Contract tests for packet->role mapping invariants."""

import pytest

from ctios.nctp_state.role_dynamics import NCTPRole, role_from_packet


def _packet(*, precision: float, drift: float, reset: float, conflict: float) -> dict[str, object]:
    return {
        "drift": {"drift_score": [drift], "reset_probability": [reset]},
        "memory": {"memory_conflict": [conflict], "memory_priority": [1.0]},
        "precision_error": {"precision": [precision]},
    }


def test_precision_drives_uncertainty_not_memory_priority() -> None:
    pkt = _packet(precision=0.1, drift=0.1, reset=0.1, conflict=0.8)
    decision = role_from_packet(pkt)
    assert decision.role is NCTPRole.QUARANTINE


def test_high_precision_can_avoid_quarantine_and_fall_back_to_observe() -> None:
    pkt = _packet(precision=100.0, drift=0.1, reset=0.1, conflict=0.8)
    decision = role_from_packet(pkt)
    assert decision.role is NCTPRole.OBSERVE


def test_missing_required_packet_section_fails_closed() -> None:
    pkt = _packet(precision=1.0, drift=0.1, reset=0.1, conflict=0.1)
    del pkt["precision_error"]
    with pytest.raises(ValueError, match="requires precision_error"):
        role_from_packet(pkt)
