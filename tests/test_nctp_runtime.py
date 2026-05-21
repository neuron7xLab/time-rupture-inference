from ctios.nctp_packet import validate_inference_packet
from ctios.nctp_runtime import (
    DriftConfig,
    RuntimeInputs,
    build_prototype_inference_packet,
    task01_multi_horizon_inference,
    task02_precision_weighted_error,
    task03_drift_rupture_inference,
    task04_causal_delay_inference,
)


def _sample() -> tuple[list[list[list[float]]], list[list[float]], list[int]]:
    x = [
        [[1.0, 2.0], [1.2, 2.1], [1.4, 2.2]],
        [[0.5, 1.0], [0.6, 1.1], [0.7, 1.2]],
    ]
    dt = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    h = [1, 4, 8]
    return x, dt, h


def test_task01_shapes() -> None:
    x, dt, h = _sample()
    out = task01_multi_horizon_inference(x, dt, h)
    assert set(out) == {"h1", "h4", "h8"}


def test_task01_rejects_bad_horizons() -> None:
    x, dt, _ = _sample()
    import pytest

    with pytest.raises(ValueError):
        task01_multi_horizon_inference(x, dt, [0])


def test_task02_numeric_sanity() -> None:
    y_hat = [[[1.0], [2.0]]]
    y_true = [[[1.5], [1.0]]]
    sigma = [[[0.5], [1.0]]]
    out = task02_precision_weighted_error(y_hat, y_true, sigma)
    assert out["error"][0][0][0] == 0.5
    assert out["precision"][0][0][0] > out["precision"][0][1][0]


def test_task03_and_task04_outputs() -> None:
    weighted_error = [[[0.2, 0.1], [0.3, 0.2]]]
    sigma = [[[0.5, 0.5], [0.6, 0.6]]]
    d = task03_drift_rupture_inference(weighted_error, sigma)
    assert 0.0 <= d["drift_score"][0][0] <= 1.0

    c = task04_causal_delay_inference([[0.1, 0.2]], [1, 4, 8])
    s = sum(c["delay_distribution"][0])
    assert abs(s - 1.0) < 1e-9


def test_task03_surrogate_null_has_lower_score_than_high_signal() -> None:
    null_we = [[[0.01, 0.01], [0.01, 0.01]]]
    null_sigma = [[[0.5, 0.5], [0.5, 0.5]]]
    high_we = [[[2.0, 2.0], [2.0, 2.0]]]
    high_sigma = [[[0.1, 0.1], [0.1, 0.1]]]
    s_null = task03_drift_rupture_inference(null_we, null_sigma)["drift_score"][0][0]
    s_high = task03_drift_rupture_inference(high_we, high_sigma)["drift_score"][0][0]
    assert s_high > s_null


def test_task03_rejects_bad_ema_decay() -> None:
    weighted_error = [[[0.2, 0.1], [0.3, 0.2]]]
    sigma = [[[0.5, 0.5], [0.6, 0.6]]]
    import pytest

    with pytest.raises(ValueError):
        task03_drift_rupture_inference(weighted_error, sigma, config=DriftConfig(ema_decay=1.0))


def test_build_packet_validates_without_runtime_errors() -> None:
    x, dt, h = _sample()
    y_true = [
        [[1.5, 2.3], [2.0, 2.8], [2.5, 3.2]],
        [[0.8, 1.3], [1.0, 1.5], [1.3, 1.8]],
    ]
    sigma = [
        [[0.4, 0.4], [0.5, 0.5], [0.7, 0.7]],
        [[0.4, 0.4], [0.5, 0.5], [0.7, 0.7]],
    ]
    packet = build_prototype_inference_packet(RuntimeInputs(x=x, dt=dt, y_true=y_true, sigma=sigma, horizons=h))
    assert validate_inference_packet(packet) == []


def test_build_packet_rejects_empty_horizons() -> None:
    x, dt, _ = _sample()
    y_true = [[[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]], [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]]
    sigma = [[[0.5, 0.5], [0.5, 0.5], [0.5, 0.5]], [[0.5, 0.5], [0.5, 0.5], [0.5, 0.5]]]
    import pytest

    with pytest.raises(ValueError):
        build_prototype_inference_packet(RuntimeInputs(x=x, dt=dt, y_true=y_true, sigma=sigma, horizons=[]))


def test_task03_null_stays_below_threshold() -> None:
    d = task03_drift_rupture_inference([[[0.0, 0.0], [0.0, 0.0]]], [[[1.0, 1.0], [1.0, 1.0]]])
    assert d["drift_score"][0][0] < 0.5


def test_task03_high_uncertainty_suppresses_drift() -> None:
    low_unc = task03_drift_rupture_inference([[[1.0, 1.0], [1.0, 1.0]]], [[[0.1, 0.1], [0.1, 0.1]]])["drift_score"][0][0]
    high_unc = task03_drift_rupture_inference([[[1.0, 1.0], [1.0, 1.0]]], [[[2.0, 2.0], [2.0, 2.0]]])["drift_score"][0][0]
    assert high_unc < low_unc
