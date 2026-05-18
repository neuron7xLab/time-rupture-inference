# SPDX-License-Identifier: MIT
"""Structural CONTRACT tests for the v8.1 env. The gap>=0.25 verdict
lives only in the diagnostic (research lineage), never here."""

import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.envs.latent_context_temporal_rupture_v8_1 import generate  # noqa: E402

CFG = yaml.safe_load(
    (ROOT / "configs" / "v8_1_scalar_inexpressible_env.yaml").read_text()
)


def test_deterministic_replay():
    a, b = generate(0, CFG), generate(0, CFG)
    assert np.array_equal(a.obs, b.obs) and a.t_z == b.t_z


def test_finite_and_flip_midpoint():
    r = generate(2, CFG)
    assert np.isfinite(r.obs).all()
    assert r.t_z == CFG["n_steps"] // 2
    pre = set(np.unique(r.z_sign[: r.t_z]))
    post = set(np.unique(r.z_sign[r.t_z :]))
    assert pre in ({1}, {-1}) and post == ({-1} if pre == {1} else {1})


def test_triggers_on_scheduled_slots_only():
    r = generate(1, CFG)
    period = CFG["period"]
    idx = np.flatnonzero(r.is_trigger)
    assert idx.size > 0
    assert all(int(k) % period == 3 for k in idx)


def test_both_contexts_produce_opposite_futures():
    # construction guarantee: across seeds the same scheduled window
    # precedes +delta and -delta futures.
    pos = neg = 0
    for sd in range(6):
        r = generate(sd, CFG)
        dev = np.sign(r.obs[r.is_trigger] - CFG["mu"])
        pos += int((dev > 0).sum())
        neg += int((dev < 0).sum())
    assert pos > 0 and neg > 0
