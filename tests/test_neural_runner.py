# SPDX-License-Identifier: MIT
import numpy as np

from ctios.neural_runner import run_neural_demo


def test_neural_runner_returns_required_metrics_and_deterministic():
    a = run_neural_demo(seed=0, steps=120, delta=7.0)
    b = run_neural_demo(seed=0, steps=120, delta=7.0)
    assert set(a) == {'seed', 'steps', 'delta', 'post_shift_mae', 'uncertainty_final'}
    assert np.isfinite(a['post_shift_mae'])
    assert np.isfinite(a['uncertainty_final'])
    assert a == b
