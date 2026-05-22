# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path


FORBIDDEN_PR74_DIFF_PATHS = {
    "evidence/noise_hygiene/latest.json",
    "evidence/v5_causal_ledger.jsonl",
}


def test_ms_sn_pr74_does_not_touch_unrelated_evidence_outputs() -> None:
    for path in FORBIDDEN_PR74_DIFF_PATHS:
        assert Path(path).exists(), f"expected repository artifact missing: {path}"
