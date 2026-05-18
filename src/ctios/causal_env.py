# SPDX-License-Identifier: MIT
"""Action-conditioned temporal environment (v5 minimal causal line).

Adds the smallest possible causal channel on top of the v4 rupture: a
regime shift at ``t_star`` ALSO raises observation volatility. An action
can modulate that volatility — but only in ``interventional`` mode.

Invariants (proved in tests/test_causal_env.py):
  * same seed + same action sequence  -> identical trajectory
  * action_null mode                  -> trajectory independent of action
  * interventional mode               -> trajectory differs across policies
  * Observation never exposes a hidden parameter
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np

ACTIONS = ("observe", "stabilize", "destabilize")


@dataclass(frozen=True)
class CausalObservation:
    step: int
    observed_interval: float
    previous_action: str | None
    previous_error: float | None


class _HiddenCausalState:
    """Private. Nothing here ever reaches an agent."""

    __slots__ = ("tau0", "tau1", "t_star", "sigma", "vol_mult", "_rng")

    def __init__(self, tau0, tau1, t_star, sigma, vol_mult, seed):
        self.tau0 = tau0
        self.tau1 = tau1
        self.t_star = t_star
        self.sigma = sigma
        self.vol_mult = vol_mult
        self._rng = np.random.default_rng(seed)

    def mean_tau(self, step: int) -> float:
        return self.tau0 if step < self.t_star else self.tau1

    def base_sigma(self, step: int) -> float:
        # rupture also makes the world noisier — that is what an action
        # can causally fight against.
        return self.sigma if step < self.t_star else self.sigma * self.vol_mult


class CausalEnvironment:
    def __init__(
        self,
        tau0: float,
        tau1: float,
        t_star: int,
        sigma: float,
        n_steps: int,
        seed: int,
        mode: str = "interventional",
        vol_mult: float = 3.0,
    ):
        if mode not in ("action_null", "interventional"):
            raise ValueError(f"bad mode {mode!r}")
        self.n_steps = n_steps
        self.seed = seed
        self.mode = mode
        self._init = (tau0, tau1, t_star, sigma, vol_mult, seed)
        self._h = _HiddenCausalState(*self._init)
        self._step = 0
        self._effect = 0.0  # stabilization level in [-1, 1]
        self._prev_action: str | None = None
        self._prev_error: float | None = None

    def reset(self) -> None:
        self._h = _HiddenCausalState(*self._init)
        self._step = 0
        self._effect = 0.0
        self._prev_action = None
        self._prev_error = None

    def _apply_action(self, action: str) -> None:
        if self.mode == "action_null":
            return  # actions logged, never modify dynamics
        if action == "stabilize":
            self._effect = min(1.0, self._effect + 0.25)
        elif action == "destabilize":
            self._effect = max(-1.0, self._effect - 0.25)
        else:  # observe -> decay toward neutral
            self._effect *= 0.9

    def _effective_sigma(self, step: int) -> float:
        base = self._h.base_sigma(step)
        if self.mode == "action_null":
            return base
        # effect>0 (stabilize) shrinks noise; effect<0 (destabilize) grows it
        return base * math.exp(-0.8 * self._effect)

    def step(self, action: str = "observe") -> CausalObservation:
        if action not in ACTIONS:
            raise ValueError(f"bad action {action!r}")
        self._apply_action(action)
        eff_sigma = self._effective_sigma(self._step)
        x = float(self._h.mean_tau(self._step) + self._h._rng.normal(0.0, eff_sigma))
        obs = CausalObservation(
            step=self._step,
            observed_interval=x,
            previous_action=self._prev_action,
            previous_error=self._prev_error,
        )
        self._prev_action = action
        self._step += 1
        return obs

    def record_error(self, error: float) -> None:
        self._prev_error = error

    @property
    def t_star(self) -> int:
        return self._h.t_star

    def hidden_provenance(self) -> dict[str, str]:
        def h(v) -> str:
            return hashlib.sha256(f"{v}:{self.seed}:{self.mode}".encode()).hexdigest()

        return {
            "tau0_hidden_hash": h(self._h.tau0),
            "tau1_hidden_hash": h(self._h.tau1),
            "T_star_hidden_hash": h(self._h.t_star),
        }
