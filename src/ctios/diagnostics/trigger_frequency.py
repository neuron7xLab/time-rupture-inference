# SPDX-License-Identifier: MIT
"""Closed-form trigger-frequency derivation for v8.1.

Construction B uses a deterministic period schedule, so the trigger
count is EXACT (not stochastic) and is derived BEFORE the oracle
diagnostic runs. If the derived frequency fails the pinned minimums the
diagnostic must not run (RED_PRECHECK).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FrequencyDerivation:
    expected_trigger_probability: float
    expected_trigger_count_per_seed: int
    expected_trigger_count_total_grid: int
    expected_same_observation_different_future_rate: float
    expected_aliasing_rate: float
    minimum_required_trigger_count: int
    frequency_precheck_passed: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "expected_trigger_probability": self.expected_trigger_probability,
            "expected_trigger_count_per_seed": self.expected_trigger_count_per_seed,
            "expected_trigger_count_total_grid": self.expected_trigger_count_total_grid,
            "expected_same_observation_different_future_rate": (
                self.expected_same_observation_different_future_rate
            ),
            "expected_aliasing_rate": self.expected_aliasing_rate,
            "minimum_required_trigger_count": self.minimum_required_trigger_count,
            "frequency_precheck_passed": self.frequency_precheck_passed,
        }


def derive(cfg: dict[str, Any]) -> FrequencyDerivation:
    n = int(cfg["n_steps"])
    period = int(cfg["period"])
    seeds = int(cfg["seed_count"])
    min_total = int(cfg["min_trigger_count_total"])
    min_alias = float(cfg["min_aliasing_rate"])
    min_sodf = float(cfg["min_same_obs_diff_future_rate"])

    # deterministic schedule: trigger at every k with k % period == 3
    per_seed = sum(1 for k in range(n) if k % period == 3)
    total = per_seed * seeds
    prob = per_seed / n
    aliasing = prob  # one trigger step per period block
    # both hidden contexts occur across the grid (random z0 per seed +
    # mid-run flip), so every aliased window has an opposite-future
    # counterpart -> rate is 1.0 by construction.
    sodf = 1.0
    passed = (
        total >= min_total
        and aliasing > min_alias
        and sodf > min_sodf
    )
    return FrequencyDerivation(
        expected_trigger_probability=prob,
        expected_trigger_count_per_seed=per_seed,
        expected_trigger_count_total_grid=total,
        expected_same_observation_different_future_rate=sodf,
        expected_aliasing_rate=aliasing,
        minimum_required_trigger_count=min_total,
        frequency_precheck_passed=passed,
    )
