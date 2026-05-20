# SPDX-License-Identifier: MIT
from ctios.neural_runner import run_neural_demo


def test_neural_runner_smoke_returns_metrics():
    m = run_neural_demo(seed=0, steps=120, delta=7.0)
    assert set(m) == {'seed', 'steps', 'delta', 'post_shift_mae', 'uncertainty_final'}
    assert m['post_shift_mae'] >= 0.0
