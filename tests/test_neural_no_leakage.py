# SPDX-License-Identifier: MIT
from pathlib import Path


def test_neural_agent_source_has_no_hidden_schedule_tokens():
    s = Path('src/ctios/neural_agent.py').read_text(encoding='utf-8').lower()
    for bad in ('tau0', 'tau1', 't_star', 'regime_label', 'hidden_context'):
        assert bad not in s
