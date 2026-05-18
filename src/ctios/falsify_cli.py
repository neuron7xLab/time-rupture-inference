# SPDX-License-Identifier: MIT
"""`tri-falsify` — run the adversarial-falsification engine on a pinned
HypothesisSpec with a registered probe. Bundled demo: a temporal-rupture
hypothesis over the v8.4 synthetic env (no private data, fully
reproducible). Emits a sealed verdict artifact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]   # src/ctios/_ -> repo root
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.trigger_scoped_metrics import (  # noqa: E402
    history_to_regime_distance,
)
from ctios.envs.latent_context_temporal_rupture_v8_4 import generate  # noqa: E402
from ctios.falsify import HypothesisSpec, falsify  # noqa: E402
from ctios.oracles import (  # noqa: E402
    correct_history_oracle,
    regime_oracle,
    scalar_oracle,
)

_ENV = yaml.safe_load((ROOT / "configs" / "v8_4_rederived_env.yaml").read_text())


def _h2r(use_history: bool, _thresholds: dict[str, float]) -> dict[str, float]:
    """Warm-trigger history-to-regime distance over the v8.4 grid.
    use_history=True -> correctly-specified causal oracle (the candidate);
    False -> scalar oracle (the degenerate negative control)."""
    mu, delta = float(_ENV["mu"]), float(_ENV["delta"])
    st, lt = float(_ENV["short_thresh"]), float(_ENV["long_thresh"])
    H, R = [], []
    for sd in range(int(_ENV["seed_count"])):
        run = generate(sd, _ENV)
        wt = np.flatnonzero(run.is_trigger)[1:]      # warm-scored
        if use_history:
            pred, _ = correct_history_oracle.predict_series(
                run.obs, st, lt, mu, delta
            )
        else:
            pred = scalar_oracle.predict_series(run.obs, st, lt, mu)
        rp = regime_oracle.predict_series(run.true_mean)
        H.append(float(np.mean(np.abs(pred[wt] - run.obs[wt]))))
        R.append(float(np.mean(np.abs(rp[wt] - run.obs[wt]))))
    return {"h2r": history_to_regime_distance(float(np.mean(H)), float(np.mean(R)))}


def _candidate(t: dict[str, float]) -> dict[str, float]:
    return _h2r(True, t)


def _negative_control(t: dict[str, float]) -> dict[str, float]:
    return _h2r(False, t)


REGISTRY = {"temporal": (_candidate, _negative_control)}


def main() -> int:
    ap = argparse.ArgumentParser(prog="tri-falsify")
    ap.add_argument(
        "--spec",
        type=Path,
        default=ROOT / "prereg" / "demo_temporal_causal_floor.yaml",
    )
    ap.add_argument("--probe", choices=sorted(REGISTRY), default="temporal")
    args = ap.parse_args()

    spec = HypothesisSpec.load(args.spec)
    cand, neg = REGISTRY[args.probe]
    v = falsify(
        spec,
        cand,
        negative_control=neg,
        evidence_dir=ROOT / "evidence",
        prereg_dir=ROOT / "prereg",   # non-GREEN -> auto-propose NEXT_*.yaml
    )

    print(f"\nTRI-FALSIFY :: {v.status}  [{spec.hid}]")
    for k, ok in {**v.checks, **v.battery}.items():
        print(f"  [{'OK' if ok else 'XX'}] {k}")
    print(f"spec_sha256={v.spec_sha256[:16]}  metrics={json.dumps(v.metrics)}")
    if v.reasons:
        print("reasons: " + "; ".join(v.reasons))
    print(f"repro: PYTHONPATH=src python -m ctios.falsify_cli --probe {args.probe}")
    return 0 if v.status in ("GREEN", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
