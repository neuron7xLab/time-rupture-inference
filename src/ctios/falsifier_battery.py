# SPDX-License-Identifier: MIT
"""ctios.falsifier_battery — adversarial battery v2 (hostile reviewer).

Given a redacted spec and an opaque probe result, run the checks a
hostile reviewer would run *before* believing a verdict. Each check is
a mechanism with evidence, not an opinion. Admissibility:

    any BLOCKER  -> INADMISSIBLE
    any MAJOR    -> CONDITIONAL
    otherwise    -> PASS
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ctios.opaque_probe import ProbeResult
from ctios.redacted import RedactedHypothesisSpec


def _load_forbidden_tokens() -> tuple[str, ...]:
    """Single source of truth: the canonical claims lexicon. Loading it
    (rather than restating the phrases here) keeps this module itself
    clean under claims-lint and prevents lexicon drift."""
    root = Path(__file__).resolve().parents[2]
    cy = root / "claims.yaml"
    if not cy.exists():
        return ()
    data = yaml.safe_load(cy.read_text()) or {}
    return tuple(str(t).lower() for t in data.get("forbidden_assertive", []))


_FORBIDDEN_CLAIM_TOKENS = _load_forbidden_tokens()

_OPS = {
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
}


@dataclass(frozen=True)
class BatteryCheck:
    code: str
    severity: str  # BLOCKER | MAJOR | MINOR | OK
    message: str
    evidence: str


@dataclass
class BatteryReport:
    hypothesis_id: str
    spec_sha256: str
    verdict: str  # INADMISSIBLE | CONDITIONAL | PASS
    checks: list[BatteryCheck] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _passes(metric: float, op: str, thr: float) -> bool:
    return bool(_OPS[op](metric, thr))


def run_falsifier_battery_v2(
    spec: RedactedHypothesisSpec,
    result: ProbeResult,
    *,
    negative_control: ProbeResult | None = None,
) -> BatteryReport:
    checks: list[BatteryCheck] = []

    def add(code: str, sev: str, msg: str, ev: str) -> None:
        checks.append(BatteryCheck(code, sev, msg, ev))

    # 1. missing falsifier
    if not spec.falsifiers:
        add("missing_falsifier", "BLOCKER", "no falsifier defined", "len==0")
    else:
        add("missing_falsifier", "OK", "falsifier(s) present",
            f"n={len(spec.falsifiers)}")

    # 2. nonfinite metric
    bad = [k for k, v in result.metrics.items() if not math.isfinite(v)]
    add(
        "nonfinite_metric",
        "BLOCKER" if bad else "OK",
        "non-finite metric(s)" if bad else "all metrics finite",
        f"bad={bad}" if bad else "ok",
    )

    # 3. probe nondeterminism
    if not result.deterministic and not result.exploratory:
        add("probe_nondeterminism", "BLOCKER",
            "probe non-deterministic and not declared exploratory",
            "deterministic=False, exploratory=False")
    elif not result.deterministic:
        add("probe_nondeterminism", "MINOR",
            "probe non-deterministic but explicitly exploratory",
            "exploratory=True")
    else:
        add("probe_nondeterminism", "OK", "probe deterministic", "ok")

    # 4. private leakage risk
    if result.private_content_committed or spec.commit_private_content:
        add("private_leakage_risk", "BLOCKER",
            "private content flagged as committed",
            f"result={result.private_content_committed} "
            f"spec={spec.commit_private_content}")
    else:
        add("private_leakage_risk", "OK", "no private content committed", "ok")

    # 5. claim boundary violation
    low = spec.claim.lower()
    hit = [t for t in _FORBIDDEN_CLAIM_TOKENS if t in low]
    add(
        "claim_boundary_violation",
        "BLOCKER" if hit else "OK",
        "claim asserts a forbidden capability" if hit else "claim within boundary",
        f"tokens={hit}" if hit else "ok",
    )

    # 6. threshold decoration + 7. metric non-load-bearing
    #    + 9. verdict instability
    for fz in spec.falsifiers:
        if fz.metric not in result.metrics:
            add("metric_non_load_bearing", "BLOCKER",
                f"falsifier metric {fz.metric!r} absent from probe result",
                f"metrics={sorted(result.metrics)}")
            continue
        m = result.metrics[fz.metric]
        pass_real = _passes(m, fz.op, fz.threshold)
        pass_strict = _passes(m, fz.op, -math.inf if fz.op in ("<=", "<")
                              else math.inf)
        pass_loose = _passes(m, fz.op, math.inf if fz.op in ("<=", "<")
                             else -math.inf)
        if pass_strict == pass_loose:
            add("threshold_decoration", "MAJOR",
                f"threshold {fz.threshold_key!r} never bites "
                f"(verdict invariant to threshold)",
                f"metric={m} op={fz.op}")
        else:
            add("threshold_decoration", "OK",
                f"threshold {fz.threshold_key!r} load-bearing",
                f"metric={m}")
        # instability: metric sits within 1e-9 of the boundary
        if abs(m - fz.threshold) < 1e-9:
            add("verdict_instability", "MAJOR",
                f"metric {fz.metric!r} on the {fz.threshold_key!r} boundary",
                f"|{m}-{fz.threshold}|<1e-9 pass={pass_real}")
        else:
            add("verdict_instability", "OK",
                f"metric {fz.metric!r} stable vs {fz.threshold_key!r}",
                f"margin={abs(m - fz.threshold):.6g}")

    referenced = {f.metric for f in spec.falsifiers}
    decorative = sorted(set(result.metrics) - referenced)
    if decorative:
        add("metric_non_load_bearing", "MINOR",
            "metric(s) reported but not gating any falsifier",
            f"unused={decorative}")
    else:
        add("metric_non_load_bearing", "OK",
            "every reported metric gates a falsifier", "ok")

    # 8. negative control too easy
    if negative_control is None:
        add("negative_control_too_easy", "MAJOR",
            "no negative control supplied; gate discrimination unproven "
            "— a clean PASS is not admissible without one",
            "negative_control=None")
    else:
        nc_all_pass = all(
            fz.metric in negative_control.metrics
            and _passes(negative_control.metrics[fz.metric], fz.op, fz.threshold)
            for fz in spec.falsifiers
        )
        if nc_all_pass:
            add("negative_control_too_easy", "BLOCKER",
                "negative control also passes every falsifier — gate "
                "is not discriminative (pseudo-GREEN)",
                "nc_all_pass=True")
        else:
            add("negative_control_too_easy", "OK",
                "negative control fails as required", "nc_all_pass=False")

    # 10. spec underdefinition
    thin = (len(spec.assumptions) < 2 or len(spec.forbidden_inferences) < 1
            or len(spec.evidence_requirements) < 1)
    if thin:
        add("spec_underdefinition", "MAJOR",
            "spec is thin (assumptions/forbidden/evidence under-specified)",
            f"a={len(spec.assumptions)} "
            f"fi={len(spec.forbidden_inferences)} "
            f"er={len(spec.evidence_requirements)}")
    else:
        add("spec_underdefinition", "OK", "spec sufficiently defined",
            f"a={len(spec.assumptions)}")

    sev = {c.severity for c in checks}
    verdict = (
        "INADMISSIBLE" if "BLOCKER" in sev
        else "CONDITIONAL" if "MAJOR" in sev
        else "PASS"
    )
    return BatteryReport(
        hypothesis_id=spec.hypothesis_id,
        spec_sha256=result.spec_sha256,
        verdict=verdict,
        checks=checks,
    )
