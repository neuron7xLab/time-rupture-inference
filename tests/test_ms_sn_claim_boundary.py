# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
from pathlib import Path

FORBIDDEN_POSITIVE_PATTERNS = [
    r"\bruntime validated\b",
    r"\bbiologically validated\b",
    r"\bintelligence validated\b",
    r"\bcomplete evidence seal\b",
    r"\bgreen runtime behavior\b",
]


def test_ms_sn_docs_do_not_expand_claim_boundary() -> None:
    offenders: list[str] = []
    targets = [Path("README_PACKAGE.md")] + list(Path("docs/research").glob("*.md"))
    for path in targets:
        text = path.read_text(encoding="utf-8").lower()
        for pat in FORBIDDEN_POSITIVE_PATTERNS:
            if re.search(pat, text):
                offenders.append(f"{path}: {pat}")

    assert not offenders, (
        "Forbidden positive claim expansion detected:\n" + "\n".join(offenders)
    )
