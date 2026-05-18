# SPDX-License-Identifier: MIT
"""Minimal action agents. No planning, no belief state, no active inference.

All three reuse the v4 ``LearnedAgent`` for interval prediction/update so
the ONLY new variable under test is the action policy.
"""

from __future__ import annotations

import numpy as np

from ctios.agents import LearnedAgent
from ctios.causal_env import ACTIONS


class _Wrap:
    """Shared prediction/update wiring around the v4 LearnedAgent."""

    name = "wrap"

    def __init__(self, prior: float = 1.0):
        self._la = LearnedAgent(prior=prior)

    def predict(self) -> float:
        return self._la.predict()

    def update(self, observed_interval: float, action: str) -> None:
        self._la.update(observed_interval)

    def drift_flag(self) -> bool:
        return self._la.drift_flag()


class NoActionAgent(_Wrap):
    name = "no_action"

    def select_action(self, previous_error: float | None) -> str:
        return "observe"


class RandomActionAgent(_Wrap):
    name = "random_action"

    def __init__(self, prior: float = 1.0, seed: int = 0):
        super().__init__(prior)
        self._rng = np.random.default_rng(seed)

    def select_action(self, previous_error: float | None) -> str:
        return ACTIONS[int(self._rng.integers(0, len(ACTIONS)))]


class CausalLearnedAgent(_Wrap):
    """observe by default; after drift / large error, test `stabilize` for a
    bounded window and keep it only while it reduces recent |error|."""

    name = "causal_learned"

    def __init__(self, prior: float = 1.0, window: int = 25, big_err_k: float = 3.0):
        super().__init__(prior)
        self.window = window
        self.big_err_k = big_err_k
        self._err_ema = 1.0
        self._entry_ema = 1.0
        self._left = 0
        self._stabilising = False

    def update(self, observed_interval: float, action: str) -> None:
        super().update(observed_interval, action)

    def select_action(self, previous_error: float | None) -> str:
        if previous_error is not None:
            ae = abs(previous_error)
            self._err_ema = 0.85 * self._err_ema + 0.15 * ae
            big = ae > self.big_err_k * max(self._err_ema, 1e-6)
            if (self.drift_flag() or big) and not self._stabilising:
                self._stabilising = True
                self._left = self.window
                self._entry_ema = self._err_ema

        if self._stabilising:
            self._left -= 1
            if self._left <= 0:
                if self._err_ema < 0.95 * self._entry_ema:
                    self._left = self.window  # working -> keep stabilising
                    self._entry_ema = self._err_ema
                else:
                    self._stabilising = False
                    return "observe"
            return "stabilize"
        return "observe"
