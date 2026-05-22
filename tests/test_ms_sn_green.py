# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path


def test_runtime_green_is_blocked_until_runtime_module_exists() -> None:
    runtime_path = Path('src/ctios/ms_sn_runtime.py')
    assert not runtime_path.exists(), 'runtime module unexpectedly present; update MS-SN gates/tests'
