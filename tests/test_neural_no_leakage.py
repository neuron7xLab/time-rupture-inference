# SPDX-License-Identifier: MIT
import numpy as np

from ctios.neural_agent import NeuralTemporalAgent


def test_neural_agent_runtime_has_no_hidden_schedule_fields():
    a = NeuralTemporalAgent(seed=0)
    _ = a.run(np.linspace(8.0, 12.0, 32))
    s = repr(a.__dict__).lower()
    for bad in ('tau0', 'tau1', 't_star', 'regime_label', 'hidden_context'):
        assert bad not in s
