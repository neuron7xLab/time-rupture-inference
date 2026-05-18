# SPDX-License-Identifier: MIT
"""ctios.benchmark_families — deterministic numpy-only interval families.

Broadens the single hidden-rupture toy into a portfolio so a claim
scoped to one generative assumption cannot silently ride on it
elsewhere. Every family is seed-deterministic (replay hash stable) and
carries its own ``expected_failure_modes`` and
``admissible_claim_boundary`` — the boundary is data, not prose.

No real-world-validity claim: these remain synthetic families.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class FamilySample:
    family_id: str
    seed: int
    intervals: np.ndarray
    metadata: dict[str, object] = field(default_factory=dict)

    def replay_hash(self) -> str:
        h = hashlib.sha256()
        h.update(self.family_id.encode())
        h.update(np.asarray(self.intervals, dtype=np.float64).tobytes())
        return h.hexdigest()


class BenchmarkFamily:
    family_id: str = "base"
    expected_failure_modes: tuple[str, ...] = ()
    admissible_claim_boundary: str = ""

    def __init__(self, seed: int = 0, n: int = 600) -> None:
        self.seed = int(seed)
        self.n = int(n)

    def _rng(self) -> np.random.Generator:
        return np.random.default_rng(self.seed)

    def generate(self) -> FamilySample:  # pragma: no cover - overridden
        raise NotImplementedError

    def _wrap(self, x: np.ndarray, **meta: object) -> FamilySample:
        return FamilySample(
            self.family_id, self.seed, np.asarray(x, dtype=np.float64),
            {"n": self.n, **meta},
        )


class NullNoRuptureFamily(BenchmarkFamily):
    family_id = "null_no_rupture"
    expected_failure_modes = ("false_rupture_detection",)
    admissible_claim_boundary = (
        "a rupture-specific claim must NOT go GREEN here (no rupture exists)"
    )

    def generate(self) -> FamilySample:
        r = self._rng()
        return self._wrap(r.normal(10.0, 1.0, self.n), rupture=False)


class SingleRuptureGaussianFamily(BenchmarkFamily):
    family_id = "single_rupture_gaussian"
    expected_failure_modes = ("miss_post_rupture_adaptation",)
    admissible_claim_boundary = "the canonical scoped positive lives here only"

    def generate(self) -> FamilySample:
        r = self._rng()
        t = self.n // 2
        x = np.concatenate(
            [r.normal(10.0, 1.0, t), r.normal(4.0, 1.0, self.n - t)]
        )
        return self._wrap(x, rupture=True, t_star=t)


class HeavyTailRuptureFamily(BenchmarkFamily):
    family_id = "heavy_tail_rupture"
    expected_failure_modes = ("gaussian_only_assumption_breaks",)
    admissible_claim_boundary = (
        "Gaussian-noise assumptions are inadmissible on Student-t tails"
    )

    def generate(self) -> FamilySample:
        r = self._rng()
        t = self.n // 2
        x = np.concatenate(
            [10.0 + r.standard_t(2.5, t), 4.0 + r.standard_t(2.5, self.n - t)]
        )
        return self._wrap(x, rupture=True, t_star=t, tail="student_t_df2.5")


class MultiRegimeRuptureFamily(BenchmarkFamily):
    family_id = "multi_regime_rupture"
    expected_failure_modes = ("single_shift_assumption_breaks",)
    admissible_claim_boundary = "single-rupture estimators are out of scope here"

    def generate(self) -> FamilySample:
        r = self._rng()
        q = self.n // 4
        segs = [r.normal(m, 1.0, q) for m in (10.0, 4.0, 8.0, 2.0)]
        x = np.concatenate(segs)[: self.n]
        return self._wrap(x, rupture=True, regimes=4)


class CarrierConfoundedRuptureFamily(BenchmarkFamily):
    family_id = "carrier_confounded_rupture"
    expected_failure_modes = ("carrier_shortcut_passes_without_signal",)
    admissible_claim_boundary = (
        "a probe exploiting the carrier, not the rupture, must fail"
    )

    def generate(self) -> FamilySample:
        r = self._rng()
        t = self.n // 2
        carrier = np.sin(np.arange(self.n) / 7.0) * 3.0
        sig = np.concatenate(
            [r.normal(10.0, 1.0, t), r.normal(4.0, 1.0, self.n - t)]
        )
        return self._wrap(
            sig + carrier, rupture=True, t_star=t, carrier="sin/7*3"
        )


class ContextualRuptureFamily(BenchmarkFamily):
    family_id = "contextual_rupture"
    expected_failure_modes = ("context_aliased_future_misread",)
    admissible_claim_boundary = (
        "identical windows aliasing opposite futures — no peeking allowed"
    )

    def generate(self) -> FamilySample:
        r = self._rng()
        z = r.integers(0, 2, self.n)
        x = np.where(z == 0, r.normal(10.0, 1.0, self.n),
                     r.normal(4.0, 1.0, self.n))
        return self._wrap(x, rupture=True, hidden_context=True)


class MultimodalIntervalFamily(BenchmarkFamily):
    family_id = "multimodal_interval"
    expected_failure_modes = ("unimodal_assumption_breaks",)
    admissible_claim_boundary = (
        "mean-based estimators are inadmissible on a bimodal interval"
    )

    def generate(self) -> FamilySample:
        r = self._rng()
        pick = r.integers(0, 2, self.n)
        x = np.where(pick == 0, r.normal(3.0, 0.5, self.n),
                     r.normal(12.0, 0.5, self.n))
        return self._wrap(x, rupture=False, modes=2)


def all_benchmark_families(seed: int = 0) -> list[BenchmarkFamily]:
    return [
        NullNoRuptureFamily(seed),
        SingleRuptureGaussianFamily(seed),
        HeavyTailRuptureFamily(seed),
        MultiRegimeRuptureFamily(seed),
        CarrierConfoundedRuptureFamily(seed),
        ContextualRuptureFamily(seed),
        MultimodalIntervalFamily(seed),
    ]
