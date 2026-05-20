# SPDX-License-Identifier: MIT
"""Check the experimental adapter boundary without promoting it.

This is an operator tool, not a pytest test. It exists so the experimental
surface can be checked before a promotion PR without changing README test-count
accounting or canonical provenance policy.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ctios.experimental.neural_attention_adapter import NeuralAttentionAdapter
from ctios.experimental.neural_attention_runner import run_neural_attention_adapter, validate_stream

REQUIRED_KEYS = {
    "post_shift_mae",
    "scalar_baseline_post_shift_mae",
    "neural_minus_scalar_mae",
    "predictions_finite",
    "errors_finite",
    "uncertainty_finite",
    "mean_uncertainty",
    "uncertainty_calibration_ratio",
}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run_adapter(seed: int) -> list[tuple[float, float, float, int]]:
    adapter = NeuralAttentionAdapter(d_model=8, lr=0.01, seed=seed, max_history=4)
    stream = [1.0, 1.2, 0.9, 1.1, 2.0, 2.2, 2.1]
    out: list[tuple[float, float, float, int]] = []
    for value in stream:
        step = adapter.step(value)
        out.append((step.prediction, step.error, step.uncertainty, adapter.history_length))
    return out


def check_deterministic_replay() -> None:
    _assert(_run_adapter(seed=7) == _run_adapter(seed=7), "deterministic replay failed")


def check_finite_outputs() -> None:
    for prediction, error, uncertainty, _ in _run_adapter(seed=1):
        _assert(math.isfinite(prediction), "non-finite prediction")
        _assert(math.isfinite(error), "non-finite error")
        _assert(math.isfinite(uncertainty), "non-finite uncertainty")


def check_bounded_history() -> None:
    max_history = 3
    adapter = NeuralAttentionAdapter(seed=0, max_history=max_history)
    for value in np.linspace(1.0, 2.0, 12):
        adapter.step(float(value))
    _assert(adapter.history_length == max_history, "history exceeded max_history")


def check_invalid_stream_rejection() -> None:
    invalid_streams = [
        np.asarray([], dtype=float),
        np.asarray([[1.0, 2.0]], dtype=float),
        np.asarray([1.0, np.nan], dtype=float),
        np.asarray([1.0, np.inf], dtype=float),
    ]
    for stream in invalid_streams:
        try:
            validate_stream(stream)
        except ValueError:
            continue
        raise AssertionError(f"invalid stream accepted: {stream!r}")


def check_runner_contract() -> None:
    stream = np.asarray([1.0, 1.1, 1.2, 2.0, 2.1, 2.2], dtype=float)
    metrics = run_neural_attention_adapter(stream, seed=3, max_history=4)
    _assert(set(metrics) == REQUIRED_KEYS, f"metric keys drifted: {sorted(metrics)}")
    _assert(metrics["predictions_finite"] is True, "predictions_finite false")
    _assert(metrics["errors_finite"] is True, "errors_finite false")
    _assert(metrics["uncertainty_finite"] is True, "uncertainty_finite false")
    for key, value in metrics.items():
        if isinstance(value, bool):
            continue
        _assert(math.isfinite(float(value)), f"non-finite metric: {key}")


def main() -> int:
    checks = [
        check_deterministic_replay,
        check_finite_outputs,
        check_bounded_history,
        check_invalid_stream_rejection,
        check_runner_contract,
    ]
    for check in checks:
        check()
    print(f"EXPERIMENTAL CONTRACT — PASS ({len(checks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
