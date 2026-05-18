# SPDX-License-Identifier: MIT
"""TemporalAgent — a runnable online adaptive temporal forecaster.

Built from PROVEN components in this repo (no new science, no hypothesis
lineage): a selectable learned backend predicts the next value of a
numeric/interval stream, adapts online from its own prediction error,
flags a regime shift (Page-Hinkley on the error stream, armed after a
warmup so the cold start cannot poison it — the v1→v2 fix), and emits a
simple action. Deterministic given (backend, seed). This is an
engineering tool over a stream — explicitly NOT cognition / AGI; the
measured capability on hard regime tasks is modest (see v9).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

from ctios.agents import LearnedAgent
from ctios.drift import PageHinkley
from ctios.learners.echo_state_learner import EchoStateLearner

BACKENDS = ("echo_state", "adaptive")


@dataclass(frozen=True)
class Decision:
    step: int
    prediction: float
    observed: float
    error: float
    regime_shift: bool
    action: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class TemporalAgent:
    """Online: predict() -> observe(x) -> Decision. Adapts every step."""

    def __init__(
        self,
        backend: str = "echo_state",
        *,
        prior: float = 1.0,
        seed: int = 0,
        dim: int = 64,
        warmup: int = 60,
        ph_delta: float = 0.2,
        ph_lambda: float = 8.0,
    ) -> None:
        if backend not in BACKENDS:
            raise ValueError(f"backend must be one of {BACKENDS}, got {backend!r}")
        self.backend = backend
        self.warmup = warmup
        self._n = 0
        self._pred = prior
        if backend == "adaptive":
            self._la: LearnedAgent | None = LearnedAgent(prior=prior, warmup=warmup)
            self._es: EchoStateLearner | None = None
        else:
            self._la = None
            self._es = EchoStateLearner(dim=dim, seed=seed, prior=prior)
        self._ph = PageHinkley(ph_delta, ph_lambda)
        self._ph_armed = False

    def predict(self) -> float:
        self._pred = (
            self._la.predict() if self._la is not None
            else self._es.predict()  # type: ignore[union-attr]
        )
        return self._pred

    def observe(self, x: float) -> Decision:
        x = float(x)
        err = x - self._pred
        self._n += 1
        if self._la is not None:
            self._la.update(x)
            shift = self._la.drift_flag()
        else:
            self._es.update(x)  # type: ignore[union-attr]
            shift = False
            if self._n > self.warmup:
                if not self._ph_armed:
                    self._ph.reset()
                    self._ph_armed = True
                elif self._ph.update(err):
                    shift = True
                    self._ph.reset()
        action = "adapt-alert" if shift else "observe"
        return Decision(self._n - 1, self._pred, x, err, shift, action)

    def run(self, stream: Iterable[float]) -> list[Decision]:
        out: list[Decision] = []
        for x in stream:
            self.predict()
            out.append(self.observe(x))
        return out
