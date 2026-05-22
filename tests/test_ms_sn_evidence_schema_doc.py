# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path


def test_evidence_schema_is_scaffold_first() -> None:
    text = Path("docs/research/MS_SN_v1_0_0_EVIDENCE_SCHEMA.md").read_text(encoding="utf-8")
    assert "PR #74 is scaffold-only" in text
    assert "evidence/ms_sn_v1_0_0/manifest.json" in text
    assert "SCAFFOLD_ONLY" in text
    assert "runtime_validation_seed" not in text


def test_runtime_manifest_is_marked_future_not_current() -> None:
    text = Path("docs/research/MS_SN_v1_0_0_EVIDENCE_SCHEMA.md").read_text(encoding="utf-8").lower()
    assert "runtime manifest is not required for pr #74" in text
    assert "future" in text
