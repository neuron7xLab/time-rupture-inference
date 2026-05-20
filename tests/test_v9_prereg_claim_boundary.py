# SPDX-License-Identifier: MIT
from pathlib import Path


def test_v9_prereg_claim_boundary():
    p = Path('prereg/v9_neural_temporal_agent.yaml')
    assert p.exists()
    txt = p.read_text(encoding='utf-8').lower()
    assert 'negative_result_is_valid: true' in txt
    assert 'allowed_claim' in txt
    for forbidden in ('intelligence', 'cognition', 'agi', 'brain simulation', 'biological time perception'):
        assert forbidden in txt
