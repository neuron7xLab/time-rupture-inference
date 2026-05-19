# SPDX-License-Identifier: MIT
"""ctios.change_detection — the distilled primitive of the arc.

Lineages #24–#29 converge on one essence: detect a hidden regime
rupture from a *stationary two-window contrast on the raw observation*,
threshold it by a *held-out-null-calibrated quantile*, fire on the
*first crossing*. The only thing that legitimately varies between
lineages is the contrast's location/scale pair (mean/std vs median/MAD)
and its window widths. Everything else is shared here, once.

No biological / cognition / AGI / theory-of-time claim is made; this is
a functional change-detection primitive on synthetic streams only.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from ctios.predictive_simulation import RuptureStream

Contrast = Callable[[np.ndarray], np.ndarray]
_Loc = Callable[[np.ndarray], float]
_Scale = Callable[[np.ndarray, np.ndarray, float, float], float]


def _mean(x: np.ndarray) -> float:
    return float(x.mean())


def _median(x: np.ndarray) -> float:
    return float(np.median(x))


def _pooled_std(s: np.ndarray, b: np.ndarray, _ms: float, _mb: float) -> float:
    return float(np.sqrt(0.5 * (s.var() + b.var())))


def _pooled_mad(s: np.ndarray, b: np.ndarray, ms: float, mb: float) -> float:
    return float(
        0.5 * (np.median(np.abs(s - ms)) + np.median(np.abs(b - mb)))
    )


def two_window_contrast(
    obs: np.ndarray,
    *,
    w_short: int,
    w_base: int,
    loc: _Loc,
    scale: _Scale,
    eps: float = 1e-6,
) -> np.ndarray:
    """|loc(short) − loc(base)| / (scale + eps), evaluated once full
    history exists (warmup = w_base + w_short); earlier indices are 0.
    Stationary under the null; spikes when a regime boundary falls
    between the two windows."""
    n = obs.size
    warmup = w_base + w_short
    s = np.zeros(n, dtype=np.float64)
    for t in range(warmup, n):
        short = obs[t - w_short:t]
        base = obs[t - w_base - w_short:t - w_short]
        ls, lb = loc(short), loc(base)
        s[t] = abs(ls - lb) / (scale(short, base, ls, lb) + eps)
    return s


def mean_std_contrast(w_short: int, w_base: int) -> Contrast:
    """The #26 observable: mean / pooled-std two-window contrast."""
    return lambda o: two_window_contrast(
        o, w_short=w_short, w_base=w_base, loc=_mean, scale=_pooled_std
    )


def median_mad_contrast(w_short: int, w_base: int) -> Contrast:
    """The #28 observable: median / pooled-MAD — robust to a bounded
    low-frequency carrier confound."""
    return lambda o: two_window_contrast(
        o, w_short=w_short, w_base=w_base, loc=_median, scale=_pooled_mad
    )


def first_crossing(series: np.ndarray, lam: float) -> int:
    """First index whose statistic exceeds λ, else −1."""
    idx = np.flatnonzero(series > lam)
    return int(idx[0]) if idx.size else -1


def quantile_calibrated_threshold(
    contrast: Contrast, calib_null_seeds: range, alpha: float
) -> float:
    """λ = the (1−α) empirical quantile of the per-stream maximum
    contrast over the held-out null calibration streams. A fixed rule —
    no hand-tuning, no in-sample peeking."""
    peaks = [
        float(np.max(contrast(RuptureStream.make_null(s).obs)))
        for s in calib_null_seeds
    ]
    return float(np.quantile(peaks, 1.0 - alpha))


class ThresholdDetector:
    """An observable + a calibrated threshold. detect → first crossing."""

    def __init__(self, contrast: Contrast, lam: float) -> None:
        self._contrast = contrast
        self.lam = lam

    def detect(self, obs: np.ndarray) -> int:
        return first_crossing(
            self._contrast(np.asarray(obs, dtype=np.float64)), self.lam
        )
