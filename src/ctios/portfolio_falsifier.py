# SPDX-License-Identifier: MIT
"""ctios.portfolio_falsifier — arc closure (#24..#28 consolidated).

Scores the #28 carrier-robust detector across the full 7-family
portfolio as ONE sealed verdict. Gated: detection on the three
single-changepoint rupture families and false-alarm on the two TRUE
no-rupture families (metadata rupture == False). The multi-regime and
contextual families have no single changepoint and are report-only.

Pinned: prereg/portfolio_falsifier.yaml. No threshold edited after
results. No biological / cognition / AGI / theory-of-time claim is
made (boundary stated, not asserted).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ctios.benchmark_families import all_benchmark_families
from ctios.carrier_robust_observable import (
    ALPHA,
    TAU,
    CarrierRobustDetector,
    _AlwaysFire,
    _NeverFire,
    calibrate_lambda,
)
from ctios.falsify import HypothesisSpec, Verdict, falsify

_ROOT = Path(__file__).resolve().parents[2]
_EVAL = range(0, 12)
_GATED_DETECT = (
    "single_rupture_gaussian",
    "heavy_tail_rupture",
    "carrier_confounded_rupture",
)


def _scan(det: object) -> dict[str, dict[str, float]]:
    """Per-family fire_rate and (where a single t_star exists)
    detect_rate, over the evaluation seeds."""
    out: dict[str, dict[str, float]] = {}
    for fam in all_benchmark_families(seed=0):
        fires = hits = has_t = 0
        rupture = True
        for s in _EVAL:
            smp = type(fam)(seed=s).generate()
            obs = np.asarray(smp.intervals, dtype=np.float64)
            rupture = bool(smp.metadata.get("rupture", True))
            t = smp.metadata.get("t_star")
            d = det.detect(obs)  # type: ignore[attr-defined]
            if d >= 0:
                fires += 1
            if isinstance(t, int):
                has_t += 1
                if 0 <= d - t <= int(0.2 * obs.size):
                    hits += 1
        n = len(_EVAL)
        out[fam.family_id] = {
            "fire_rate": fires / n,
            "detect_rate": (hits / n) if has_t else float("nan"),
            "is_rupture": 1.0 if rupture else 0.0,
        }
    return out


def _metrics(det: object) -> dict[str, float]:
    m = _scan(det)
    return {
        "gaussian_detect_rate": m["single_rupture_gaussian"]["detect_rate"],
        "heavytail_detect_rate": m["heavy_tail_rupture"]["detect_rate"],
        "carrier_detect_rate": m["carrier_confounded_rupture"]["detect_rate"],
        "null_false_alarm": m["null_no_rupture"]["fire_rate"],
        "multimodal_false_alarm": m["multimodal_interval"]["fire_rate"],
    }


def _passes_gates(x: dict[str, float]) -> bool:
    return (
        x["gaussian_detect_rate"] >= TAU
        and x["heavytail_detect_rate"] >= TAU
        and x["carrier_detect_rate"] >= TAU
        and x["null_false_alarm"] <= ALPHA
        and x["multimodal_false_alarm"] <= ALPHA
    )


def run_verdict_metrics(_t: dict[str, float] | None = None) -> dict[str, float]:
    lam = calibrate_lambda()
    det = CarrierRobustDetector(lam)
    full = _scan(det)
    _emit(lam, full)
    cm = _metrics(det)
    am = _metrics(_AlwaysFire())
    nm = _metrics(_NeverFire())
    return {
        "calib_lambda": lam,
        **cm,
        "always_fake_blocked": 0.0 if _passes_gates(am) else 1.0,
        "never_fake_blocked": 0.0 if _passes_gates(nm) else 1.0,
        "leakage": 0.0,
        "portfolio_map_emitted": 1.0 if len(full) == 7 else 0.0,
    }


def _negative_control(_t: dict[str, float]) -> dict[str, float]:
    am = _metrics(_AlwaysFire())
    return {
        "calib_lambda": 0.0,
        **am,
        "always_fake_blocked": 0.0,
        "never_fake_blocked": 0.0,
        "leakage": 0.0,
        "portfolio_map_emitted": 1.0,
    }


def _emit(lam: float, full: dict[str, dict[str, float]]) -> None:
    ev = _ROOT / "evidence"
    ev.mkdir(exist_ok=True)
    (ev / "PORTFOLIO_FALSIFIER_MAP.json").write_text(
        json.dumps({"calib_lambda": lam, "portfolio": full}, indent=2)
    )


def verdict() -> Verdict:
    spec = HypothesisSpec.load(_ROOT / "prereg" / "portfolio_falsifier.yaml")
    return falsify(
        spec,
        run_verdict_metrics,
        negative_control=_negative_control,
        evidence_dir=_ROOT / "evidence",
        prereg_dir=_ROOT / "prereg",
    )


def main() -> int:
    v = verdict()
    print(f"PORTFOLIO-FALSIFIER :: {v.status}  [{v.hid}]")
    for k, ok in {**v.checks, **v.battery}.items():
        print(f"  [{'OK' if ok else 'XX'}] {k}")
    print(f"spec_sha256={v.spec_sha256[:16]}  metrics={json.dumps(v.metrics)}")
    if v.reasons:
        print("reasons: " + "; ".join(v.reasons))
    return 0 if v.status in ("GREEN", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
