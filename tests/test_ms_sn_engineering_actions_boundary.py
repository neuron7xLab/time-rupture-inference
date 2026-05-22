# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path


def test_engineering_actions_do_not_request_runtime_skeleton() -> None:
    text = Path("docs/research/MS_SN_v1_0_0_ENGINEERING_ACTIONS.md").read_text(
        encoding="utf-8"
    ).lower()
    forbidden = [
        "create runtime skeleton",
        "create runtime module",
        "implement runtime",
        "runtime validation",
    ]
    for phrase in forbidden:
        assert phrase not in text or "forbidden" in text or "out of scope" in text


def test_engineering_actions_explicitly_state_scaffold_only() -> None:
    text = Path("docs/research/MS_SN_v1_0_0_ENGINEERING_ACTIONS.md").read_text(
        encoding="utf-8"
    )
    assert "PR #74 is scaffold-only" in text
    assert "Future runtime work requires a separate PR" in text
