# SPDX-License-Identifier: MIT
"""Pre-registered metrics computed from per-step prediction errors."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from ctios.contract import RECOVERY_ROLL_WINDOW, validate_window
from ctios.series import rolling_mean_prefix


@dataclass(frozen=True)
class Metrics:
    pre_shift_mae: float
    post_shift_mae: float
    adaptation_time: float
    area_under_post_shift_error: float
    detection_delay: float
    false_alarm_rate: float
    stability_pre_shift: float
    recovery_slope: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def compute_metrics(
    errors: np.ndarray,
    t_star: int,
    eval_horizon: int,
    detection_step: int | None,
    recovery_band_mult: float,
) -> Metrics:
    validate_window(t_star, eval_horizon, errors.size, detection_step)
    abs_err = np.abs(errors)
    pre = abs_err[:t_star]
    post = abs_err[t_star : t_star + eval_horizon]

    pre_mae = float(np.mean(pre)) if pre.size else float("nan")
    post_mae = float(np.mean(post)) if post.size else float("nan")
    aue = float(np.sum(post))
    stability = float(np.var(pre)) if pre.size else float("nan")

    band = recovery_band_mult * pre_mae
    roll = rolling_mean_prefix(post, RECOVERY_ROLL_WINDOW)
    rec = np.where(roll <= band)[0]
    adaptation_time = float(rec[0]) if rec.size else float("inf")

    if detection_step is None or detection_step < t_star:
        detection_delay = float("inf")
    else:
        detection_delay = float(detection_step - t_star)

    pre_signals = 0
    # false alarms are reported by the runner via detection history; here we
    # accept a sentinel and let the runner override (kept 0.0 if unknown).
    false_alarm_rate = float(pre_signals)

    if rec.size >= 1:
        seg = roll[: int(rec[0]) + 1]
        # Slope is defined per transition step between consecutive points.
        # For a single-point segment there are no transitions, so slope = 0.0.
        recovery_slope = float((seg[0] - seg[-1]) / max(1, len(seg) - 1))
    else:
        recovery_slope = 0.0

    return Metrics(
        pre_shift_mae=pre_mae,
        post_shift_mae=post_mae,
        adaptation_time=adaptation_time,
        area_under_post_shift_error=aue,
        detection_delay=detection_delay,
        false_alarm_rate=false_alarm_rate,
        stability_pre_shift=stability,
        recovery_slope=recovery_slope,
    )
