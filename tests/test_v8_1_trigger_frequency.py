# SPDX-License-Identifier: MIT
"""Contract: the derivation emits required fields and is closed-form
exact. NOT a scientific verdict (that lives in the diagnostic)."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.trigger_frequency import derive  # noqa: E402

CFG = yaml.safe_load(
    (ROOT / "configs" / "v8_1_scalar_inexpressible_env.yaml").read_text()
)


def test_required_fields_present():
    d = derive(CFG).as_dict()
    for k in (
        "expected_trigger_probability",
        "expected_trigger_count_per_seed",
        "expected_trigger_count_total_grid",
        "expected_same_observation_different_future_rate",
        "expected_aliasing_rate",
        "minimum_required_trigger_count",
        "frequency_precheck_passed",
    ):
        assert k in d


def test_closed_form_exact():
    d = derive(CFG)
    n, period, seeds = CFG["n_steps"], CFG["period"], CFG["seed_count"]
    per = sum(1 for k in range(n) if k % period == 3)
    assert d.expected_trigger_count_per_seed == per
    assert d.expected_trigger_count_total_grid == per * seeds


def test_precheck_passes_at_pinned_config():
    # contract: the pinned config is constructed to clear the precheck
    assert derive(CFG).frequency_precheck_passed is True


def test_invalid_n_steps_rejected():
    cfg = dict(CFG)
    cfg["n_steps"] = 0
    with pytest.raises(ValueError, match="n_steps"):
        derive(cfg)


def test_invalid_min_aliasing_rate_rejected():
    cfg = dict(CFG)
    cfg["min_aliasing_rate"] = float("nan")
    with pytest.raises(ValueError, match="min_aliasing_rate"):
        derive(cfg)


def test_invalid_min_same_obs_diff_future_rate_rejected():
    cfg = dict(CFG)
    cfg["min_same_obs_diff_future_rate"] = 1.5
    with pytest.raises(ValueError, match="min_same_obs_diff_future_rate"):
        derive(cfg)
