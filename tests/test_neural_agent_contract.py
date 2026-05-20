# SPDX-License-Identifier: MIT
import numpy as np

from ctios.neural_agent import NeuralTemporalAgent


def test_neural_agent_emits_finite_outputs():
    a = NeuralTemporalAgent(seed=0)
    xs = np.linspace(8.0, 12.0, 50)
    out = a.run(xs)
    assert len(out) == 50
    assert all(np.isfinite(d.prediction) for d in out)
    assert all(np.isfinite(d.error) for d in out)
    assert all(np.isfinite(d.uncertainty) for d in out)
