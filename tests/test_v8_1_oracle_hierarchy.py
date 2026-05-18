# SPDX-License-Identifier: MIT
"""Oracle ordering is a construction invariant (regime ≤ history ≤
scalar). The pre-registered gap threshold is a SCIENTIFIC verdict and
lives only in the diagnostic — asserting it here would red CI on a
legitimate RED."""

import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.envs.latent_context_temporal_rupture_v8_1 import generate  # noqa: E402
from ctios.oracles import history_oracle, regime_oracle, scalar_oracle  # noqa: E402

CFG = yaml.safe_load(
    (ROOT / "configs" / "v8_1_scalar_inexpressible_env.yaml").read_text()
)


def _mae(p, o) -> float:
    return float(np.mean(np.abs(np.asarray(p) - np.asarray(o))))


def test_ordering_regime_le_history_le_scalar():
    s = h = r = 0.0
    for sd in range(8):
        run = generate(sd, CFG)
        sp = scalar_oracle.predict_series(
            run.obs, CFG["short_thresh"], CFG["long_thresh"], CFG["mu"]
        )
        hp, _ = history_oracle.predict_series(
            run.obs, CFG["short_thresh"], CFG["long_thresh"], CFG["mu"], CFG["delta"]
        )
        rp = regime_oracle.predict_series(run.true_mean)
        s += _mae(sp, run.obs)
        h += _mae(hp, run.obs)
        r += _mae(rp, run.obs)
    assert r <= h + 1e-6
    assert h <= s + 1e-6


def test_regime_is_noise_floor():
    run = generate(0, CFG)
    rp = regime_oracle.predict_series(run.true_mean)
    assert _mae(rp, run.obs) < 1.5 * CFG["sigma"]
