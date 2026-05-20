import numpy as np
import pytest

from ctios.neural_runner import run_neural_temporal_adapter


def test_runner_metrics_and_deterministic_replay():
    stream = np.random.default_rng(9).normal(10.0, 1.5, 200)
    a = run_neural_temporal_adapter(stream, seed=11)
    b = run_neural_temporal_adapter(stream, seed=11)
    assert set(a).issuperset({"post_shift_mae", "scalar_baseline_post_shift_mae", "neural_minus_scalar_mae"})
    assert np.isfinite(a["post_shift_mae"])
    assert a == b


def test_runner_rejects_bad_stream_shape_and_values():
    bad_streams = [
        np.array([]),
        np.array([[1.0, 2.0]]),
        np.array([1.0, np.nan]),
    ]
    for bad in bad_streams:
        with pytest.raises(ValueError):
            run_neural_temporal_adapter(bad, seed=1)


def test_runner_finite_flags_are_boolean():
    stream = np.random.default_rng(2).normal(10.0, 0.5, 32)
    out = run_neural_temporal_adapter(stream, seed=2)
    assert isinstance(out["predictions_finite"], bool)
    assert isinstance(out["errors_finite"], bool)
    assert isinstance(out["uncertainty_finite"], bool)


def test_runner_comparison_metric_is_finite_across_seeds():
    base = np.linspace(8.0, 12.0, 64)
    for seed in range(5):
        out = run_neural_temporal_adapter(base, seed=seed)
        assert np.isfinite(out["neural_minus_scalar_mae"])


def test_runner_accepts_explicit_max_history():
    stream = np.random.default_rng(4).normal(10.0, 1.0, 80)
    out = run_neural_temporal_adapter(stream, seed=4, max_history=8)
    assert np.isfinite(out["post_shift_mae"])


def test_runner_deterministic_with_small_history_window():
    stream = np.random.default_rng(7).normal(10.0, 1.0, 96)
    a = run_neural_temporal_adapter(stream, seed=3, max_history=4)
    b = run_neural_temporal_adapter(stream, seed=3, max_history=4)
    assert a == b


def test_runner_rejects_invalid_max_history():
    stream = np.random.default_rng(0).normal(10.0, 1.0, 16)
    with pytest.raises(ValueError, match="max_history"):
        run_neural_temporal_adapter(stream, seed=0, max_history=0)
