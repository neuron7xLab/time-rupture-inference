# SPDX-License-Identifier: MIT
"""Contract: the learned model is deterministic and obs-only (no z /
schedule / future leakage). NOT the scientific verdict."""
import inspect
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ctios.learners.echo_state_learner import EchoStateLearner  # noqa: E402


def test_constructor_takes_no_hidden_state():
    p = set(inspect.signature(EchoStateLearner.__init__).parameters)
    assert not (p & {"z", "z_sign", "t_z", "true_mean", "is_trigger",
                     "schedule", "period", "delta"})


def test_update_only_consumes_scalar_obs():
    p = list(inspect.signature(EchoStateLearner.update).parameters)
    assert p == ["self", "observed_interval"]


def test_deterministic_and_finite():
    rng = np.random.default_rng(0)
    stream = rng.normal(10.0, 1.0, 300)

    def run() -> list[float]:
        m = EchoStateLearner(dim=32, seed=7)
        out = []
        for x in stream:
            out.append(m.predict())
            m.update(float(x))
        return out

    a, b = run(), run()
    assert a == b and all(np.isfinite(a))


def test_readout_is_learned_not_constant():
    m = EchoStateLearner(dim=32, seed=1)
    first = m.predict()
    for x in (9.0, 11.0, 8.0, 12.0, 10.0, 7.0, 13.0):
        m.update(x)
    assert m.predict() != first  # readout adapted from data
