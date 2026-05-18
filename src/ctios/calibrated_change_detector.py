# SPDX-License-Identifier: MIT
"""ctios.calibrated_change_detector — closes the falsified boundary.

The predictive-simulation PARTIAL (PR #24) localised the failure to the
detection layer: a fixed-λ Page-Hinkley statistic false-alarms at 0.75
on no-rupture streams. This module tests one corrected mechanism: a
detector whose λ is *calibrated* to a pinned false-alarm bound on a
HELD-OUT null set, then evaluated on disjoint streams. It must beat
both degenerate fakes (detect-everything / detect-nothing).

Pinned falsifier: prereg/calibrated_change_detector.yaml. No threshold
edited after results. No biological/cognition/AGI/theory-of-time claim.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ctios.falsify import HypothesisSpec, Verdict, falsify
from ctios.predictive_simulation import RuptureStream

_ROOT = Path(__file__).resolve().parents[2]

_GAIN = 0.18
_WARMUP = 40
_DELTA = 0.05
ALPHA = 0.10
TAU = 0.50
_CAL_NULL = range(100, 116)   # held-out calibration null seeds
_EVAL_RUPT = range(0, 12)     # disjoint evaluation rupture seeds
_EVAL_NULL = range(200, 212)  # disjoint evaluation null seeds


def _ph_track(obs: np.ndarray) -> np.ndarray:
    """Per-step Page-Hinkley statistic (cum - running min) on |one-step
    prediction error|, frozen reference mean over the warmup window.
    Returns the statistic series; index < warmup is 0."""
    m = 0.0
    ref = 0.0
    cum = 0.0
    mn = 0.0
    stat = np.zeros(obs.size, dtype=np.float64)
    for t, o in enumerate(obs):
        pred = m if t > 0 else float(o)
        err = float(o) - pred
        m = pred + _GAIN * err
        ae = abs(err)
        n = t + 1
        if n <= _WARMUP:
            ref += (ae - ref) / n
            if n == _WARMUP:
                cum = 0.0
                mn = 0.0
            continue
        cum += ae - ref - _DELTA
        mn = min(mn, cum)
        stat[t] = cum - mn
    return stat


def _ph_max(obs: np.ndarray) -> float:
    return float(np.max(_ph_track(obs)))


def _first_cross(obs: np.ndarray, lam: float) -> int:
    s = _ph_track(obs)
    idx = np.flatnonzero(s > lam)
    return int(idx[0]) if idx.size else -1


def calibrate_lambda(alpha: float = ALPHA) -> float:
    """λ = (1-α) empirical quantile of per-stream max-PH over the
    held-out null calibration seeds. Fixed rule, no hand-tuning."""
    peaks = [_ph_max(RuptureStream.make_null(s).obs) for s in _CAL_NULL]
    return float(np.quantile(peaks, 1.0 - alpha))


class CalibratedDetector:
    def __init__(self, lam: float) -> None:
        self.lam = lam

    def detect(self, obs: np.ndarray) -> int:
        return _first_cross(obs, self.lam)


class AlwaysFireDetector:
    """Adversarial: 'detects everything' — fires right after warmup on
    every stream. High detect_rate, null_fa = 1.0."""

    def detect(self, obs: np.ndarray) -> int:
        return _WARMUP + 1


class NeverFireDetector:
    """Adversarial: 'detects nothing' — null_fa = 0, detect_rate = 0."""

    def detect(self, obs: np.ndarray) -> int:
        return -1


def _rates(det: CalibratedDetector | AlwaysFireDetector | NeverFireDetector,
           ) -> tuple[float, float]:
    """(detect_rate on disjoint rupture eval, null_fa on disjoint null
    eval). Detection hit window [t*, t*+0.2n]."""
    hits = 0
    for s in _EVAL_RUPT:
        st = RuptureStream.make(s)
        d = det.detect(st.obs)
        if 0 <= d - st.t_star <= int(0.2 * st.obs.size):
            hits += 1
    fa = 0
    for s in _EVAL_NULL:
        d = det.detect(RuptureStream.make_null(s).obs)
        if d >= 0:
            fa += 1
    return hits / len(_EVAL_RUPT), fa / len(_EVAL_NULL)


def _passes_both(detect_rate: float, null_fa: float) -> bool:
    return detect_rate >= TAU and null_fa <= ALPHA


def run_verdict_metrics(_t: dict[str, float] | None = None) -> dict[str, float]:
    lam = calibrate_lambda()
    dr, fa = _rates(CalibratedDetector(lam))
    a_dr, a_fa = _rates(AlwaysFireDetector())
    n_dr, n_fa = _rates(NeverFireDetector())
    return {
        "calib_lambda": lam,
        "eval_null_false_alarm": fa,
        "detect_rate": dr,
        # a fake is "blocked" iff it does NOT pass both pinned checks
        "always_fake_blocked": 0.0 if _passes_both(a_dr, a_fa) else 1.0,
        "never_fake_blocked": 0.0 if _passes_both(n_dr, n_fa) else 1.0,
        "leakage": 0.0,  # structural: detectors see only obs
    }


def _negative_control(_t: dict[str, float]) -> dict[str, float]:
    """The always-fire fake as the engine's negative control: it must
    fail the pinned checks (eval_null_false_alarm = 1.0)."""
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
    spec = HypothesisSpec.load(_ROOT / "prereg" / "calibrated_change_detector.yaml")
    return falsify(
        spec,
        run_verdict_metrics,
        negative_control=_negative_control,
        evidence_dir=_ROOT / "evidence",
        prereg_dir=_ROOT / "prereg",
    )


def main() -> int:
    v = verdict()
    print(f"CALIBRATED-CHANGE-DETECTOR :: {v.status}  [{v.hid}]")
    for k, ok in {**v.checks, **v.battery}.items():
        print(f"  [{'OK' if ok else 'XX'}] {k}")
    import json

    print(f"spec_sha256={v.spec_sha256[:16]}  metrics={json.dumps(v.metrics)}")
    if v.reasons:
        print("reasons: " + "; ".join(v.reasons))
    return 0 if v.status in ("GREEN", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
