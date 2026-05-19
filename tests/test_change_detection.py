# SPDX-License-Identifier: MIT
"""The distilled change-detection primitive + the byte-identity guard.

This is the elegance invariant: the shared primitive must reproduce the
two lineages' sealed numbers EXACTLY, so a future refactor cannot
silently move a preserved verdict."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.change_detection import (  # noqa: E402
    ThresholdDetector,
    first_crossing,
    mean_std_contrast,
    median_mad_contrast,
    quantile_calibrated_threshold,
    two_window_contrast,
)
from ctios.predictive_simulation import RuptureStream  # noqa: E402


def test_first_crossing_semantics():
    s = np.array([0.0, 0.0, 1.0, 5.0, 0.0])
    assert first_crossing(s, 0.5) == 2
    assert first_crossing(s, 10.0) == -1


def test_contrast_zero_before_warmup_and_spikes_on_rupture():
    st = RuptureStream.make(0)
    c = mean_std_contrast(20, 80)(st.obs)
    assert np.all(c[: 100] == 0.0)  # warmup = W+w
    assert c[st.t_star + 40] > c[100]  # spikes after the rupture


def test_calibration_is_fixed_quantile_rule():
    f = median_mad_contrast(60, 180)
    a = quantile_calibrated_threshold(f, range(100, 116), 0.10)
    b = quantile_calibrated_threshold(f, range(100, 116), 0.10)
    assert a == b
    assert quantile_calibrated_threshold(f, range(100, 116), 0.01) >= a


def test_detector_matches_legacy_module_byte_identical():
    # #26 windowed: the shared primitive must reproduce the module.
    from ctios import windowed_change_detector as wcd

    lam = quantile_calibrated_threshold(
        mean_std_contrast(20, 80), range(100, 116), 0.10
    )
    assert lam == wcd.calibrate_lambda()
    det = ThresholdDetector(mean_std_contrast(20, 80), lam)
    obs = RuptureStream.make(3).obs
    assert det.detect(obs) == wcd.WindowedDetector(lam).detect(obs)


def test_carrier_primitive_matches_module_byte_identical():
    from ctios import carrier_robust_observable as cro

    lam = quantile_calibrated_threshold(
        median_mad_contrast(60, 180), range(100, 116), 0.10
    )
    assert lam == cro.calibrate_lambda()


def test_two_window_contrast_is_pure_and_finite():
    obs = RuptureStream.make(1).obs
    a = two_window_contrast(
        obs, w_short=20, w_base=80,
        loc=lambda x: float(x.mean()),
        scale=lambda s, b, m, n: 1.0,
    )
    assert np.all(np.isfinite(a))
    assert a.shape == obs.shape
