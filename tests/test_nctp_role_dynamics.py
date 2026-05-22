# SPDX-License-Identifier: MIT
"""Contract tests for deterministic NCTP role dynamics."""

from ctios.nctp_state.role_dynamics import NCTPRole, RoleSignals, decide_role


def test_role_enum_is_string_like() -> None:
    assert isinstance(NCTPRole.ADAPT, str)
    assert NCTPRole.ADAPT == "adapt"


def test_quarantine_wins_at_high_uncertainty_and_conflict() -> None:
    d = decide_role(RoleSignals(0.95, 0.95, 0.80, 0.60))
    assert d.role is NCTPRole.QUARANTINE
    assert d.escalation_required is True


def test_stabilize_wins_when_reset_high_without_quarantine() -> None:
    d = decide_role(RoleSignals(0.95, 0.70, 0.79, 0.59))
    assert d.role is NCTPRole.STABILIZE
    assert d.memory_write_allowed is False


def test_adapt_wins_on_drift_when_higher_priorities_not_met() -> None:
    d = decide_role(RoleSignals(0.60, 0.69, 0.10, 0.10))
    assert d.role is NCTPRole.ADAPT
    assert d.update_allowed is True


def test_observe_at_nominal_signals() -> None:
    d = decide_role(RoleSignals(0.54, 0.69, 0.79, 0.59))
    assert d.role is NCTPRole.OBSERVE
    assert d.reason == "signals below adaptation thresholds"
