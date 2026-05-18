# SPDX-License-Identifier: MIT
"""v6 lineage guards: opt-in default OFF (frozen v4 invariant), determinism."""

import inspect

import numpy as np
import pytest

from ctios.agents import LearnedAgent
from ctios.env import Environment


def test_precision_weighted_defaults_off():
    # Frozen-invariant guard: enabling it must be an explicit opt-in.
    assert inspect.signature(LearnedAgent.__init__).parameters[
        "precision_weighted"
    ].default is False


def test_q_process_must_be_positive():
    with pytest.raises(ValueError, match="q_process"):
        LearnedAgent(precision_weighted=True, q_process=0.0)


def _post(agent: LearnedAgent, seed: int) -> float:
    env = Environment(10.0, 17.0, 300, 1.0, 600, seed)
    env.reset()
    errs = []
    for _ in range(600):
        p = agent.predict()
        o = env.step()
        errs.append(abs(o.observed_interval - p))
        agent.update(o.observed_interval)
    return float(np.mean(errs[300:550]))


def test_precision_agent_deterministic():
    assert _post(LearnedAgent(prior=1.0, precision_weighted=True), 0) == _post(
        LearnedAgent(prior=1.0, precision_weighted=True), 0
    )


def test_precision_agent_adapts_post_shift():
    # Sanity: it must at least track the regime (not diverge).
    assert _post(LearnedAgent(prior=1.0, precision_weighted=True), 0) < 3.0
