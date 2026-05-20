# SPDX-License-Identifier: MIT
"""CTI-OS neural temporal adapter.

Small deterministic neural learner intended to run *inside* the existing
non-neural verification machine.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ctios.learners.echo_state_learner import EchoStateLearner


@dataclass(frozen=True)
class NeuralDecision:
    prediction: float
    error: float
    uncertainty: float


class NeuralTemporalAgent:
    """Observation-only online neural temporal predictor.

    Contract:
    - deterministic given seed/hyperparameters
    - consumes only observed scalar stream
    - returns prediction/error/uncertainty per step
    """

    def __init__(
        self,
        seed: int = 0,
        dim: int = 64,
        leak: float = 0.3,
        ridge: float = 1e-2,
        prior: float = 1.0,
    ) -> None:
        self._learner = EchoStateLearner(
            dim=dim,
            seed=seed,
            leak=leak,
            ridge=ridge,
            prior=prior,
        )
        self._ema_abs_err = 0.0

    def step(self, observed_interval: float) -> NeuralDecision:
        pred = float(self._learner.predict())
        err = float(observed_interval - pred)
        self._learner.update(float(observed_interval))
        self._ema_abs_err = 0.95 * self._ema_abs_err + 0.05 * abs(err)
        return NeuralDecision(
            prediction=pred,
            error=err,
            uncertainty=float(self._ema_abs_err),
        )

    def run(self, stream: np.ndarray) -> list[NeuralDecision]:
        return [self.step(float(x)) for x in stream]
