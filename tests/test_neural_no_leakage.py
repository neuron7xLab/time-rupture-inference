# SPDX-License-Identifier: MIT
from pathlib import Path
import numpy as np

from ctios.neural_agent import NeuralTemporalAgent


def test_neural_agent_source_no_hidden_schedule_tokens():
    s = Path('src/ctios/neural_agent.py').read_text(encoding='utf-8').lower()
    for bad in ('tau0', 'tau1', 't_star', 'regime_label', 'hidden_context'):
        assert s.find(bad) == -1


def test_neural_agent_behavioral_interface_scalar_only():
    a = NeuralTemporalAgent(seed=0)
    d = a.step(10.0)
    assert type(d.prediction) == float
    out = a.run(np.asarray([10.0, 11.0, 12.0]))
    assert len(out) == 3
