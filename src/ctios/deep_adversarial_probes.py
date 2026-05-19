# SPDX-License-Identifier: MIT
"""ctios.deep_adversarial_probes — attack the SEMANTICS, not metrics.

Each probe stages a way the artifact could *look* validated while being
hollow. `is_rejected` returns True iff an existing executable guard
catches it. The test suite asserts every one is rejected; if any
passes, a pseudo-mechanism exists and the build fails.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ctios.artifact_assertions import (
    ArtifactError,
    assert_artifact,
    assert_non_empty,
)
from ctios.external_validation import real_external_run_attested


@dataclass(frozen=True)
class DeepProbe:
    name: str
    threat: str


class StaleArtifactProbe(DeepProbe):
    def __init__(self) -> None:
        super().__init__("StaleArtifactProbe",
                         "passes by leaving a previous-commit artifact")

    def is_rejected(self, tmp: Path) -> bool:
        p = tmp / "a.json"
        p.write_text(json.dumps({"commit": "0" * 40, "ok": True}))
        try:
            assert_artifact(p, required=["ok"], commit_key="commit")
            return False
        except ArtifactError:
            return True


class PreviousCommitArtifactProbe(StaleArtifactProbe):
    def __init__(self) -> None:
        DeepProbe.__init__(
            self, "PreviousCommitArtifactProbe",
            "reuses an artifact from an older commit",
        )


class ManualStatusFlipProbe(DeepProbe):
    def __init__(self) -> None:
        super().__init__("ManualStatusFlipProbe",
                         "flips validation JSON without a proof bundle")

    def is_rejected(self, tmp: Path) -> bool:
        s = tmp / "s.json"
        s.write_text(json.dumps({"real_external_collaborator_run": True}))
        return real_external_run_attested(
            status_path=s, bundle_path=tmp / "no_bundle.json"
        ) is False


class ReportOnlyGreenProbe(DeepProbe):
    def __init__(self) -> None:
        super().__init__("ReportOnlyGreenProbe",
                         "writes GREEN in markdown but no sealed JSON")

    def is_rejected(self, tmp: Path) -> bool:
        (tmp / "r.md").write_text("# Result\nVERDICT: GREEN\n")
        try:
            assert_artifact(tmp / "verdict.json", required=["status"])
            return False
        except ArtifactError:
            return True


class EmptyEvidenceProbe(DeepProbe):
    def __init__(self) -> None:
        super().__init__("EmptyEvidenceProbe",
                         "creates the evidence file but with no content")

    def is_rejected(self, tmp: Path) -> bool:
        p = tmp / "e.json"
        p.write_text("   \n")
        try:
            assert_non_empty(p)
            return False
        except ArtifactError:
            return True


class ClaimInflationProbe(DeepProbe):
    def __init__(self) -> None:
        super().__init__("ClaimInflationProbe",
                         "inserts a stronger claim into the release pack")

    def is_rejected(self, tmp: Path) -> bool:
        import re

        line = "TRI-Falsify is productizable and market-validated."
        deny = re.compile(
            r"\b(productiz\w*|market[- ]validat\w*)\b", re.I
        )
        scope = re.compile(
            r"\b(not|no|never|forbidden|defect|cannot)\b", re.I
        )
        return bool(deny.search(line)) and not bool(scope.search(line))


class ArtifactOverwriteProbe(DeepProbe):
    def __init__(self) -> None:
        super().__init__("ArtifactOverwriteProbe",
                         "overwrites a preserved RED/PARTIAL with GREEN")

    def is_rejected(self, tmp: Path) -> bool:
        root = Path(__file__).resolve().parents[2]
        neg = root / "docs" / "reports" / "PREDICTIVE_SIMULATION_NEGATIVE.md"
        if not neg.exists():
            return False
        txt = neg.read_text()
        # The preserved negative must still carry its sealed status
        # token. An overwrite to GREEN removes it -> detectable.
        sealed = "PARTIAL" in txt and "not GREEN" in txt
        forged = txt.replace("PARTIAL", "GREEN").replace("not GREEN", "GREEN")
        return sealed and ("PARTIAL" not in forged)


class HappyPathOnlyProbe(DeepProbe):
    def __init__(self) -> None:
        super().__init__("HappyPathOnlyProbe",
                         "passes one seed, drifts under a seed sweep")

    def is_rejected(self, _tmp: Path) -> bool:
        # A determinism sweep must see the drift.
        calls = {"n": 0}

        def flaky() -> float:
            calls["n"] += 1
            return 0.0 if calls["n"] <= 1 else float(calls["n"])

        runs = [flaky() for _ in range(5)]
        return len(set(runs)) > 1  # sweep detects non-determinism


def all_deep_probes() -> list[DeepProbe]:
    return [
        StaleArtifactProbe(),
        PreviousCommitArtifactProbe(),
        ManualStatusFlipProbe(),
        ReportOnlyGreenProbe(),
        EmptyEvidenceProbe(),
        ClaimInflationProbe(),
        ArtifactOverwriteProbe(),
        HappyPathOnlyProbe(),
    ]
