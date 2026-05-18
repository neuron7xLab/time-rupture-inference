import numpy as np
import pytest

from ctios.metrics import compute_metrics


def test_zero_error_perfect_metrics():
    e = np.zeros(600)
    m = compute_metrics(e, 300, 250, 305, 1.5)
    assert m.post_shift_mae == 0.0
    assert m.area_under_post_shift_error == 0.0


def test_no_detection_is_infinite_delay():
    e = np.zeros(600)
    m = compute_metrics(e, 300, 250, None, 1.5)
    assert m.detection_delay == float("inf")


def test_post_shift_error_raises_mae():
    e = np.zeros(600)
    e[300:550] = 5.0
    m = compute_metrics(e, 300, 250, 305, 1.5)
    assert m.post_shift_mae == 5.0
    assert m.pre_shift_mae == 0.0


def test_detection_before_tstar_rejected():
    e = np.zeros(600)
    m = compute_metrics(e, 300, 250, 280, 1.5)
    assert m.detection_delay == float("inf")


def test_recovery_slope_computed_when_only_one_recovery_point_exists():
    e = np.zeros(10)
    e[:4] = 4.0
    e[4:10] = np.array([3.0, 2.0, 1.0, 0.5, 0.5, 0.0])
    m = compute_metrics(e, t_star=4, eval_horizon=6, detection_step=5,
                        recovery_band_mult=0.3)
    assert m.adaptation_time == 5.0
    assert m.recovery_slope > 0.0


@pytest.mark.parametrize(
    ("pre_len", "post_values", "recovery_band_mult", "expected_adaptation_time"),
    [
        (4, np.array([3.0, 2.0, 1.0, 0.5, 0.5, 0.0]), 0.3, 5.0),
        (8, np.array([6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.1]), 0.8, 6.0),
        (16, np.array([5.0, 4.0, 3.0, 2.0, 1.0, 0.6, 0.3, 0.2]), 0.55, 7.0),
    ],
)
def test_single_recovery_point_bug_is_fixed_across_scales(
    pre_len, post_values, recovery_band_mult, expected_adaptation_time
):
    e = np.zeros(pre_len + post_values.size)
    e[:pre_len] = 4.0
    e[pre_len:] = post_values
    m = compute_metrics(e, t_star=pre_len, eval_horizon=post_values.size,
                        detection_step=pre_len + 1,
                        recovery_band_mult=recovery_band_mult)
    assert m.adaptation_time == expected_adaptation_time
    assert m.recovery_slope > 0.0


@pytest.mark.parametrize(
    ("pre_len", "post_values", "recovery_band_mult"),
    [
        (4, np.array([3.0, 2.0]), 0.7),
        (6, np.array([6.0, 5.0, 4.0, 3.0]), 1.2),
        (10, np.array([10.0, 8.0, 6.0, 4.0, 2.0]), 1.6),
    ],
)
def test_recovery_slope_is_per_step_across_scales(
    pre_len, post_values, recovery_band_mult
):
    e = np.zeros(pre_len + post_values.size)
    e[:pre_len] = 4.0
    e[pre_len:] = post_values
    m = compute_metrics(e, t_star=pre_len, eval_horizon=post_values.size,
                        detection_step=pre_len + 1,
                        recovery_band_mult=recovery_band_mult)
    assert m.adaptation_time == float(post_values.size - 1)
    roll = np.array(
        [np.mean(post_values[: i + 1]) for i in range(post_values.size)]
    )
    expected_slope = (roll[0] - roll[-1]) / max(1, post_values.size - 1)
    assert m.recovery_slope == pytest.approx(expected_slope)


def test_causal_action_counts_are_post_shift_window_only():
    from ctios.causal_metrics import run_metrics

    errors = np.zeros(20)
    actions = ["observe"] * 10 + ["stabilize"] * 5 + ["intervene"] * 5
    m = run_metrics(errors, actions, t_star=10, eval_horizon=10)
    assert m["action_counts"] == {"stabilize": 5, "intervene": 5}


def test_causal_action_count_views_are_consistent():
    from ctios.causal_metrics import run_metrics

    errors = np.zeros(12)
    actions = ["observe"] * 4 + ["stabilize"] * 3 + ["intervene"] * 5
    m = run_metrics(errors, actions, t_star=4, eval_horizon=6)

    assert m["action_counts_pre_shift"] == {"observe": 4}
    assert m["action_counts_post_shift"] == {"stabilize": 3, "intervene": 3}
    assert m["action_counts"] == m["action_counts_post_shift"]
    assert m["action_counts_total"] == {"observe": 4, "stabilize": 3, "intervene": 5}
