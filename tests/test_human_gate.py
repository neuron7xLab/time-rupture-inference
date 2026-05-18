# SPDX-License-Identifier: MIT
"""Human approval gate — append-only, never auto-run."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.human_gate import (  # noqa: E402
    GateError,
    approve_next,
    audit_trail,
    next_experiment_runnable,
    reject_next,
    seal_verdict,
)


def test_no_decision_means_not_runnable(tmp_path):
    assert next_experiment_runnable(tmp_path) is False
    assert audit_trail(tmp_path) == []


def test_approve_makes_runnable_and_is_appended(tmp_path):
    approve_next(tmp_path, "alice", "falsifier accepted")
    assert next_experiment_runnable(tmp_path) is True
    trail = audit_trail(tmp_path)
    assert len(trail) == 1 and trail[0].action == "approve"


def test_reject_after_approve_blocks_again(tmp_path):
    approve_next(tmp_path, "a", "ok")
    reject_next(tmp_path, "a", "underdefined")
    assert next_experiment_runnable(tmp_path) is False
    assert len(audit_trail(tmp_path)) == 2  # append-only, nothing overwritten


def test_seal_is_recorded(tmp_path):
    seal_verdict(tmp_path, "a", "verdict final")
    assert audit_trail(tmp_path)[-1].action == "seal"


@pytest.mark.parametrize("fn", [approve_next, reject_next, seal_verdict])
def test_empty_reviewer_or_reason_fails(tmp_path, fn):
    with pytest.raises(GateError):
        fn(tmp_path, "", "reason")
    with pytest.raises(GateError):
        fn(tmp_path, "rev", "  ")
