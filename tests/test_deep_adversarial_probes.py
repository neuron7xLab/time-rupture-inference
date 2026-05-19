# SPDX-License-Identifier: MIT
"""WP6 — every pseudo-mechanism probe MUST be rejected by an existing
executable guard. A passing probe means a hollow mechanism shipped."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.deep_adversarial_probes import all_deep_probes  # noqa: E402


def test_every_deep_probe_is_rejected(tmp_path):
    failures = []
    for p in all_deep_probes():
        if not p.is_rejected(tmp_path):
            failures.append(f"{p.name}: NOT rejected ({p.threat})")
    assert failures == [], "pseudo-mechanism slipped through:\n" + "\n".join(
        failures
    )


def test_probe_set_is_complete():
    names = {p.name for p in all_deep_probes()}
    assert {
        "StaleArtifactProbe", "PreviousCommitArtifactProbe",
        "ManualStatusFlipProbe", "ReportOnlyGreenProbe",
        "EmptyEvidenceProbe", "ClaimInflationProbe",
        "ArtifactOverwriteProbe", "HappyPathOnlyProbe",
    } == names
