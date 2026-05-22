# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
from pathlib import Path


def test_prereg_lock_hash_and_doc() -> None:
    config = Path("configs/ms_sn_v1_0_0.yaml")
    digest = hashlib.sha256(config.read_bytes()).hexdigest()
    pinned = Path("configs/ms_sn_v1_0_0.sha256").read_text(encoding="utf-8").strip()
    assert digest == pinned

    doc = Path("docs/research/MS_SN_v1_0_0_PREREG_LOCK.md")
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "frozen" in text
    assert "v1.0.1" in text
    assert "PR #74" in text
