import inspect

import numpy as np
import pytest

from ctios.neural_agent import NeuralTemporalAdapter


def test_runtime_api_is_obs_only():
    p = list(inspect.signature(NeuralTemporalAdapter.step).parameters)
    assert p == ["self", "observed_interval"]


def test_finite_outputs():
    m = NeuralTemporalAdapter(seed=3)
    stream = np.linspace(8.0, 12.0, 64)
    out = [m.step(float(x)) for x in stream]
    assert np.isfinite([s.prediction for s in out]).all()
    assert np.isfinite([s.error for s in out]).all()
    assert np.isfinite([s.uncertainty for s in out]).all()


def test_rejects_non_finite_observation():
    m = NeuralTemporalAdapter(seed=1)
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError, match="finite"):
            m.step(bad)


def test_history_is_bounded_by_max_history():
    m = NeuralTemporalAdapter(seed=2, max_history=5)
    for x in np.linspace(0.0, 20.0, 21):
        m.step(float(x))
    assert m._hist_len == 5


def test_rejects_invalid_max_history():
    with pytest.raises(ValueError, match="max_history"):
        NeuralTemporalAdapter(max_history=0)


def test_rejects_invalid_learning_rate():
    with pytest.raises(ValueError, match="lr"):
        NeuralTemporalAdapter(lr=0.0)


def test_rejects_invalid_d_model():
    with pytest.raises(ValueError, match="d_model"):
        NeuralTemporalAdapter(d_model=0)
