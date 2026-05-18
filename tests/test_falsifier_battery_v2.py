# SPDX-License-Identifier: MIT
"""Adversarial battery v2 — admissibility logic."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.falsifier_battery import run_falsifier_battery_v2  # noqa: E402
from ctios.opaque_probe import ProbeResult  # noqa: E402
from ctios.redacted import (  # noqa: E402
    EvidenceRequirement,
    ForbiddenInference,
    RedactedFalsifier,
    RedactedHypothesisSpec,
    RedactedVariable,
)


def _spec(claim="c"):
    return RedactedHypothesisSpec(
        hypothesis_id="h",
        claim=claim,
        null="n",
        assumptions=["a1", "a2"],
        variables=[RedactedVariable("m", "measured"),
                   RedactedVariable("c", "control")],
        falsifiers=[RedactedFalsifier("err", "<=", "ceil", 1.0)],
        forbidden_inferences=[ForbiddenInference("no agi")],
        evidence_requirements=[EvidenceRequirement("sealed")],
    )


def _codes(report):
    return {c.code: c.severity for c in report.checks}


def test_clean_result_with_failing_control_passes():
    s = _spec()
    good = ProbeResult("h", "sha", {"err": 0.4})
    nc = ProbeResult("h", "sha", {})  # control missing metric -> fails
    r = run_falsifier_battery_v2(s, good, negative_control=nc)
    assert r.verdict == "PASS"


def test_nonfinite_metric_is_inadmissible():
    r = run_falsifier_battery_v2(
        _spec(), ProbeResult("h", "s", {"err": float("inf")})
    )
    assert r.verdict == "INADMISSIBLE"
    assert _codes(r)["nonfinite_metric"] == "BLOCKER"


def test_nondeterministic_probe_is_inadmissible_unless_exploratory():
    bad = ProbeResult("h", "s", {"err": 0.5}, deterministic=False)
    assert run_falsifier_battery_v2(_spec(), bad).verdict == "INADMISSIBLE"
    expl = ProbeResult("h", "s", {"err": 0.5}, deterministic=False,
                       exploratory=True)
    assert run_falsifier_battery_v2(_spec(), expl).verdict != "INADMISSIBLE"


def test_private_leakage_is_inadmissible():
    leak = ProbeResult("h", "s", {"err": 0.5}, private_content_committed=True)
    r = run_falsifier_battery_v2(_spec(), leak)
    assert r.verdict == "INADMISSIBLE"
    assert _codes(r)["private_leakage_risk"] == "BLOCKER"


def test_claim_boundary_violation_is_inadmissible():
    r = run_falsifier_battery_v2(
        _spec(claim="this proves general intelligence"),
        ProbeResult("h", "s", {"err": 0.5}),
    )
    assert _codes(r)["claim_boundary_violation"] == "BLOCKER"
    assert r.verdict == "INADMISSIBLE"


def test_pseudo_green_negative_control_is_inadmissible():
    s = _spec()
    good = ProbeResult("h", "s", {"err": 0.4})
    easy_nc = ProbeResult("h", "s", {"err": 0.4})  # control also passes
    r = run_falsifier_battery_v2(s, good, negative_control=easy_nc)
    assert _codes(r)["negative_control_too_easy"] == "BLOCKER"
    assert r.verdict == "INADMISSIBLE"


def test_missing_negative_control_is_conditional_at_best():
    # A clean PASS is not admissible without a discriminative control.
    r = run_falsifier_battery_v2(_spec(), ProbeResult("h", "s", {"err": 0.4}))
    assert r.verdict in ("CONDITIONAL", "INADMISSIBLE")
    assert _codes(r)["negative_control_too_easy"] == "MAJOR"


def test_metric_on_boundary_flags_instability():
    r = run_falsifier_battery_v2(
        _spec(), ProbeResult("h", "s", {"err": 1.0})
    )
    assert _codes(r)["verdict_instability"] == "MAJOR"
