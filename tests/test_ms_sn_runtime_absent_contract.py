# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path


def test_runtime_absent_contract_blocks_silent_runtime_introduction() -> None:
    runtime_path = Path("src/ctios/ms_sn_runtime.py")
    assert not runtime_path.exists(), (
        "src/ctios/ms_sn_runtime.py is forbidden in PR #74. "
        "This PR is scaffold-only. Runtime implementation requires a separate PR, "
        "separate runtime manifest, and updated claim boundary."
    )
