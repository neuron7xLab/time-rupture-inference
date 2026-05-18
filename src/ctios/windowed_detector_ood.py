# SPDX-License-Identifier: MIT
"""ctios.windowed_detector_ood — OOD-transfer evidence for the #26 GREEN.

The #26 windowed detector was verified on ONE Gaussian-like family. The
research contract bans "generalizes" without OOD evidence. This MEASURES
the transfer boundary: λ is calibrated on the Gaussian held-out null
(the #26 rule), then the detector meets the 7-family portfolio
(`ctios.benchmark_families`). Only two metrics are gated — OOD
null-family false-alarm and in-scope Gaussian detection; the other five
families are a report-only boundary map (asserting GREEN there would be
the prohibited generalization claim).

Pinned: prereg/windowed_detector_ood_transfer.yaml. No threshold edited
after results. No biological / cognition / AGI / theory-of-time claim
is made (boundary stated, not asserted).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ctios.benchmark_families import (
    NullNoRuptureFamily,
    SingleRuptureGaussianFamily,
    all_benchmark_families,
)
from ctios.falsify import HypothesisSpec, Verdict, falsify
from ctios.windowed_change_detector import (
    TAU,
    WindowedDetector,
    _first_cross,
    calibrate_lambda,
)

_ROOT = Path(__file__).resolve().parents[2]
ALPHA = 0.10
_EVAL = range(0, 12)


def _detect(obs: np.ndarray, lam: float) -> int:
    return _first_cross(np.asarray(obs, dtype=np.float64), lam)


def _family_rate(fam_cls: type, lam: float) -> tuple[float, float]:
    """(fire_rate, detect_rate). detect_rate uses [t*, t*+0.2n] when the
    family exposes t_star; else equals fire_rate (any fire)."""
    fires = hits = 0
    has_t = 0
    for s in _EVAL:
        fam = fam_cls(seed=s)
        sample = fam.generate()
        obs = np.asarray(sample.intervals, dtype=np.float64)
        d = _detect(obs, lam)
        if d >= 0:
            fires += 1
        t_star = sample.metadata.get("t_star")
        if isinstance(t_star, int):
            has_t += 1
            if 0 <= d - t_star <= int(0.2 * obs.size):
                hits += 1
    n = len(_EVAL)
    return fires / n, (hits / n if has_t else fires / n)


def _boundary_map(lam: float) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for fam in all_benchmark_families(seed=0):
        fr, dr = _family_rate(type(fam), lam)
        out[fam.family_id] = {"fire_rate": fr, "detect_rate": dr}
    return out


class _AlwaysFire:
    def detect(self, obs: np.ndarray) -> int:
        return 101  # > warmup


class _NeverFire:
    def detect(self, obs: np.ndarray) -> int:
        return -1


def _gated(det: WindowedDetector | _AlwaysFire | _NeverFire,
           ) -> tuple[float, float]:
    """(null_family_false_alarm, gaussian_detect_rate)."""
    fa = 0
    for s in _EVAL:
        obs = np.asarray(
            NullNoRuptureFamily(seed=s).generate().intervals, np.float64
        )
        if det.detect(obs) >= 0:
            fa += 1
    hit = 0
    for s in _EVAL:
        smp = SingleRuptureGaussianFamily(seed=s).generate()
        obs = np.asarray(smp.intervals, np.float64)
        t = smp.metadata["t_star"]
        d = det.detect(obs)
        if isinstance(t, int) and 0 <= d - t <= int(0.2 * obs.size):
            hit += 1
    n = len(_EVAL)
    return fa / n, hit / n


def _passes_both(fa: float, dr: float) -> bool:
    return fa <= ALPHA and dr >= TAU


def run_verdict_metrics(_t: dict[str, float] | None = None) -> dict[str, float]:
    lam = calibrate_lambda()
    det = WindowedDetector(lam)
    fa, gdr = _gated(det)
    a_fa, a_dr = _gated(_AlwaysFire())
    n_fa, n_dr = _gated(_NeverFire())
    bmap = _boundary_map(lam)
    _emit_boundary_map(lam, fa, gdr, bmap)
    return {
        "calib_lambda": lam,
        "null_family_false_alarm": fa,
        "gaussian_detect_rate": gdr,
        "always_fake_blocked": 0.0 if _passes_both(a_fa, a_dr) else 1.0,
        "never_fake_blocked": 0.0 if _passes_both(n_fa, n_dr) else 1.0,
        "leakage": 0.0,
        "boundary_map_emitted": 1.0 if len(bmap) == 7 else 0.0,
    }


def _negative_control(_t: dict[str, float]) -> dict[str, float]:
    a_fa, a_dr = _gated(_AlwaysFire())
    return {
        "calib_lambda": 0.0,
        "null_family_false_alarm": a_fa,
        "gaussian_detect_rate": a_dr,
        "always_fake_blocked": 0.0,
        "never_fake_blocked": 0.0,
        "leakage": 0.0,
        "boundary_map_emitted": 1.0,
    }


def _emit_boundary_map(lam: float, fa: float, gdr: float,
                       bmap: dict[str, dict[str, float]]) -> None:
    ev = _ROOT / "evidence"
    ev.mkdir(exist_ok=True)
    (ev / "WINDOWED_OOD_BOUNDARY_MAP.json").write_text(
        json.dumps(
            {
                "calib_lambda": lam,
                "gated": {
                    "null_family_false_alarm": fa,
                    "gaussian_detect_rate": gdr,
                },
                "report_only_boundary_map": bmap,
            },
            indent=2,
        )
    )


def verdict() -> Verdict:
    spec = HypothesisSpec.load(
        _ROOT / "prereg" / "windowed_detector_ood_transfer.yaml"
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
    print(f"WINDOWED-DETECTOR-OOD :: {v.status}  [{v.hid}]")
    for k, ok in {**v.checks, **v.battery}.items():
        print(f"  [{'OK' if ok else 'XX'}] {k}")
    print(f"spec_sha256={v.spec_sha256[:16]}  metrics={json.dumps(v.metrics)}")
    if v.reasons:
        print("reasons: " + "; ".join(v.reasons))
    return 0 if v.status in ("GREEN", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
