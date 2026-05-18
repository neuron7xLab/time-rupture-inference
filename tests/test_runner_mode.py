# SPDX-License-Identifier: MIT
"""--mode is now wired (was a dead CLI: parse_args discarded). Guards it."""

import pytest

from ctios.runner import _agents_for_mode


def test_full_mode_keeps_everything():
    agents = {"learned_full": object(), "injected": object(), "oracle": object()}
    assert _agents_for_mode(agents, "full") == agents


def test_baselines_excludes_learned_variants():
    agents = {
        "last_interval": object(),
        "moving_average_w5": object(),
        "learned_full": object(),
        "learned_no_update": object(),
        "oracle": object(),
    }
    selected = _agents_for_mode(agents, "baselines")
    assert not any(k.startswith("learned_") for k in selected)
    assert {"last_interval", "moving_average_w5", "oracle"} <= set(selected)


def test_learned_keeps_controls_and_core_ablations():
    agents = {
        "learned_full": object(),
        "learned_no_update": object(),
        "learned_no_drift": object(),
        "oracle": object(),
        "injected": object(),
        "random": object(),
    }
    assert set(_agents_for_mode(agents, "learned")) == {
        "learned_full",
        "learned_no_update",
        "learned_no_drift",
        "oracle",
        "injected",
    }


def test_unknown_mode_fails_loud():
    with pytest.raises(ValueError, match="unknown mode"):
        _agents_for_mode({}, "bogus")
