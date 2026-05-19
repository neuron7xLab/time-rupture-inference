# SPDX-License-Identifier: MIT
"""ctios.carrier_robust_observable — closes #27's carrier-confound cell.

#27's boundary map showed the mean two-window contrast was defeated by
an additive bounded carrier (fire=1.00, detect=0.00 — confident alarm,
wrong reason). New root cause: confound-robustness, not the #24/#25
observable cold-start. This replaces the observable with a WIDE
median/MAD two-window contrast — robust to a bounded low-frequency
carrier WITHOUT knowing its period (windows chosen a priori as "wide
enough", never fitted to the carrier).

Pinned: prereg/carrier_robust_observable.yaml. No threshold edited
after results. No biological / cognition / AGI / theory-of-time claim
is made (boundary stated, not asserted).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ctios.benchmark_families import (
    CarrierConfoundedRuptureFamily,
    NullNoRuptureFamily,
    SingleRuptureGaussianFamily,
)
from ctios.change_detection import (
    first_crossing,
    median_mad_contrast,
    quantile_calibrated_threshold,
)
from ctios.falsify import HypothesisSpec, Verdict, falsify

_ROOT = Path(__file__).resolve().parents[2]
_W_SHORT = 60
_W_BASE = 180
_EPS = 1e-6
_WARMUP = _W_BASE + _W_SHORT  # 240
ALPHA = 0.10
TAU = 0.50
_CAL_NULL = range(100, 116)
_EVAL = range(0, 12)


# The #28 observable, expressed via the shared primitive
# (byte-identical: median/MAD wide two-window contrast).
_CONTRAST = median_mad_contrast(_W_SHORT, _W_BASE)


def _contrast(obs: np.ndarray) -> np.ndarray:
    return _CONTRAST(np.asarray(obs, dtype=np.float64))


def _first_cross(obs: np.ndarray, lam: float) -> int:
    return first_crossing(_contrast(obs), lam)


def calibrate_lambda(alpha: float = ALPHA) -> float:
    return quantile_calibrated_threshold(_CONTRAST, _CAL_NULL, alpha)


class CarrierRobustDetector:
    def __init__(self, lam: float) -> None:
        self.lam = lam

    def detect(self, obs: np.ndarray) -> int:
        return _first_cross(obs, self.lam)


class _AlwaysFire:
    def detect(self, obs: np.ndarray) -> int:
        return _WARMUP + 1


class _NeverFire:
    def detect(self, obs: np.ndarray) -> int:
        return -1


def _detect_rate(det: object, fam_cls: type) -> float:
    hits = 0
    for s in _EVAL:
        smp = fam_cls(seed=s).generate()
        obs = np.asarray(smp.intervals, dtype=np.float64)
        t = smp.metadata.get("t_star")
        d = det.detect(obs)  # type: ignore[attr-defined]
        if isinstance(t, int) and 0 <= d - t <= int(0.2 * obs.size):
            hits += 1
    return hits / len(_EVAL)


def _null_fa(det: object) -> float:
    fa = 0
    for s in _EVAL:
        obs = np.asarray(
            NullNoRuptureFamily(seed=s).generate().intervals, np.float64
        )
        if det.detect(obs) >= 0:  # type: ignore[attr-defined]
            fa += 1
    return fa / len(_EVAL)


def _gates(det: object) -> tuple[float, float, float]:
    return (
        _detect_rate(det, CarrierConfoundedRuptureFamily),
        _null_fa(det),
        _detect_rate(det, SingleRuptureGaussianFamily),
    )


def _passes(cdr: float, fa: float, gdr: float) -> bool:
    return cdr >= TAU and fa <= ALPHA and gdr >= TAU


def run_verdict_metrics(_t: dict[str, float] | None = None) -> dict[str, float]:
    lam = calibrate_lambda()
    cdr, fa, gdr = _gates(CarrierRobustDetector(lam))
    a = _gates(_AlwaysFire())
    n = _gates(_NeverFire())
    return {
        "calib_lambda": lam,
        "carrier_detect_rate": cdr,
        "null_family_false_alarm": fa,
        "gaussian_detect_rate": gdr,
        "always_fake_blocked": 0.0 if _passes(*a) else 1.0,
        "never_fake_blocked": 0.0 if _passes(*n) else 1.0,
        "leakage": 0.0,
    }


def _negative_control(_t: dict[str, float]) -> dict[str, float]:
    a_cdr, a_fa, a_gdr = _gates(_AlwaysFire())
    return {
        "calib_lambda": 0.0,
        "carrier_detect_rate": a_cdr,
        "null_family_false_alarm": a_fa,
        "gaussian_detect_rate": a_gdr,
        "always_fake_blocked": 0.0,
        "never_fake_blocked": 0.0,
        "leakage": 0.0,
    }


def verdict() -> Verdict:
    spec = HypothesisSpec.load(
        _ROOT / "prereg" / "carrier_robust_observable.yaml"
    )
    return falsify(
        spec,
        run_verdict_metrics,
        negative_control=_negative_control,
        evidence_dir=_ROOT / "evidence",
        prereg_dir=_ROOT / "prereg",
    )


def main() -> int:
    v = verdict()
    print(f"CARRIER-ROBUST-OBSERVABLE :: {v.status}  [{v.hid}]")
    for k, ok in {**v.checks, **v.battery}.items():
        print(f"  [{'OK' if ok else 'XX'}] {k}")
    print(f"spec_sha256={v.spec_sha256[:16]}  metrics={json.dumps(v.metrics)}")
    if v.reasons:
        print("reasons: " + "; ".join(v.reasons))
    return 0 if v.status in ("GREEN", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
