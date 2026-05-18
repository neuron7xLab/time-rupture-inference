# SPDX-License-Identifier: MIT
"""Contract: analytic causal bound emits required fields, finite."""

import sys
from pathlib import Path

import yaml
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.causal_bound import derive  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_2_trigger_scoped_env.yaml").read_text())


def test_bound_fields_and_finite():
    d = derive(CFG).as_dict()
    for k in ("triggers_per_seed", "expected_forced_wrong",
              "regime_trigger_floor", "history_trigger_mae_min",
              "h2r_causal_min", "attainable_at_0_35"):
        assert k in d
    assert d["h2r_causal_min"] >= 0.0
    assert isinstance(d["attainable_at_0_35"], bool)
    assert d["triggers_per_seed"] > 0


def test_forced_wrong_is_clamped_by_trigger_count():
    cfg = {
        "n_steps": 10,
        "period": 100,
        "delta": 1.0,
        "sigma": 1.0,
        "hidden_flips": 5,
        "warm_scored": False,
    }
    d = derive(cfg).as_dict()
    assert d["triggers_per_seed"] == 1
    assert d["expected_forced_wrong"] == 1.0
    # If every trigger is forced-wrong, MAE equals the wrong-sign error ceiling.
    assert d["history_trigger_mae_min"] == 2.0


def test_invalid_triggerless_config_raises_value_error():
    cfg = {
        "n_steps": 3,
        "period": 10,
        "delta": 1.0,
        "sigma": 1.0,
    }
    with pytest.raises(ValueError, match="zero trigger events"):
        derive(cfg)


def test_negative_flips_are_clamped_to_zero():
    cfg = {
        "n_steps": 10,
        "period": 100,
        "delta": 1.0,
        "sigma": 1.0,
        "hidden_flips": -10,
        "warm_scored": True,
    }
    d = derive(cfg).as_dict()
    assert d["expected_forced_wrong"] == 0.0
    assert d["history_trigger_mae_min"] == d["regime_trigger_floor"]


def test_warm_scored_string_false_is_parsed_as_false():
    cfg = {
        "n_steps": 10,
        "period": 100,
        "delta": 1.0,
        "sigma": 1.0,
        "hidden_flips": 0,
        "warm_scored": "False",
    }
    d = derive(cfg).as_dict()
    assert d["expected_forced_wrong"] == 0.5


def test_invalid_warm_scored_value_raises():
    cfg = {
        "n_steps": 10,
        "period": 100,
        "delta": 1.0,
        "sigma": 1.0,
        "hidden_flips": 0,
        "warm_scored": "maybe",
    }
    with pytest.raises(ValueError, match="warm_scored"):
        derive(cfg)


def test_non_finite_hidden_flips_rejected():
    cfg = {
        "n_steps": 10,
        "period": 100,
        "delta": 1.0,
        "sigma": 1.0,
        "hidden_flips": float("nan"),
        "warm_scored": False,
    }
    with pytest.raises(ValueError, match="hidden_flips"):
        derive(cfg)


def test_non_finite_sigma_rejected():
    cfg = {
        "n_steps": 10,
        "period": 100,
        "delta": 1.0,
        "sigma": float("inf"),
    }
    with pytest.raises(ValueError, match="sigma"):
        derive(cfg)


def test_non_finite_delta_rejected():
    cfg = {
        "n_steps": 10,
        "period": 100,
        "delta": float("nan"),
        "sigma": 1.0,
    }
    with pytest.raises(ValueError, match="delta"):
        derive(cfg)
