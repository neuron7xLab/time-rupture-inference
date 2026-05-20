# SPDX-License-Identifier: MIT

from pathlib import Path


FORBIDDEN_CLAIMS = (
    "intelligence",
    "cognition",
    "agi",
    "brain simulation",
    "biological time perception",
)


def test_v9_prereg_claim_boundary():
    path = Path("prereg/v9_neural_temporal_agent.yaml")
    assert path.exists()
    txt = path.read_text(encoding="utf-8").lower()
    assert "negative_result_is_valid: true" in txt
    assert "allowed_claim" in txt
    for forbidden in FORBIDDEN_CLAIMS:
        assert forbidden in txt
