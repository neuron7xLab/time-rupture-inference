# SPDX-License-Identifier: MIT
"""Unit guards for the v7 diagnostics (helpers only; the full grid is a
research run via `make v7-diagnostics`, not a CI gate — like v6/v7)."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_v7_cpu import _drive, _env_stream  # noqa: E402
from v7_diagnostics import HEADROOM_MAX, _latent_separability, _Oracle  # noqa: E402


def test_oracle_predicts_regime_means_and_is_upper_bound():
    n, shift = 600, 7.0
    stream = _env_stream(0, n, shift, np.random.default_rng(0))
    orc = _drive(_Oracle(n, shift), stream, 200)["post_shift_mae"]
    # oracle (knows regime means) must be a strong upper bound: near the
    # noise floor, well under a naive constant-1.0 predictor's error.
    assert 0.0 < orc < 3.0


def test_headroom_threshold_pinned():
    assert HEADROOM_MAX == 0.15  # frozen in the pre-registration


def test_latent_separability_finite_nonnegative():
    s = _latent_separability(0, 300, 7.0)
    assert np.isfinite(s) and s >= 0.0
