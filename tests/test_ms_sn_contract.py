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


import re


def test_ms_sn_ci_matrix_targets_declared_in_makefile() -> None:
    workflow = Path(".github/workflows/ms-sn-v1.yml").read_text(encoding="utf-8")
    makefile = Path("Makefile").read_text(encoding="utf-8")
    targets = {"ms-sn-prereg-lock","ms-sn-runtime-absent-contract","ms-sn-runtime-red","ms-sn-reproducibility","ms-sn-scaffold-seal","ms-sn-claim-boundary"}
    for target in targets:
        assert target in workflow
        assert re.search(rf"^{re.escape(target)}:", makefile, flags=re.MULTILINE)


def test_ms_sn_ci_has_no_runtime_green_semantics() -> None:
    workflow = Path(".github/workflows/ms-sn-v1.yml").read_text(encoding="utf-8").lower()
    assert "runtime-green" not in workflow
    assert "green-runtime" not in workflow
    assert "green runtime" not in workflow
