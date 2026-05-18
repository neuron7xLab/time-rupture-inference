# SPDX-License-Identifier: MIT
"""Contract: correctly-specified history oracle is finite, deterministic,
and takes no hidden-state arguments (no z/schedule leakage)."""

import inspect
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.envs.latent_context_temporal_rupture_v8_1 import generate  # noqa: E402
from ctios.oracles import correct_history_oracle as cho  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_2_trigger_scoped_env.yaml").read_text())


def test_no_hidden_args():
    params = set(inspect.signature(cho.predict_series).parameters)
    assert not (params & {"z", "z_sign", "t_z", "true_mean", "is_trigger",
                          "schedule", "period"})


def test_finite_and_deterministic():
    r = generate(0, CFG)
    a = cho.predict_series(r.obs, CFG["short_thresh"], CFG["long_thresh"],
                           CFG["mu"], CFG["delta"])[0]
    b = cho.predict_series(r.obs, CFG["short_thresh"], CFG["long_thresh"],
                           CFG["mu"], CFG["delta"])[0]
    assert np.isfinite(a).all() and np.array_equal(a, b)
    assert a.shape == r.obs.shape
