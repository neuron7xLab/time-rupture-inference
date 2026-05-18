# SPDX-License-Identifier: MIT
"""Contract: warm/flip-aware bound math + backward compatibility."""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ctios.diagnostics.causal_bound import derive  # noqa: E402

V84 = yaml.safe_load((ROOT / "configs" / "v8_4_rederived_env.yaml").read_text())
V82 = yaml.safe_load((ROOT / "configs" / "v8_2_trigger_scoped_env.yaml").read_text())


def test_v8_4_floor_attainable_pre_run():
    d = derive(V84)
    assert d.attainable_at_0_35 is True
    assert d.h2r_causal_min <= 0.35


def test_backward_compatible_v8_2_unchanged():
    # configs without warm/flips keys -> legacy forced=1.5 (v8.3 reproduced)
    d = derive(V82)
    assert d.h2r_causal_min > 0.35 and d.attainable_at_0_35 is False
