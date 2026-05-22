# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
from pathlib import Path

FORBIDDEN_POSITIVE_PATTERNS = [
    r"\bruntime[- ]green\b",
    r"\bgreen runtime\b",
    r"\bgreen runtime behavior\b",
    r"\bruntime validated\b",
    r"\bruntime validation\b",
    r"\bruntime behavior\b",
    r"\bruntime promotion\b",
    r"\bproduction[- ]ready\b",
    r"\bproduction readiness\b",
    r"\bbiological proof\b",
    r"\bbiological validation\b",
    r"\bbiologically validated\b",
    r"\bintelligence validation\b",
    r"\bintelligence validated\b",
    r"\bconsciousness\b",
    r"\bempirical validation\b",
    r"\bcomplete evidence seal\b",
]

ALLOWED_NEGATION_MARKERS = [
    "no ",
    "not ",
    "does not ",
    "out of scope",
    "forbidden",
    "non-claim",
    "must not claim",
    "claim ",
]


def test_ms_sn_docs_do_not_expand_claim_boundary() -> None:
    offenders: list[str] = []
    targets = [Path("README_PACKAGE.md")] + list(Path("docs/research").glob("*.md"))
    for path in targets:
        text = path.read_text(encoding="utf-8").lower()
        for pat in FORBIDDEN_POSITIVE_PATTERNS:
            for match in re.finditer(pat, text):
                window = text[max(0, match.start() - 160) : min(len(text), match.end() + 160)]
                if any(marker in window for marker in ALLOWED_NEGATION_MARKERS):
                    continue
                offenders.append(f"{path}: {pat}")
    assert not offenders, "Forbidden positive claim expansion detected:\n" + "\n".join(offenders)
