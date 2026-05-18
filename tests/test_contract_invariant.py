"""Anti-regression for the silent-pseudo-GREEN bug class.

The bug: `eval_horizon` lived partly in config and partly as the magic
literal 250 in the runner and tests, letting the measurement window
drift out of agreement with the pre-registered metric. These tests make
that class structurally impossible to reintroduce without a red test.
"""

import re
from pathlib import Path

import numpy as np
import pytest
import yaml

from ctios import contract
from ctios.causal_metrics import run_metrics
from ctios.metrics import compute_metrics
from ctios.runner import _run_on_series

SRC = Path(__file__).resolve().parents[1] / "src" / "ctios"


def test_eval_horizon_single_source_of_truth():
    y = yaml.safe_load((SRC.parents[1] / "configs" / "metrics.yaml").read_text())
    assert contract.EVAL_HORIZON == int(y["eval_horizon"])


def test_no_magic_post_shift_window_literal_in_src():
    """Any `t_star/T_STAR + <number>` slice is the forbidden pattern."""
    pat = re.compile(r"(t_star|T_STAR)\s*[:+]\s*\d{2,}")
    offenders = []
    for f in SRC.glob("*.py"):
        if f.name == "contract.py":
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if pat.search(line):
                offenders.append(f"{f.name}:{i}: {line.strip()}")
    assert not offenders, "magic post-shift window literal reintroduced:\n" + "\n".join(
        offenders
    )


@pytest.mark.parametrize(
    "t_star,horizon,det",
    [(11, 5, None), (5, 0, None), (5, 3, 10), (-1, 5, None), (8, 5, None)],
)
def test_compute_metrics_fails_loud_on_bad_window(t_star, horizon, det):
    with pytest.raises(ValueError):
        compute_metrics(np.zeros(10), t_star, horizon, det, 1.5)


def test_run_on_series_fails_loud_on_bad_window():
    a = __import__("ctios.agents", fromlist=["LearnedAgent"]).LearnedAgent(prior=1.0)
    with pytest.raises(ValueError):
        _run_on_series(a, np.ones(10), t_star=5, eval_horizon=0)


def test_causal_run_metrics_fails_loud_on_bad_window():
    with pytest.raises(ValueError):
        run_metrics(np.zeros(10), ["observe"] * 10, t_star=11, eval_horizon=5)


def test_causal_run_metrics_fails_loud_on_misaligned_lengths():
    with pytest.raises(ValueError):
        run_metrics(np.zeros(10), ["observe"] * 9, t_star=5, eval_horizon=4)


def test_validate_aligned_lengths_fails_loud():
    with pytest.raises(ValueError):
        contract.validate_aligned_lengths(10, 9, names=("errors_len", "actions_len"))
