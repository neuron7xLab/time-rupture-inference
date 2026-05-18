# SPDX-License-Identifier: MIT
import numpy as np
import pytest

from ctios.series import rolling_mean_prefix


def test_rolling_mean_prefix_matches_manual_prefix_and_window():
    x = np.array([5.0, 3.0, 1.0, 0.0, 4.0])
    got = rolling_mean_prefix(x, 3)
    expected = np.array(
        [
            np.mean(x[:1]),
            np.mean(x[:2]),
            np.mean(x[:3]),
            np.mean(x[1:4]),
            np.mean(x[2:5]),
        ]
    )
    assert np.allclose(got, expected)


def test_rolling_mean_prefix_window_clamps_to_series_length():
    x = np.array([2.0, 4.0, 6.0])
    got = rolling_mean_prefix(x, 20)
    expected = np.array([2.0, 3.0, 4.0])
    assert np.allclose(got, expected)


@pytest.mark.parametrize("w", [0, -1, -7])
def test_rolling_mean_prefix_rejects_non_positive_window(w: int):
    x = np.array([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="window"):
        rolling_mean_prefix(x, w)
