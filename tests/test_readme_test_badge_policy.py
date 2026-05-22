# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
from pathlib import Path


def test_readme_has_no_numeric_passing_badge() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert re.search(r"tests[-_][0-9]+[-_](passing|PASSING)", readme, flags=re.IGNORECASE) is None
    assert re.search(r"\b[0-9]+\s+tests\s+incl\b", readme, flags=re.IGNORECASE) is None
