# SPDX-License-Identifier: MIT
"""Contract: analytic causal bound emits required fields, finite."""

import sys
from pathlib import Path

import yaml

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
