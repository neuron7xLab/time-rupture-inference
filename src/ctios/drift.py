# SPDX-License-Identifier: MIT
"""Online change-point detectors operating on the prediction-error stream.

Page-Hinkley is the primary online signal; CUSUM is provided as an
independent cross-check (negative-control for detector dependence).
"""

from __future__ import annotations


class PageHinkley:
    """Page-Hinkley test on a scalar stream (two-sided on |error|)."""

    def __init__(self, delta: float = 0.2, lambda_: float = 8.0, alpha: float = 0.999):
        self.delta = delta
        self.lambda_ = lambda_
        self.alpha = alpha
        self._mean = 0.0
        self._n = 0
        self._m = 0.0
        self._min = 0.0

    def update(self, value: float) -> bool:
        v = abs(value)
        self._n += 1
        self._mean = self.alpha * self._mean + (1.0 - self.alpha) * v if self._n > 1 else v
        self._m += v - self._mean - self.delta
        self._min = min(self._min, self._m)
        return (self._m - self._min) > self.lambda_

    def reset(self) -> None:
        self._mean = 0.0
        self._n = 0
        self._m = 0.0
        self._min = 0.0


class CUSUM:
    """Symmetric CUSUM on |error| — independent detector for cross-check."""

    def __init__(self, threshold: float = 12.0, drift: float = 0.25):
        self.threshold = threshold
        self.drift = drift
        self._g_pos = 0.0
        self._mean = 0.0
        self._n = 0

    def update(self, value: float) -> bool:
        v = abs(value)
        self._n += 1
        self._mean += (v - self._mean) / self._n
        self._g_pos = max(0.0, self._g_pos + v - self._mean - self.drift)
        return self._g_pos > self.threshold

    def reset(self) -> None:
        self._g_pos = 0.0
        self._mean = 0.0
        self._n = 0
