# SPDX-License-Identifier: MIT
"""ctios.change_detection_arc — the arc as one runnable.

Six pinned experiments, one inverse argument:

    error is not enough (#24,#25 RED) →
      the observable is the boundary (#26 GREEN) →
        it must survive distribution shift (#27 PARTIAL) →
          and a confound (#28 GREEN) →
            stated honestly across the whole portfolio (#29 PARTIAL).

This runs every sealed verdict once and emits a single consolidated
manifest. It asserts nothing: each lineage's pinned falsifier owns its
own verdict (verdict-isolation). No tuning, no new science.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from ctios.calibrated_change_detector import verdict as v_calibrated
from ctios.carrier_robust_observable import verdict as v_carrier
from ctios.falsify import Verdict
from ctios.portfolio_falsifier import verdict as v_portfolio
from ctios.predictive_simulation import verdict as v_predictive
from ctios.windowed_change_detector import verdict as v_windowed
from ctios.windowed_detector_ood import verdict as v_ood

_ROOT = Path(__file__).resolve().parents[2]

ARC: list[tuple[str, str, Callable[[], Verdict]]] = [
    ("24", "predictive_simulation", v_predictive),
    ("25", "calibrated_change_detector", v_calibrated),
    ("26", "windowed_change_detector", v_windowed),
    ("27", "windowed_detector_ood", v_ood),
    ("28", "carrier_robust_observable", v_carrier),
    ("29", "portfolio_falsifier", v_portfolio),
]


_SHAPE = "RED RED GREEN PARTIAL GREEN PARTIAL"
_INVARIANT = (
    "every falsifier pinned before its run; no threshold edited after "
    "results; every verdict sealed; frozen v4/v5 untouched"
)


def run_arc() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for num, name, fn in ARC:
        v = fn()
        rows.append(
            {
                "n": num,
                "lineage": name,
                "status": v.status,
                "spec_sha256": v.spec_sha256,
                "checks_passed": sum(1 for ok in v.checks.values() if ok),
                "checks_total": len(v.checks),
                "battery_clean": all(v.battery.values()),
            }
        )
    return rows


def main() -> int:
    rows = run_arc()
    ev = _ROOT / "evidence"
    ev.mkdir(exist_ok=True)
    (ev / "CHANGE_DETECTION_ARC.json").write_text(
        json.dumps(
            {"arc": rows, "shape": _SHAPE, "invariant": _INVARIANT}, indent=2
        )
    )
    print("CHANGE-DETECTION ARC")
    for r in rows:
        print(
            f"  #{r['n']} {r['lineage']:<28} {r['status']:<8}"
            f" {r['checks_passed']}/{r['checks_total']} checks"
            f" {'battery OK' if r['battery_clean'] else 'battery XX'}"
        )
    print(f"  shape: {_SHAPE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
