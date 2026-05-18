# SPDX-License-Identifier: MIT
"""Audit P2/P3 close-out: config-surface single source + invariants register."""

import inspect
from pathlib import Path

import yaml

from ctios.agents import LearnedAgent

ROOT = Path(__file__).resolve().parents[1]


def test_anti_divergence_config_matches_code_default():
    cfg = yaml.safe_load((ROOT / "configs" / "agents.yaml").read_text())
    defaults = inspect.signature(LearnedAgent.__init__).parameters
    assert cfg["anti_divergence"] is defaults["anti_divergence"].default is False
    assert cfg["min_gain_scale"] == defaults["min_gain_scale"].default == 0.35


def test_invariants_register_paths_exist():
    inv = yaml.safe_load((ROOT / "invariants.yaml").read_text())
    assert inv["invariants"], "invariant register must not be empty"
    for entry in inv["invariants"]:
        assert entry["id"] and entry["statement"] and entry["enforced_by"]
        for ref in entry["enforced_by"]:
            path = ref.split("::")[0].split(":")[0].strip()
            if path.endswith((".py", ".md", ".yaml")):
                assert (ROOT / path).exists(), f"{entry['id']} dangling ref: {path}"
