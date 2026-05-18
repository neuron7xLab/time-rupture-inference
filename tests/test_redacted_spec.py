# SPDX-License-Identifier: MIT
"""Structural invariants of the redacted hypothesis model."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.redacted import (  # noqa: E402
    EvidenceRequirement,
    ForbiddenInference,
    NextExperimentPolicy,
    RedactedFalsifier,
    RedactedHypothesisSpec,
    RedactedVariable,
)


def _spec(**over):
    base = dict(
        hypothesis_id="h",
        claim="c",
        null="n",
        assumptions=["a1"],
        variables=[RedactedVariable("v", "measured")],
        falsifiers=[RedactedFalsifier("m", "<=", "k", 1.0)],
        forbidden_inferences=[ForbiddenInference("no agi")],
        evidence_requirements=[EvidenceRequirement("sealed")],
    )
    base.update(over)
    return RedactedHypothesisSpec(**base)


def test_valid_spec_constructs_and_exposes_thresholds():
    s = _spec()
    assert s.thresholds() == {"k": 1.0}
    assert s.human_review_required is True
    assert s.commit_private_content is False


@pytest.mark.parametrize(
    "over",
    [
        {"hypothesis_id": " "},
        {"claim": ""},
        {"null": ""},
        {"assumptions": []},
        {"variables": []},
        {"falsifiers": []},
        {"forbidden_inferences": []},
        {"evidence_requirements": []},
        {"human_review_required": False},
        {"commit_private_content": True},
    ],
)
def test_invariants_reject_illposed_spec(over):
    with pytest.raises(ValueError):
        _spec(**over)


def test_variable_role_validated():
    with pytest.raises(ValueError):
        RedactedVariable("v", "not-a-role")


def test_falsifier_op_validated():
    with pytest.raises(ValueError):
        RedactedFalsifier("m", "==", "k", 1.0)


def test_policy_cannot_autorun_or_loosen():
    with pytest.raises(ValueError):
        NextExperimentPolicy(auto_run=True)
    with pytest.raises(ValueError):
        NextExperimentPolicy(loosen_failed_checks=True)
