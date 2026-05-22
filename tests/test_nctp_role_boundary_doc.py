# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path


def test_nctp_role_boundary_doc_has_required_language() -> None:
    path = Path("docs/research/NCTP_ROLE_DYNAMICS_BOUNDARY.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "independent from MS-SN" in text
    assert "StrEnum" in text
    assert "no claim expansion" in text
    assert "no runtime validation" in text
