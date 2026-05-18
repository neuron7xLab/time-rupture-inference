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
