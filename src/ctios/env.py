"""Temporal environment with a hidden interval and a step change at T*.

Structural no-leakage guarantee
-------------------------------
The hidden parameters (tau0, tau1, t_star, sigma) live ONLY inside the
private ``_HiddenSchedule``. ``Environment.step`` returns an
``Observation`` whose fields are exactly ``step`` and ``observed_interval``
(the noisy realised inter-event interval — a quantity any observer in the
world could time with a stopwatch). No hidden parameter is ever placed in
an ``Observation``. The oracle is the *only* consumer of the hidden
schedule, and it is constructed from it explicitly and on purpose, as the
achievable upper bound. Learning/baseline agents are never handed the
schedule object — enforced by ``tests/test_no_leakage.py``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ctios.utils import rng


@dataclass(frozen=True)
class Observation:
    """Everything an agent is allowed to perceive at one step."""

    step: int
    observed_interval: float


class _HiddenSchedule:
    """Private. Holds the parameters no learning agent may see."""

    __slots__ = ("tau0", "tau1", "t_star", "sigma", "_rng")

    def __init__(self, tau0: float, tau1: float, t_star: int, sigma: float, seed: int):
        self.tau0 = tau0
        self.tau1 = tau1
        self.t_star = t_star
        self.sigma = sigma
        self._rng = rng(seed)

    def mean_interval(self, step: int) -> float:
        return self.tau0 if step < self.t_star else self.tau1

    def sample(self, step: int) -> float:
        return float(self.mean_interval(step) + self._rng.normal(0.0, self.sigma))


class Environment:
    """Deterministic-replay temporal source with a hidden regime shift."""

    def __init__(
        self,
        tau0: float,
        tau1: float,
        t_star: int,
        sigma: float,
        n_steps: int,
        seed: int,
    ):
        self.n_steps = n_steps
        self.seed = seed
        self._hidden = _HiddenSchedule(tau0, tau1, t_star, sigma, seed)
        self._step = 0

    # --- public surface visible to agents -------------------------------
    def reset(self) -> None:
        self._hidden = _HiddenSchedule(
            self._hidden.tau0,
            self._hidden.tau1,
            self._hidden.t_star,
            self._hidden.sigma,
            self.seed,
        )
        self._step = 0

    def step(self) -> Observation:
        x = self._hidden.sample(self._step)
        obs = Observation(step=self._step, observed_interval=x)
        self._step += 1
        return obs

    # --- evaluation-only channel (NEVER passed to learning agents) ------
    def eval_true_mean(self, step: int) -> float:
        return self._hidden.mean_interval(step)

    @property
    def t_star(self) -> int:
        return self._hidden.t_star

    def oracle_view(self) -> _HiddenSchedule:
        """Explicitly hand the schedule to the oracle (upper bound only)."""
        return self._hidden

    def hidden_provenance(self) -> dict[str, str]:
        """sha256 of each hidden parameter salted by seed.

        Logs provenance (proves the run used the declared schedule) WITHOUT
        revealing the value — closes critique §7.2 with no leakage.
        """
        import hashlib

        def h(v: float | int) -> str:
            return hashlib.sha256(f"{v}:{self.seed}".encode()).hexdigest()

        return {
            "tau0_hidden_hash": h(self._hidden.tau0),
            "tau1_hidden_hash": h(self._hidden.tau1),
            "T_star_hidden_hash": h(self._hidden.t_star),
        }


def true_mean_series(env: Environment) -> np.ndarray:
    return np.array([env.eval_true_mean(k) for k in range(env.n_steps)], dtype=float)
