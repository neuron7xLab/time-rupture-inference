from ctios.nctp_packet import TASK_SPECS, validate_inference_packet


def test_task_specs_cover_seven_tasks() -> None:
    assert len(TASK_SPECS) == 7
    assert TASK_SPECS[0].task_id == "TASK-01"
    assert TASK_SPECS[-1].task_id == "TASK-07"


def test_validate_inference_packet_happy_path() -> None:
    packet = {
        "state": {"s_t": object()},
        "forecast": {"Y_hat": object(), "horizons": [1, 4, 8]},
        "precision_error": {
            "error": object(),
            "precision": object(),
            "weighted_error": object(),
        },
        "drift": {
            "drift_score": object(),
            "rupture_label_hat": object(),
            "update_gain": object(),
            "reset_probability": object(),
        },
        "memory": {
            "retrieved_state": object(),
            "retrieval_weights": object(),
            "memory_conflict": object(),
            "write_priority": object(),
        },
        "causal_delay": {
            "delay_distribution": object(),
            "causal_credit": object(),
            "effect_prediction": object(),
        },
        "regime_extrapolation": {
            "regime_probs": object(),
            "future_regime_path": object(),
            "regime_change_time": object(),
            "extrapolated_state": object(),
        },
        "counterfactual": {
            "Y_real_hat": object(),
            "Y_counterfact_hat": object(),
            "counterfactual_delta": object(),
            "causal_effect_score": object(),
            "status": "stub",
        },
        "runtime_boundary": {"task05_memory": "stub", "task06_regime": "stub", "task07_counterfactual": "stub"},
    }
    assert validate_inference_packet(packet) == []


def test_validate_inference_packet_detects_gaps() -> None:
    errors = validate_inference_packet({"forecast": {"horizons": []}, "state": {"s_t": object()}})
    assert errors
    assert any("missing top-level keys" in e for e in errors)
    assert any("forecast.horizons" in e for e in errors)


def test_validate_inference_packet_rejects_non_positive_horizons() -> None:
    packet = {
        "state": {"s_t": object()},
        "forecast": {"Y_hat": object(), "horizons": [1, 0, 8]},
        "precision_error": {"error": object(), "precision": object(), "weighted_error": object()},
        "drift": {"drift_score": object(), "rupture_label_hat": object(), "update_gain": object(), "reset_probability": object()},
        "memory": {"retrieved_state": object(), "retrieval_weights": object(), "memory_conflict": object(), "write_priority": object()},
        "causal_delay": {"delay_distribution": object(), "causal_credit": object(), "effect_prediction": object()},
        "regime_extrapolation": {"regime_probs": object(), "future_regime_path": object(), "regime_change_time": object(), "extrapolated_state": object()},
        "counterfactual": {"Y_real_hat": object(), "Y_counterfact_hat": object(), "counterfactual_delta": object(), "causal_effect_score": object(), "status": "stub"},
        "runtime_boundary": {"task05_memory": "stub", "task06_regime": "stub", "task07_counterfactual": "stub"},
    }
    errors = validate_inference_packet(packet)
    assert any("positive integers" in e for e in errors)


def test_validate_inference_packet_rejects_unknown_top_level_keys() -> None:
    packet = {
        "state": {"s_t": object()},
        "forecast": {"Y_hat": object(), "horizons": [1, 4]},
        "precision_error": {"error": object(), "precision": object(), "weighted_error": object()},
        "drift": {"drift_score": object(), "rupture_label_hat": object(), "update_gain": object(), "reset_probability": object()},
        "memory": {"retrieved_state": object(), "retrieval_weights": object(), "memory_conflict": object(), "write_priority": object()},
        "causal_delay": {"delay_distribution": object(), "causal_credit": object(), "effect_prediction": object()},
        "regime_extrapolation": {"regime_probs": object(), "future_regime_path": object(), "regime_change_time": object(), "extrapolated_state": object()},
        "counterfactual": {"Y_real_hat": object(), "Y_counterfact_hat": object(), "counterfactual_delta": object(), "causal_effect_score": object(), "status": "stub"},
        "runtime_boundary": {"task05_memory": "stub", "task06_regime": "stub", "task07_counterfactual": "stub"},
        "extra": object(),
    }
    errors = validate_inference_packet(packet)
    assert any("unknown top-level keys" in e for e in errors)


def test_validate_inference_packet_rejects_unknown_section_keys() -> None:
    packet = {
        "state": {"s_t": object()},
        "forecast": {"Y_hat": object(), "horizons": [1, 4], "bogus": 1},
        "precision_error": {"error": object(), "precision": object(), "weighted_error": object()},
        "drift": {"drift_score": object(), "rupture_label_hat": object(), "update_gain": object(), "reset_probability": object()},
        "memory": {"retrieved_state": object(), "retrieval_weights": object(), "memory_conflict": object(), "write_priority": object()},
        "causal_delay": {"delay_distribution": object(), "causal_credit": object(), "effect_prediction": object()},
        "regime_extrapolation": {"regime_probs": object(), "future_regime_path": object(), "regime_change_time": object(), "extrapolated_state": object()},
        "counterfactual": {"Y_real_hat": object(), "Y_counterfact_hat": object(), "counterfactual_delta": object(), "causal_effect_score": object(), "status": "stub"},
        "runtime_boundary": {"task05_memory": "stub", "task06_regime": "stub", "task07_counterfactual": "stub"},
    }
    errors = validate_inference_packet(packet)
    assert any("unknown keys" in e for e in errors)


def test_validate_rejects_non_numeric_drift_score() -> None:
    packet = {
        "state": {"s_t": object()},
        "forecast": {"Y_hat": object(), "horizons": [1, 4]},
        "precision_error": {"error": object(), "precision": object(), "weighted_error": object()},
        "drift": {"drift_score": [[float("nan")]], "rupture_label_hat": object(), "update_gain": object(), "reset_probability": object()},
        "memory": {"retrieved_state": object(), "retrieval_weights": object(), "memory_conflict": object(), "write_priority": object()},
        "causal_delay": {"delay_distribution": [[1.0]], "causal_credit": object(), "effect_prediction": object()},
        "regime_extrapolation": {"regime_probs": object(), "future_regime_path": object(), "regime_change_time": object(), "extrapolated_state": object()},
        "counterfactual": {"Y_real_hat": object(), "Y_counterfact_hat": object(), "counterfactual_delta": object(), "causal_effect_score": object(), "status": "stub"},
        "runtime_boundary": {"task05_memory": "stub", "task06_regime": "stub", "task07_counterfactual": "stub"},
    }
    errors = validate_inference_packet(packet)
    assert any("drift.drift_score" in e for e in errors)


def test_validate_rejects_delay_distribution_not_normalized() -> None:
    packet = {
        "state": {"s_t": object()},
        "forecast": {"Y_hat": object(), "horizons": [1, 4]},
        "precision_error": {"error": object(), "precision": object(), "weighted_error": object()},
        "drift": {"drift_score": [[0.1]], "rupture_label_hat": object(), "update_gain": object(), "reset_probability": object()},
        "memory": {"retrieved_state": object(), "retrieval_weights": object(), "memory_conflict": object(), "write_priority": object()},
        "causal_delay": {"delay_distribution": [[0.7, 0.7]], "causal_credit": object(), "effect_prediction": object()},
        "regime_extrapolation": {"regime_probs": object(), "future_regime_path": object(), "regime_change_time": object(), "extrapolated_state": object()},
        "counterfactual": {"Y_real_hat": object(), "Y_counterfact_hat": object(), "counterfactual_delta": object(), "causal_effect_score": object(), "status": "stub"},
        "runtime_boundary": {"task05_memory": "stub", "task06_regime": "stub", "task07_counterfactual": "stub"},
    }
    errors = validate_inference_packet(packet)
    assert any("normalized" in e for e in errors)
