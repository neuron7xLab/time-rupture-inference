# SPDX-License-Identifier: MIT
from pathlib import Path

import yaml

CFG = yaml.safe_load(
    (Path(__file__).resolve().parents[1] / "configs" / "v7_experiment.yaml").read_text()
)


def test_config_loads_and_ids():
    assert CFG["experiment_id"] == "cti_os_v7"
    assert CFG["fail_closed"] is True
    assert CFG["phase1_no_gpu"] is True


def test_required_model_names_present():
    assert set(CFG["models"]) == {
        "heuristic_v4",
        "esn_small",
        "linear_ssm_small",
        "ar_baseline",
    }


def test_seed_policy_valid():
    assert isinstance(CFG["seed_start"], int) and CFG["seed_start"] >= 0
    assert isinstance(CFG["seed_count"], int) and CFG["seed_count"] >= 30


def test_shift_magnitudes_valid():
    sm = CFG["shift_magnitudes"]
    assert len(sm) >= 3 and any(x < 0 for x in sm) and all(x != 0 for x in sm)


def test_metrics_contract():
    assert {"post_shift_mae", "win_rate_vs_heuristic", "win_rate_vs_baseline"} <= set(
        CFG["metrics"]
    )
