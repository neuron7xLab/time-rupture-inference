# SPDX-License-Identifier: MIT
"""Structural CONTRACT tests only. The scientific verdict (gap >= 0.25)
lives solely in scripts/run_scalar_inexpressibility_diagnostic.py — a
research lineage that may legitimately be RED; it is never a CI gate."""

import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.envs.latent_context_temporal_rupture import generate  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "scalar_inexpressible_env.yaml").read_text())
# Mechanism-exercising config (triggers made frequent) — tests the LOGIC,
# not the pinned-parameter scientific verdict.
MECH = {**CFG, "sigma": 3.0, "short_thresh": 9.5, "long_thresh": 10.5, "n_steps": 400}


def test_deterministic_replay():
    a, b = generate(0, CFG), generate(0, CFG)
    assert np.array_equal(a.obs, b.obs) and a.t_z == b.t_z


def test_obs_finite_and_flip_at_midpoint():
    r = generate(1, CFG)
    assert np.isfinite(r.obs).all()
    assert r.t_z == CFG["n_steps"] // 2
    pre = set(np.unique(r.z_sign[: r.t_z]))
    post = set(np.unique(r.z_sign[r.t_z :]))
    assert pre in ({1}, {-1}) and post == ({-1} if pre == {1} else {1})


def test_trigger_logic_correct_when_exercised():
    r = generate(3, MECH)
    assert r.is_trigger.any(), "mechanism config must produce triggers"
    st, lt = MECH["short_thresh"], MECH["long_thresh"]

    def cat(x: float) -> int:
        return 0 if x < st else (2 if x > lt else 1)

    for k in np.flatnonzero(r.is_trigger):
        if k >= 3:
            assert [
                cat(float(r.obs[k - 3])),
                cat(float(r.obs[k - 2])),
                cat(float(r.obs[k - 1])),
            ] == [0, 0, 2]
