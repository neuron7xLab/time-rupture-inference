# SPDX-License-Identifier: MIT
"""Agents. Learning/baseline agents receive only ``Observation``.

The benchmark-scoped adaptation claim (operational, NOT cognition) lives
entirely in ``LearnedAgent``: it is never told tau0/tau1/T*; it must
infer the interval from its own prediction error and re-adapt after the
hidden shift. Every ablation removes exactly one mechanism so necessity
(not mere presence) is testable.
"""

from __future__ import annotations

from collections import deque
from typing import Protocol

import numpy as np

from ctios.drift import PageHinkley
from ctios.env import _HiddenSchedule


class Agent(Protocol):
    name: str

    def predict(self) -> float: ...
    def update(self, observed_interval: float) -> None: ...
    def drift_flag(self) -> bool: ...


class _Base:
    name = "base"

    def drift_flag(self) -> bool:
        return False


class LastIntervalAgent(_Base):
    name = "last_interval"

    def __init__(self, prior: float = 1.0):
        self._last = prior

    def predict(self) -> float:
        return self._last

    def update(self, observed_interval: float) -> None:
        self._last = observed_interval


class MovingAverageAgent(_Base):
    def __init__(self, window: int, prior: float = 1.0):
        self.name = f"moving_average_w{window}"
        self._buf: deque[float] = deque(maxlen=window)
        self._prior = prior

    def predict(self) -> float:
        return float(np.mean(self._buf)) if self._buf else self._prior

    def update(self, observed_interval: float) -> None:
        self._buf.append(observed_interval)


class ExpSmoothingAgent(_Base):
    def __init__(self, alpha: float, prior: float = 1.0):
        self.name = f"exp_smoothing_a{alpha}"
        self.alpha = alpha
        self._m = prior
        self._init = False

    def predict(self) -> float:
        return self._m

    def update(self, observed_interval: float) -> None:
        if not self._init:
            self._m = observed_interval
            self._init = True
        else:
            self._m += self.alpha * (observed_interval - self._m)


class RandomAgent(_Base):
    name = "random"

    def __init__(self, seed: int, lo: float, hi: float):
        self._rng = np.random.default_rng(seed)
        self.lo, self.hi = lo, hi

    def predict(self) -> float:
        return float(self._rng.uniform(self.lo, self.hi))

    def update(self, observed_interval: float) -> None:
        return None


class InjectedAgent(_Base):
    """Hard-wired with tau0. Optimal pre-shift, must fail post-shift."""

    name = "injected"

    def __init__(self, tau0: float):
        self._tau0 = tau0

    def predict(self) -> float:
        return self._tau0

    def update(self, observed_interval: float) -> None:
        return None  # by design: no adaptation


class OracleAgent(_Base):
    """Knows the hidden schedule. Achievable upper bound (regret = 0)."""

    name = "oracle"

    def __init__(self, hidden: _HiddenSchedule):
        self._h = hidden
        self._step = 0

    def predict(self) -> float:
        return self._h.mean_interval(self._step)

    def update(self, observed_interval: float) -> None:
        self._step += 1


class LearnedAgent(_Base):
    """Adaptive interval estimator with drift-triggered gain boost.

    Mechanisms (each independently ablatable):
      * memory      : recursive estimate of the interval
      * update      : online error-driven correction
      * drift       : Page-Hinkley on error -> transient high-gain recovery
      * post_shift  : whether updates are allowed to continue after warmup
      * anti_divergence : OPT-IN local gain damping on oscillating/sign-
        flipping error. Default OFF — enabling it changes the update law
        and therefore the FROZEN v4 number; it is a separate pre-registered
        improvement line, never folded silently into the v4 baseline.
    """

    name = "learned_full"

    def __init__(
        self,
        base_gain: float = 0.06,
        boost_gain: float = 0.55,
        boost_steps: int = 18,
        ph_delta: float = 0.2,
        ph_lambda: float = 8.0,
        prior: float = 1.0,
        *,
        use_memory: bool = True,
        use_update: bool = True,
        use_drift: bool = True,
        post_shift_update: bool = True,
        warmup: int = 60,
        anti_divergence: bool = False,
        min_gain_scale: float = 0.35,
    ):
        if not 0.0 < base_gain <= 1.0:
            raise ValueError("base_gain must be in (0, 1]")
        if not 0.0 < boost_gain <= 1.0:
            raise ValueError("boost_gain must be in (0, 1]")
        if boost_steps < 0:
            raise ValueError("boost_steps must be >= 0")
        if warmup < 0:
            raise ValueError("warmup must be >= 0")
        if not 0.0 < min_gain_scale <= 1.0:
            raise ValueError("min_gain_scale must be in (0, 1]")

        self.base_gain = base_gain
        self.boost_gain = boost_gain
        self.boost_steps = boost_steps
        self._ph = PageHinkley(ph_delta, ph_lambda)
        self._m = prior
        self._last = prior
        self._pred = prior
        self._boost_left = 0
        self._n = 0
        self._drift = False
        self._ph_armed = False
        self.use_memory = use_memory
        self.use_update = use_update
        self.use_drift = use_drift
        self.post_shift_update = post_shift_update
        self.warmup = warmup
        self.anti_divergence = anti_divergence
        self.min_gain_scale = min_gain_scale
        self._prev_err = 0.0

    def predict(self) -> float:
        self._pred = self._m if self.use_memory else self._last
        return self._pred

    def drift_flag(self) -> bool:
        return self._drift

    def update(self, observed_interval: float) -> None:
        self._n += 1
        err = observed_interval - self._pred
        self._last = observed_interval
        self._drift = False

        if not self.use_update:
            return
        if not self.post_shift_update and self._n > self.warmup:
            return

        # Arm Page-Hinkley only AFTER warmup and re-baseline it on the
        # converged-error regime, so the cold-start transient (prior far
        # from the true interval) cannot poison the drift baseline.
        # (v1 RED root cause — see evidence/NEGATIVE_RESULT_v1.md.)
        if self.use_drift and self._n > self.warmup:
            if not self._ph_armed:
                self._ph.reset()
                self._ph_armed = True
            elif self._ph.update(err):
                self._drift = True
                self._boost_left = self.boost_steps
                self._ph.reset()

        gain = self.base_gain
        if self._boost_left > 0:
            gain = self.boost_gain
            self._boost_left -= 1

        # Opt-in convergence guard: if error flips sign and grows, damp
        # gain to avoid overshoot-driven divergence around a new regime.
        if self.anti_divergence:
            prev_mag = abs(self._prev_err)
            curr_mag = abs(err)
            if self._prev_err * err < 0.0 and curr_mag > prev_mag:
                if prev_mag > 1e-9:
                    scale = max(self.min_gain_scale, min(1.0, prev_mag / curr_mag))
                else:
                    scale = self.min_gain_scale
                gain *= scale

        self._m += gain * err
        self._prev_err = err


def make_ablations(prior: float) -> dict[str, LearnedAgent]:
    variants: dict[str, dict[str, bool]] = {
        "learned_no_update": {"use_update": False},
        "learned_no_drift": {"use_drift": False},
        "learned_no_memory": {"use_memory": False},
        "learned_frozen_post_shift": {"post_shift_update": False},
    }
    return {name: LearnedAgent(prior=prior, **kw) for name, kw in variants.items()}
