# SPDX-License-Identifier: MIT
"""Keep README test-count policy drift-free.

Numeric test counts are forbidden in README; CI badge must be non-numeric.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_uses_ci_verified_badge_policy() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "tests-CI_VERIFIED" in readme
    assert (
        re.search(r"tests[-_][0-9]+[-_](passing|PASSING)", readme, flags=re.IGNORECASE)
        is None
    )


def test_readme_has_no_numeric_test_count_in_structure_block() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert re.search(r"\b\d+\s+tests\s+incl\b", readme, flags=re.IGNORECASE) is None
