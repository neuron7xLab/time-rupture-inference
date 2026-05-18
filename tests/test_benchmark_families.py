# SPDX-License-Identifier: MIT
"""WP4 — broadened benchmark families: deterministic replay, seed
sensitivity, and boundary honesty (null != rupture-GREEN; carrier
shortcut fails; heavy-tail/multimodal do not reuse Gaussian silently)."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.benchmark_families import (  # noqa: E402
    CarrierConfoundedRuptureFamily,
    HeavyTailRuptureFamily,
    MultimodalIntervalFamily,
    NullNoRuptureFamily,
    SingleRuptureGaussianFamily,
    all_benchmark_families,
)


def test_replay_hash_stable_same_seed():
    for fam_cls in (SingleRuptureGaussianFamily, HeavyTailRuptureFamily):
        a = fam_cls(seed=7).generate()
        b = fam_cls(seed=7).generate()
        assert a.replay_hash() == b.replay_hash()


def test_different_seed_changes_sequence():
    a = SingleRuptureGaussianFamily(seed=1).generate()
    b = SingleRuptureGaussianFamily(seed=2).generate()
    assert a.replay_hash() != b.replay_hash()


def test_all_families_unique_ids_and_deterministic():
    fams = all_benchmark_families(seed=0)
    ids = [f.family_id for f in fams]
    assert len(ids) == len(set(ids)) == 7
    for f in fams:
        assert f.generate().replay_hash() == f.generate().replay_hash()


def test_null_family_has_no_rupture_metadata():
    s = NullNoRuptureFamily(seed=0).generate()
    assert s.metadata["rupture"] is False
    # a rupture-specific claim must not be admissible here
    assert "false_rupture_detection" in NullNoRuptureFamily.expected_failure_modes


def test_carrier_family_signal_differs_from_carrier_only():
    s = CarrierConfoundedRuptureFamily(seed=0).generate()
    x = np.asarray(s.intervals)
    carrier = np.sin(np.arange(x.size) / 7.0) * 3.0
    # a probe using carrier-only would miss the regime drop entirely
    assert abs(x[: x.size // 2].mean() - x[x.size // 2:].mean()) > 1.0
    assert not np.allclose(x, carrier)


def test_heavy_tail_and_multimodal_not_gaussian_shaped():
    ht = np.asarray(HeavyTailRuptureFamily(seed=0).generate().intervals)
    mm = np.asarray(MultimodalIntervalFamily(seed=0).generate().intervals)
    # Heavy tail lives in the per-regime residual; the global mean shift
    # otherwise masks it. Removing the (deterministic) regime medians
    # isolates the Student-t tail: excess kurtosis >> Gaussian (~0).
    h = ht.size // 2
    resid = np.concatenate(
        [ht[:h] - np.median(ht[:h]), ht[h:] - np.median(ht[h:])]
    )
    zr = resid / resid.std()
    assert (zr**4).mean() - 3.0 > 1.0
    # multimodal: a single Gaussian mean is a poor summary (bimodal gap)
    lo = mm[mm < mm.mean()].mean()
    hi = mm[mm >= mm.mean()].mean()
    assert hi - lo > 3.0
