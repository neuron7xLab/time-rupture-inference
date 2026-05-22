# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
from pathlib import Path

REQUIRED_TARGETS = {
    "ms-sn-prereg-lock",
    "ms-sn-runtime-absent-contract",
    "ms-sn-runtime-red",
    "ms-sn-reproducibility",
    "ms-sn-scaffold-seal",
    "ms-sn-claim-boundary",
    "ms-sn-scope-guard",
}


def test_ms_sn_ci_matrix_targets_are_declared_in_makefile() -> None:
    workflow = Path(".github/workflows/ms-sn-v1.yml").read_text(encoding="utf-8")
    makefile = Path("Makefile").read_text(encoding="utf-8")

    for target in REQUIRED_TARGETS:
        assert target in workflow, f"{target} missing from CI matrix"
        assert re.search(rf"^{re.escape(target)}:", makefile, flags=re.MULTILINE), (
            f"{target} missing from Makefile"
        )


def test_ms_sn_ci_does_not_use_runtime_green_semantics() -> None:
    workflow = Path(".github/workflows/ms-sn-v1.yml").read_text(encoding="utf-8").lower()

    forbidden = ["runtime-green", "green-runtime", "green runtime"]

    for token in forbidden:
        assert token not in workflow
