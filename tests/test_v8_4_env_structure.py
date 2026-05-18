# SPDX-License-Identifier: MIT
"""Contract: v8.4 env deterministic, finite, marker well-separated,
triggers on schedule. NOT a verdict."""
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ctios.envs.latent_context_temporal_rupture_v8_4 import generate  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_4_rederived_env.yaml").read_text())


def test_deterministic_and_finite():
    a, b = generate(0, CFG), generate(0, CFG)
    assert np.array_equal(a.obs, b.obs) and np.isfinite(a.obs).all()
    assert a.t_z == CFG["n_steps"] // 2


def test_marker_separation_clears_thresholds():
    sep = CFG["marker_sep"]
    assert CFG["mu"] - sep < CFG["short_thresh"] - 2.0
    assert CFG["mu"] + sep > CFG["long_thresh"] + 2.0


def test_triggers_scheduled_and_both_signs():
    pos = neg = 0
    for sd in range(6):
        r = generate(sd, CFG)
        idx = np.flatnonzero(r.is_trigger)
        assert idx.size >= 1 and all(int(k) % CFG["period"] == 3 for k in idx)
        dev = np.sign(r.obs[r.is_trigger] - CFG["mu"])
        pos += int((dev > 0).sum())
        neg += int((dev < 0).sum())
    assert pos > 0 and neg > 0
