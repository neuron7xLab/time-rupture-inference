# SPDX-License-Identifier: MIT
import numpy as np

from ctios.neural_agent import NeuralTemporalAgent


def test_neural_agent_deterministic_given_seed():
    xs = np.sin(np.linspace(0, 3.14, 120)) * 2 + 10
    a = NeuralTemporalAgent(seed=7)
    b = NeuralTemporalAgent(seed=7)
    oa = a.run(xs)
    ob = b.run(xs)
    assert [round(d.prediction, 10) for d in oa] == [round(d.prediction, 10) for d in ob]
