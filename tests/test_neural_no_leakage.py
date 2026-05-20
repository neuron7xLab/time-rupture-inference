# SPDX-License-Identifier: MIT
from pathlib import Path

import numpy as np

from ctios.neural_agent import NeuralTemporalAgent


def test_neural_agent_source_no_hidden_schedule_tokens():
    source = Path("src/ctios/neural_agent.py").read_text(encoding="utf-8").lower()
    for forbidden in ("tau0", "tau1", "t_star", "regime_label", "hidden_context"):
        assert source.find(forbidden) == -1


def test_neural_agent_behavioral_interface_scalar_only():
    agent = NeuralTemporalAgent(seed=0)
    decision = agent.step(10.0)
    assert isinstance(decision.prediction, float)
    out = agent.run(np.asarray([10.0, 11.0, 12.0]))
    assert len(out) == 3
