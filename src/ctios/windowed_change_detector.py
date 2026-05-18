# SPDX-License-Identifier: MIT
"""ctios.windowed_change_detector — boundary-layer experiment #3.

Negatives #1 (fixed-λ PH) and #2 (calibrated-λ PH) converged on one
root cause: the *observable* — a single re-converging scalar's
|one-step error| — carries its own cold-start transient that no λ can
separate from the rupture. This replaces the observable entirely with a
**stationary two-window standardized contrast on the raw observation**
(no estimator, no re-convergence, no cold-start). Same pinned falsifier
shape, new observable.

Pinned: prereg/windowed_change_detector.yaml. No threshold edited after
results. No biological/cognition/AGI/theory-of-time claim.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ctios.falsify import HypothesisSpec, Verdict, falsify
from ctios.predictive_simulation import RuptureStream

_ROOT = Path(__file__).resolve().parents[2]

_W_SHORT = 20
_W_BASE = 80
_EPS = 1e-6
_WARMUP = _W_BASE + _W_SHORT  # 100: first index with full history
ALPHA = 0.10
TAU = 0.50
_CAL_NULL = range(100, 116)
_EVAL_RUPT = range(0, 12)
_EVAL_NULL = range(200, 212)


def _contrast(obs: np.ndarray) -> np.ndarray:
    """S_t = |mean(short) - mean(base)| / (pooled_std + eps).
    Stationary under null (two windows of the same process); spikes
    when a regime boundary falls between the windows. Index < warmup
    is 0 (insufficient history)."""
    n = obs.size
    s = np.zeros(n, dtype=np.float64)
    for t in range(_WARMUP, n):
        short = obs[t - _W_SHORT:t]
        base = obs[t - _W_BASE - _W_SHORT:t - _W_SHORT]
        pooled = np.sqrt(0.5 * (short.var() + base.var()))
        s[t] = abs(short.mean() - base.mean()) / (pooled + _EPS)
    return s


def _first_cross(obs: np.ndarray, lam: float) -> int:
    s = _contrast(obs)
    idx = np.flatnonzero(s > lam)
    return int(idx[0]) if idx.size else -1


def calibrate_lambda(alpha: float = ALPHA) -> float:
    """λ = (1-α) empirical quantile of per-stream max contrast over the
    held-out null calibration seeds. Fixed rule, no hand-tuning."""
    peaks = [
        float(np.max(_contrast(RuptureStream.make_null(s).obs)))
        for s in _CAL_NULL
    ]
    return float(np.quantile(peaks, 1.0 - alpha))


class WindowedDetector:
    def __init__(self, lam: float) -> None:
        self.lam = lam

    def detect(self, obs: np.ndarray) -> int:
        return _first_cross(obs, self.lam)


class AlwaysFireDetector:
    """Adversarial: 'detects everything' — fires right after warmup."""

    def detect(self, obs: np.ndarray) -> int:
        return _WARMUP + 1


class NeverFireDetector:
    """Adversarial: 'detects nothing'."""

    def detect(self, obs: np.ndarray) -> int:
        return -1


def _rates(det: WindowedDetector | AlwaysFireDetector | NeverFireDetector,
           ) -> tuple[float, float]:
    hits = 0
    for s in _EVAL_RUPT:
        st = RuptureStream.make(s)
        d = det.detect(st.obs)
        if 0 <= d - st.t_star <= int(0.2 * st.obs.size):
            hits += 1
    fa = 0
    for s in _EVAL_NULL:
        if det.detect(RuptureStream.make_null(s).obs) >= 0:
            fa += 1
    return hits / len(_EVAL_RUPT), fa / len(_EVAL_NULL)


def _passes_both(detect_rate: float, null_fa: float) -> bool:
    return detect_rate >= TAU and null_fa <= ALPHA


def run_verdict_metrics(_t: dict[str, float] | None = None) -> dict[str, float]:
    lam = calibrate_lambda()
    dr, fa = _rates(WindowedDetector(lam))
    a_dr, a_fa = _rates(AlwaysFireDetector())
    n_dr, n_fa = _rates(NeverFireDetector())
    return {
        "calib_lambda": lam,
        "eval_null_false_alarm": fa,
        "detect_rate": dr,
        "always_fake_blocked": 0.0 if _passes_both(a_dr, a_fa) else 1.0,
        "never_fake_blocked": 0.0 if _passes_both(n_dr, n_fa) else 1.0,
        "leakage": 0.0,
    }


def _negative_control(_t: dict[str, float]) -> dict[str, float]:
    a_dr, a_fa = _rates(AlwaysFireDetector())
    return {
        "calib_lambda": 0.0,
        "eval_null_false_alarm": a_fa,
        "detect_rate": a_dr,
        "always_fake_blocked": 0.0,
        "never_fake_blocked": 0.0,
        "leakage": 0.0,
    }


def verdict() -> Verdict:
    spec = HypothesisSpec.load(_ROOT / "prereg" / "windowed_change_detector.yaml")
    return falsify(
        spec,
        run_verdict_metrics,
        negative_control=_negative_control,
        evidence_dir=_ROOT / "evidence",
        prereg_dir=_ROOT / "prereg",
    )


def main() -> int:
    v = verdict()
    print(f"WINDOWED-CHANGE-DETECTOR :: {v.status}  [{v.hid}]")
    for k, ok in {**v.checks, **v.battery}.items():
        print(f"  [{'OK' if ok else 'XX'}] {k}")
    import json

    print(f"spec_sha256={v.spec_sha256[:16]}  metrics={json.dumps(v.metrics)}")
    if v.reasons:
        print("reasons: " + "; ".join(v.reasons))
    return 0 if v.status in ("GREEN", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
