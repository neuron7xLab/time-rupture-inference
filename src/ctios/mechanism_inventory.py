# SPDX-License-Identifier: MIT
"""ctios.mechanism_inventory — the inventory is computed, not asserted.

Classifies every src module and script and detects whether a test
imports it. The markdown is the OUTPUT. A CORE_MECHANISM with no linked
test is a hard failure (`tests/test_mechanism_inventory.py`).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src" / "ctios"
_TESTS = _ROOT / "tests"

CORE = "CORE_MECHANISM"
FALSIFIER = "FALSIFIER"
ADVERSARIAL = "ADVERSARIAL_PROBE"
EVIDENCE = "EVIDENCE_PRODUCER"
BOUNDARY = "CLAIM_BOUNDARY"
REPRO = "REPRODUCIBILITY_GUARD"
SURFACE = "REVIEWER_SURFACE"
REPORT = "REPORT_ONLY"

_RULES: list[tuple[str, str]] = [
    (r"_cli$|platform_demo", SURFACE),  # thin wrappers / demo orchestrators
    (r"adversarial|deep_adversarial", ADVERSARIAL),
    (r"falsif|_battery|readiness_score|external_validation|"
     r"v6_precision", FALSIFIER),
    (r"artifact_assertions|provenance|code_quality_audit|"
     r"mechanism_inventory|design_lineage|test_value_audit", REPRO),
    (r"claims|contract", BOUNDARY),
    (r"report|change_detection_arc", EVIDENCE),
    (r"runner|env|agent|drift|metric|gate|series|ledger|"
     r"calibrat|windowed|carrier|portfolio|predictive|redacted|"
     r"opaque|spec_compiler|change_detection|benchmark|automation|"
     r"causal|v6_precision|utils|oracles|envs|learners|diagnostics",
     CORE),
]


@dataclass(frozen=True)
class Item:
    file: str
    classification: str
    linked_test: str
    necessary_because: str


def _classify(name: str) -> str:
    for pat, cls in _RULES:
        if re.search(pat, name):
            return cls
    return CORE


def build() -> list[Item]:
    items: list[Item] = []
    for f in sorted(_SRC.glob("*.py")):
        if f.name in ("__init__.py", "_version.py"):
            continue
        mod = f"ctios.{f.stem}"
        linked = ""
        for tf in sorted(_TESTS.glob("test_*.py")):
            if mod in tf.read_text() or f"import {f.stem}" in tf.read_text():
                linked = tf.name
                break
        cls = _classify(f.stem)
        items.append(
            Item(
                f"src/ctios/{f.name}", cls, linked,
                f"classified {cls} by responsibility",
            )
        )
    for s in sorted((_ROOT / "scripts").glob("*.sh")):
        items.append(
            Item(
                f"scripts/{s.name}", SURFACE,
                "scripts/*.sh artifact-asserted via reviewer_attack",
                "reviewer-facing gate",
            )
        )
    return items


def core_without_test(items: list[Item]) -> list[str]:
    return [
        i.file for i in items
        if i.classification == CORE and not i.linked_test
    ]


def write() -> Path:
    items = build()
    out = _ROOT / "docs" / "MECHANISM_INVENTORY.md"
    lines = [
        "# Mechanism Inventory (generated)",
        "",
        "Computed by `python -m ctios.mechanism_inventory`. Every "
        "CORE_MECHANISM must have a linked test or the build fails.",
        "",
        "| file | classification | linked_test |",
        "|---|---|---|",
    ]
    lines += [
        f"| {i.file} | {i.classification} | {i.linked_test or '—'} |"
        for i in items
    ]
    miss = core_without_test(items)
    lines += ["", f"core_without_test: {miss or '(none)'}"]
    out.write_text("\n".join(lines) + "\n")
    (_ROOT / "evidence" / "MECHANISM_INVENTORY.json").write_text(
        json.dumps(
            {
                "items": [i.__dict__ for i in items],
                "core_without_test": miss,
            },
            indent=2,
        )
    )
    return out


def main() -> int:
    items = build()
    miss = core_without_test(items)
    write()
    print(f"mechanism inventory :: {len(items)} files, "
          f"core_without_test={len(miss)}")
    return 0 if not miss else 1


if __name__ == "__main__":
    raise SystemExit(main())
