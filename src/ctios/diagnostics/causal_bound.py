# SPDX-License-Identifier: MIT
"""Analytic causal lower bound on history_to_regime_distance.

One hidden context flip + a cold prior force unavoidable wrong-sign
triggers for ANY causal oracle (the flip is unobservable until its first
post-flip trigger is realized). This derives, BEFORE running any oracle,
the minimum attainable h2r — so a v8.3 failure can be attributed to a
benchmark-parameterization boundary rather than an oracle bug.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CausalBound:
    triggers_per_seed: int
    expected_forced_wrong: float
    regime_trigger_floor: float
    history_trigger_mae_min: float
    h2r_causal_min: float
    attainable_at_0_35: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "triggers_per_seed": self.triggers_per_seed,
            "expected_forced_wrong": self.expected_forced_wrong,
            "regime_trigger_floor": self.regime_trigger_floor,
            "history_trigger_mae_min": self.history_trigger_mae_min,
            "h2r_causal_min": self.h2r_causal_min,
            "attainable_at_0_35": self.attainable_at_0_35,
        }


def derive(cfg: dict[str, Any]) -> CausalBound:
    n = int(cfg["n_steps"])
    period = int(cfg["period"])
    delta = float(cfg["delta"])
    sigma = float(cfg["sigma"])
    t = sum(1 for k in range(n) if k % period == 3)
    # cold prior wrong with prob 0.5; the one post-flip trigger always
    # wrong until observed -> expected unavoidable wrong = 0.5 + 1.0.
    forced = 1.5
    floor = sigma * math.sqrt(2.0 / math.pi)        # E|N(0,sigma)|
    wrong_err = 2.0 * delta                          # predict -sign*delta
    hist_min = ((t - forced) * floor + forced * wrong_err) / t
    h2r_min = (hist_min - floor) / floor if floor > 0 else float("inf")
    return CausalBound(
        triggers_per_seed=t,
        expected_forced_wrong=forced,
        regime_trigger_floor=floor,
        history_trigger_mae_min=hist_min,
        h2r_causal_min=h2r_min,
        attainable_at_0_35=h2r_min <= 0.35,
    )
