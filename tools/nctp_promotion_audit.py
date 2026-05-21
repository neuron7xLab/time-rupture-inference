# SPDX-License-Identifier: MIT
"""Audit readiness of the nested NCTP adaptive-state prototype.

This tool is intentionally outside pytest accounting. It verifies the currently
nested prototype before any later top-level promotion PR changes README counts,
provenance roots, or canonical runtime surfaces.
"""

from __future__ import annotations

from copy import deepcopy

from ctios.nctp_state.packet import TASK_SPECS, validate_inference_packet
from ctios.nctp_state.runtime import (
    build_prototype_inference_packet,
    task03_drift_shift_inference,
)


def _sample_inputs() -> tuple[
    list[list[list[float]]],
    list[list[float]],
    list[list[list[float]]],
    list[list[list[float]]],
    list[int],
]:
    x = [
        [[1.0, 2.0], [1.1, 2.1], [1.2, 2.2]],
        [[0.5, 1.0], [0.55, 1.05], [2.5, 3.0]],
    ]
    dt = [[1.0, 1.5, 2.0], [1.0, 2.0, 3.0]]
    y_true = [
        [[1.3, 2.3], [1.6, 2.6], [2.0, 3.0]],
        [[2.8, 3.3], [3.1, 3.6], [3.5, 4.0]],
    ]
    sigma = [
        [[0.4, 0.4], [0.5, 0.5], [0.7, 0.7]],
        [[0.2, 0.2], [0.2, 0.2], [0.2, 0.2]],
    ]
    horizons = [1, 4, 8]
    return x, dt, y_true, sigma, horizons


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def audit_packet_contract() -> None:
    _assert(len(TASK_SPECS) == 7, "TASK_SPECS must cover seven tasks")
    x, dt, y_true, sigma, horizons = _sample_inputs()
    packet = build_prototype_inference_packet(x, dt, y_true, sigma, horizons)
    errors = validate_inference_packet(packet)
    _assert(errors == [], "valid packet rejected: " + "; ".join(errors))

    malformed = deepcopy(packet)
    malformed["state"] = None
    malformed_errors = validate_inference_packet(malformed)
    _assert(
        any("section 'state' must be a dict" in err for err in malformed_errors),
        "malformed state must fail validation",
    )

    missing_state = deepcopy(packet)
    del missing_state["state"]["s_prev"]
    missing_errors = validate_inference_packet(missing_state)
    _assert(
        any("section 'state' missing keys: s_prev" in err for err in missing_errors),
        "missing state.s_prev must fail validation",
    )


def audit_adaptive_state_behavior() -> None:
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
    _assert(
        changed.drift_score[0][0] > stable.drift_score[0][0],
        "changed stream must increase drift score",
    )
    _assert(changed.shift_label_hat[0][0], "changed stream must cross label threshold")
    _assert(
        changed.reset_probability[0][0] > stable.reset_probability[0][0],
        "changed stream must increase reset probability",
    )


def audit_dt_sensitivity() -> None:
    x, _, y_true, sigma, horizons = _sample_inputs()
    low = build_prototype_inference_packet(
        x=x,
        dt=[[0.1, 0.1, 0.1], [0.1, 0.1, 0.1]],
        y_true=y_true,
        sigma=sigma,
        horizons=horizons,
    )
    high = build_prototype_inference_packet(
        x=x,
        dt=[[5.0, 5.0, 5.0], [5.0, 5.0, 5.0]],
        y_true=y_true,
        sigma=sigma,
        horizons=horizons,
    )
    low_score = low["drift"]["drift_score"][0][0]
    high_score = high["drift"]["drift_score"][0][0]
    _assert(high_score > low_score, "builder must preserve dt sensitivity")


def main() -> int:
    audit_packet_contract()
    audit_adaptive_state_behavior()
    audit_dt_sensitivity()
    print("NCTP_PROMOTION_AUDIT — PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
