# SPDX-License-Identifier: MIT
"""Smoke-check the NCTP adaptive state prototype."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ctios.nctp_state.packet import validate_inference_packet
from ctios.nctp_state.runtime import (
    build_prototype_inference_packet,
    task03_drift_shift_inference,
)


def _sample() -> tuple[list[list[list[float]]], list[list[float]], list[int]]:
    x = [
        [[1.0, 2.0], [1.1, 2.1], [1.2, 2.2]],
        [[0.5, 1.0], [0.55, 1.05], [2.5, 3.0]],
    ]
    dt = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    horizons = [1, 4, 8]
    return x, dt, horizons


def main() -> int:
    x, dt, horizons = _sample()
    y_true = [
        [[1.3, 2.3], [1.6, 2.6], [2.0, 3.0]],
        [[2.8, 3.3], [3.1, 3.6], [3.5, 4.0]],
    ]
    sigma = [
        [[0.4, 0.4], [0.5, 0.5], [0.7, 0.7]],
        [[0.2, 0.2], [0.2, 0.2], [0.2, 0.2]],
    ]
    packet = build_prototype_inference_packet(x, dt, y_true, sigma, horizons)
    errors = validate_inference_packet(packet)
    if errors:
        raise AssertionError("packet validation failed: " + "; ".join(errors))

    stable = task03_drift_shift_inference(
        weighted_error=[[[0.01], [0.02], [0.01]]],
        state_t=[[1.02]],
        state_prev=[[1.0]],
        sigma=[[[0.1], [0.1], [0.1]]],
        dt=[[1.0, 1.0, 1.0]],
        memory_conflict=[[0.0, 0.0, 0.0]],
    )
    changed = task03_drift_shift_inference(
        weighted_error=[[[10.0], [9.0], [11.0]]],
        state_t=[[4.0]],
        state_prev=[[1.0]],
        sigma=[[[0.2], [0.2], [0.2]]],
        dt=[[1.0, 1.0, 1.0]],
        memory_conflict=[[0.6, 0.6, 0.6]],
    )

    stable_score = stable.drift_score[0][0]
    changed_score = changed.drift_score[0][0]
    if not changed_score > stable_score:
        raise AssertionError("changed stream must score above stable stream")
    if not changed.shift_label_hat[0][0]:
        raise AssertionError("changed stream must trigger TASK-03 label")
    if changed.reset_probability[0][0] <= stable.reset_probability[0][0]:
        raise AssertionError("changed stream must increase reset probability")

    print(
        "NCTP_STATE_SMOKE — PASS "
        f"stable_score={stable_score:.4f} changed_score={changed_score:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
