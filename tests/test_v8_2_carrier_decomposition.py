# SPDX-License-Identifier: MIT
"""Contract: masks are disjoint and cover all steps; carrier-aware preds
are finite. NOT a verdict."""

import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.carrier_decomposition import (  # noqa: E402
    carrier_aware_predictions,
    channel_masks,
)
from ctios.envs.latent_context_temporal_rupture_v8_1 import generate  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_2_trigger_scoped_env.yaml").read_text())


def test_masks_disjoint_and_cover():
    r = generate(0, CFG)
    m = channel_masks(r.obs, r.is_trigger, CFG["period"])
    t, c, b = m["trigger"], m["carrier"], m["background"]
    assert not (t & c).any() and not (t & b).any() and not (c & b).any()
    assert (t | c | b).all()


def test_carrier_aware_predictions_finite():
    r = generate(1, CFG)
    sp, hp = carrier_aware_predictions(
        r.obs, CFG["short_thresh"], CFG["long_thresh"], CFG["mu"], CFG["delta"]
    )
    assert sp.shape == hp.shape == r.obs.shape
    assert np.isfinite(sp).all() and np.isfinite(hp).all()
