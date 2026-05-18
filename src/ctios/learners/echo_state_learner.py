# SPDX-License-Identifier: MIT
"""Small online-learned recurrent sequence model (echo-state reservoir +
recursive-least-squares readout).

The recurrent map is a fixed seeded random projection; the READOUT is
learned online from data (no hand-coded sign rule). It consumes ONLY the
observed interval stream — no hidden context, no schedule, no trigger
labels, no future. Deterministic given the seed.
"""

from __future__ import annotations

import numpy as np


class EchoStateLearner:
    def __init__(
        self,
        dim: int = 64,
        seed: int = 0,
        leak: float = 0.3,
        ridge: float = 1e-2,
        prior: float = 1.0,
    ) -> None:
        r = np.random.default_rng(seed)
        w = r.normal(0.0, 1.0, (dim, dim))
        radius = float(np.max(np.abs(np.linalg.eigvals(w))))
        self._W = 0.9 * w / (radius + 1e-9)        # echo-state property
        self._win = r.normal(0.0, 0.5, dim)
        self._h = np.zeros(dim)
        self._leak = leak
        self._P = np.eye(dim) / ridge
        self._w = np.zeros(dim)
        self._pred = prior

    def predict(self) -> float:
        self._pred = float(self._w @ self._h)
        return self._pred

    def update(self, observed_interval: float) -> None:
        x = float(observed_interval)
        # RLS readout fit on the state that produced the prediction
        err = x - self._w @ self._h
        Ph = self._P @ self._h
        g = Ph / (1.0 + self._h @ Ph)
        self._w = self._w + g * err
        self._P = self._P - np.outer(g, Ph)
        # advance the reservoir state with the observation
        self._h = (1.0 - self._leak) * self._h + self._leak * np.tanh(
            self._W @ self._h + self._win * x
        )
