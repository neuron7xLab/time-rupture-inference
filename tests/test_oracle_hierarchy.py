# SPDX-License-Identifier: MIT
"""CONTRACT tests for the oracle hierarchy. The pre-registered gap
threshold (>=0.25) is a SCIENTIFIC verdict — it lives only in the
diagnostic script (research lineage, RED-preservable), never here. These
tests assert only construction-invariant ordering, exercised under a
config where triggers actually fire."""

import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.envs.latent_context_temporal_rupture import generate  # noqa: E402
from ctios.oracles import history_oracle, regime_oracle, scalar_oracle  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "scalar_inexpressible_env.yaml").read_text())
MECH = {**CFG, "sigma": 3.0, "short_thresh": 9.5, "long_thresh": 10.5, "n_steps": 400}


def _mae(p, o) -> float:
    return float(np.mean(np.abs(np.asarray(p) - np.asarray(o))))


def test_ordering_regime_le_history_le_scalar_invariant():
    """Construction invariant: regime is the floor; history is never
    materially worse than scalar (it reduces to it absent triggers)."""
    s = h = r = 0.0
    for sd in range(8):
        run = generate(sd, MECH)
        sp = scalar_oracle.predict_series(
            run.obs, MECH["short_thresh"], MECH["long_thresh"], MECH["mu"]
        )
        hp, _ = history_oracle.predict_series(
            run.obs, MECH["short_thresh"], MECH["long_thresh"], MECH["mu"], MECH["delta"]
        )
        rp = regime_oracle.predict_series(run.true_mean)
        s += _mae(sp, run.obs)
        h += _mae(hp, run.obs)
        r += _mae(rp, run.obs)
    assert r <= h + 1e-6
    assert h <= s + 1e-6


def test_regime_oracle_is_noise_floor():
    run = generate(0, CFG)
    rp = regime_oracle.predict_series(run.true_mean)
    assert _mae(rp, run.obs) < 1.5 * CFG["sigma"]
