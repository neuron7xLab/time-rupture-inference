# SPDX-License-Identifier: MIT
"""Opaque probe protocol + deterministic mock."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.opaque_probe import (  # noqa: E402
    DeterministicMockProbe,
    OpaqueProbe,
    ProbeResult,
)
from ctios.redacted import (  # noqa: E402
    EvidenceRequirement,
    ForbiddenInference,
    RedactedFalsifier,
    RedactedHypothesisSpec,
    RedactedVariable,
)


def _spec():
    return RedactedHypothesisSpec(
        hypothesis_id="h",
        claim="c",
        null="n",
        assumptions=["a"],
        variables=[RedactedVariable("m", "measured")],
        falsifiers=[
            RedactedFalsifier("err", "<=", "ceil", 1.0),
            RedactedFalsifier("sep", ">=", "minsep", 0.1),
        ],
        forbidden_inferences=[ForbiddenInference("no agi")],
        evidence_requirements=[EvidenceRequirement("sealed")],
    )


def test_mock_probe_satisfies_protocol_and_is_deterministic():
    p = DeterministicMockProbe("sha123")
    assert isinstance(p, OpaqueProbe)
    s = _spec()
    r1 = p.run(s)
    r2 = p.run(s)
    assert r1.metrics == r2.metrics
    assert r1.metrics_fingerprint() == r2.metrics_fingerprint()
    assert r1.deterministic and r1.finite
    assert r1.private_content_committed is False


def test_mock_probe_emits_a_metric_per_falsifier():
    r = DeterministicMockProbe("x").run(_spec())
    assert set(r.metrics) == {"err", "sep"}
    assert r.metrics["err"] <= 1.0 and r.metrics["sep"] >= 0.1


def test_probe_result_defaults_are_honest():
    r = ProbeResult("h", "sha", {"m": 1.0})
    assert r.deterministic and r.finite
    assert r.private_content_committed is False
    assert r.exploratory is False
