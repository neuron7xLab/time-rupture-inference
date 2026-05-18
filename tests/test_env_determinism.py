import numpy as np

from ctios.env import Environment


def _series(seed: int) -> np.ndarray:
    e = Environment(10.0, 17.0, 300, 1.0, 600, seed)
    return np.array([e.step().observed_interval for _ in range(600)])


def test_same_seed_identical():
    assert np.array_equal(_series(0), _series(0))


def test_different_seed_differs():
    assert not np.array_equal(_series(0), _series(1))


def test_reset_replays():
    e = Environment(10.0, 17.0, 300, 1.0, 600, 7)
    a = [e.step().observed_interval for _ in range(600)]
    e.reset()
    b = [e.step().observed_interval for _ in range(600)]
    assert a == b


def test_regime_shift_present():
    e = Environment(10.0, 17.0, 300, 0.0, 600, 0)  # noiseless: exact means
    xs = [e.step().observed_interval for _ in range(600)]
    assert abs(xs[100] - 10.0) < 1e-9
    assert abs(xs[400] - 17.0) < 1e-9
