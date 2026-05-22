# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path

import yaml


def test_ms_sn_config_has_required_keys() -> None:
    cfg = yaml.safe_load(Path('configs/ms_sn_v1_0_0.yaml').read_text())['ms_sn_v1_0_0']
    required = {
        'seed', 'gamma_min', 'gamma_max', 'r_desync', 'r_metastable_low',
        'r_metastable_high', 'r_stasis', 'overload_lambda', 'w_desync',
        'w_stasis', 'w_recovery', 'dt_max', 'a_max'
    }
    assert required.issubset(set(cfg))
