# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path

FORBIDDEN = ("PR #72", "PR72", "PR: `#72`")


def test_no_pr72_references() -> None:
    files = [Path("README_PACKAGE.md")] + list(Path("docs/research").glob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            assert token not in text, f"forbidden token {token} found in {path}"


def test_pr74_context_present() -> None:
    assert "PR #74" in Path("README_PACKAGE.md").read_text(encoding="utf-8")
    assert "PR #74" in Path("docs/research/PR74_CONTEXT.md").read_text(encoding="utf-8")
