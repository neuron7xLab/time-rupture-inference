import numpy as np

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
