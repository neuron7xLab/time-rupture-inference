# SPDX-License-Identifier: MIT
"""ctios.architecture_scorecard — the canonical architecture contract as
an operational, deterministic, fail-closed audit function.

This module turns three otherwise-decorative stages of the canonical
"architecture output" contract into executable mechanism:

* STAGE 11 SCORING_MODEL  — fixed-weight rubric over nine dimensions;
* STAGE 13 CONFIDENCE      — sub-factor confidence with hard ceilings
                             keyed to an evidence tier;
* ANTI-PSEUDO FIREWALL     — line-level detection of unbacked rhetoric.

Design rules, inherited verbatim from :mod:`ctios.readiness_score`:

1. The number never overrides a blocking fact. A firewall CRITICAL or an
   unbacked dimension is a blocking fact, and it caps the verdict.
2. Confidence is hard-capped by the evidence tier. No verification
   harness -> 0.60; synthetic only -> 0.75; local regression -> 0.90;
   repeated regression -> 0.95; independent validation -> 0.99.
3. ``ELITE_VALIDATED_PRODUCTION`` is *unreachable* without a real
   repeated-regression tier, regardless of the raw score.
4. A dimension with no supplied evidence defaults to the floor (1.0) and
   is recorded as unbacked — silence scores low, never high.

This is an audit instrument over *artifacts*. It is not a claim that the
apparatus has cognition, intelligence, or understanding of time; the
forbidden lexicon below is held as enforcement *data*, exactly as in
:mod:`scripts.claims_lint`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

# --------------------------------------------------------------------------
# STAGE 11 — scoring weights (frozen; must sum to exactly 1.0).
# --------------------------------------------------------------------------
WEIGHTS: dict[str, float] = {
    "definitional_precision": 0.13,
    "operational_executability": 0.14,
    "inference_control": 0.13,
    "verification_strength": 0.15,
    "cognitive_neural_validity": 0.12,  # rubric label; not a system claim
    "safety_boundary": 0.10,
    "artifact_usability": 0.10,
    "compression_quality": 0.07,
    "adaptivity": 0.06,
}

DIMENSIONS: tuple[str, ...] = tuple(WEIGHTS)

SCORE_FLOOR = 1.0
SCORE_CEIL = 5.0


class EvidenceTier(IntEnum):
    """Strength of the evidence backing a verdict. Higher binds a higher
    confidence ceiling and unlocks a higher score class."""

    NONE = 0  # no verification harness exists
    SYNTHETIC_ONLY = 1  # only synthetic/self tests exist
    LOCAL_REGRESSION = 2  # a real regression suite passes locally
    REPEATED_REGRESSION = 3  # regression passes repeatedly over time
    INDEPENDENT_VALIDATION = 4  # external/independent validation recorded


# STAGE 13 — hard confidence ceilings, indexed by evidence tier.
CONFIDENCE_CEILING: dict[EvidenceTier, float] = {
    EvidenceTier.NONE: 0.60,
    EvidenceTier.SYNTHETIC_ONLY: 0.75,
    EvidenceTier.LOCAL_REGRESSION: 0.90,
    EvidenceTier.REPEATED_REGRESSION: 0.95,
    EvidenceTier.INDEPENDENT_VALIDATION: 0.99,
}

# Minimum tier at which ELITE_VALIDATED_PRODUCTION becomes reachable.
PRODUCTION_MIN_TIER = EvidenceTier.REPEATED_REGRESSION


class ScoreClass(str):  # noqa: D101 - simple string-enum surrogate
    pass


REJECTED = "REJECTED"
PARTIAL = "PARTIAL"
VALIDATED = "VALIDATED"
ELITE_SYNTHETIC = "ELITE_VALIDATED_SYNTHETIC"
ELITE_PRODUCTION = "ELITE_VALIDATED_PRODUCTION"
BLOCKED = "BLOCKED"


# --------------------------------------------------------------------------
# ANTI-PSEUDO FIREWALL — line-level rhetoric detectors.
#
# Each entry: (name, trigger-regex, exoneration-regex, severity, remedy).
# A line FIRES when `trigger` matches and `exonerate` does NOT. CRITICAL
# fires are blocking facts. The patterns are data, not assertions.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FirewallRule:
    name: str
    trigger: re.Pattern[str]
    exonerate: re.Pattern[str] | None
    severity: str  # "CRITICAL" | "HIGH" | "MEDIUM"
    remedy: str


def _rx(pat: str) -> re.Pattern[str]:
    return re.compile(pat, re.IGNORECASE)


FIREWALL_RULES: tuple[FirewallRule, ...] = (
    FirewallRule(
        "praise_without_metric",
        _rx(r"\b(powerful|revolutionary|groundbreaking|state-of-the-art|"
            r"world-class|cutting-edge|game-chang\w*)\b"),
        _rx(r"\b\d|\bbenchmark\b|\bmetric\b|\bp\s*[<=]\s*0?\.\d"),
        "HIGH",
        "Attach a metric or delete the adjective.",
    ),
    FirewallRule(
        "neural_without_mechanism",
        _rx(r"\bneural\b"),
        _rx(r"\b(weight|layer|activation|operator|transform\w*|gradient|"
            r"-like|label only|not biological|metaphor|forbidden|"
            r"representation)\b"),
        "HIGH",
        "Name the computational mechanism or drop the term.",
    ),
    FirewallRule(
        "truth_without_evidence",
        _rx(r"\b(proves?|proven|guarantee[sd]?|certain(ly)?)\b"),
        _rx(r"\b(test|artifact|evidence|seal\w*|falsifier|under\b|"
            r"not\b|never\b|cannot\b|reproduc\w*)\b"),
        "CRITICAL",
        "Bind to a test/artifact/falsifier or demote the verb.",
    ),
    FirewallRule(
        "safe_without_boundary",
        _rx(r"\b(is\s+safe|fully\s+safe|completely\s+safe)\b"),
        _rx(r"\b(boundary|bounded|scope[ds]?|within|under|fail[- ]?closed)\b"),
        "HIGH",
        "State the boundary that makes it safe.",
    ),
    FirewallRule(
        "agentic_without_policy",
        _rx(r"\b(agentic|autonomous)\b"),
        _rx(r"\b(policy|gate[ds]?|human[- ]?review|fail[- ]?closed|"
            r"control|boundary|approval)\b"),
        "MEDIUM",
        "Cite the control policy / human gate.",
    ),
    FirewallRule(
        "generalizes_without_ood",
        _rx(r"\bgeneraliz\w+\b"),
        _rx(r"\b(out[- ]?of[- ]?distribution|ood|held[- ]?out|transfer\b|"
            r"beyond\b|test|not\b)\b"),
        "MEDIUM",
        "Show the out-of-distribution / held-out test.",
    ),
)


def firewall_scan(text: str) -> list[dict[str, Any]]:
    """Return one record per fired firewall rule, with 1-based line numbers."""
    hits: list[dict[str, Any]] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        for rule in FIREWALL_RULES:
            if not rule.trigger.search(raw):
                continue
            if rule.exonerate is not None and rule.exonerate.search(raw):
                continue
            hits.append(
                {
                    "rule": rule.name,
                    "severity": rule.severity,
                    "line": lineno,
                    "text": raw.strip(),
                    "remedy": rule.remedy,
                }
            )
    return hits


# --------------------------------------------------------------------------
# Confidence (STAGE 13).
# --------------------------------------------------------------------------
@dataclass
class ConfidenceInputs:
    """Sub-factors in [0, 1]. Higher is better except the two penalties."""

    evidence_directness: float = 0.0
    test_coverage: float = 0.0
    reproducibility: float = 0.0
    ambiguity_level: float = 0.0  # penalty
    safety_risk: float = 0.0  # penalty
    uncertainty_penalty: float = 0.0  # penalty

    def raw(self) -> float:
        good = (
            self.evidence_directness
            + self.test_coverage
            + self.reproducibility
            + (1.0 - self.ambiguity_level)
            + (1.0 - self.safety_risk)
        ) / 5.0
        return max(0.0, min(1.0, good - self.uncertainty_penalty))


def confidence(inputs: ConfidenceInputs, tier: EvidenceTier) -> float:
    """Confidence = min(raw sub-factor confidence, tier ceiling)."""
    return round(min(inputs.raw(), CONFIDENCE_CEILING[tier]), 4)


# --------------------------------------------------------------------------
# Scorecard.
# --------------------------------------------------------------------------
def _classify(score: float, tier: EvidenceTier) -> tuple[str, str]:
    """Map (final_score, tier) -> (score_class, cap_reason)."""
    if score < 4.0:
        return REJECTED, ""
    if score < 4.5:
        return PARTIAL, ""
    if score < 4.8:
        return VALIDATED, ""
    if score < 4.95:
        return ELITE_SYNTHETIC, ""
    # score >= 4.95: production class only with a real regression tier.
    if tier >= PRODUCTION_MIN_TIER:
        return ELITE_PRODUCTION, ""
    return (
        ELITE_SYNTHETIC,
        f"score {score:.3f} qualifies for production class but evidence "
        f"tier is {tier.name} (< {PRODUCTION_MIN_TIER.name}); capped.",
    )


@dataclass
class Scorecard:
    dimensions: dict[str, float]
    final_score: float
    score_class: str
    tier: EvidenceTier
    final_confidence: float
    blocking_facts: list[str]
    unbacked_dimensions: list[str]
    firewall_hits: list[dict[str, Any]]
    cap_reason: str = ""
    note: str = (
        "The number is not an achievement. The verdict is decided by "
        "blocking facts and the evidence tier, not by the score."
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "scoring_model": {
                **{k: round(v, 4) for k, v in self.dimensions.items()},
                "final_score": round(self.final_score, 4),
                "score_class": self.score_class,
            },
            "evidence_tier": self.tier.name,
            "final_confidence": self.final_confidence,
            "blocking_facts": self.blocking_facts,
            "unbacked_dimensions": self.unbacked_dimensions,
            "firewall_hits": self.firewall_hits,
            "cap_reason": self.cap_reason,
            "note": self.note,
        }


def _validate_dimension(name: str, value: float) -> float:
    if not SCORE_FLOOR <= value <= SCORE_CEIL:
        raise ValueError(
            f"dimension {name!r} = {value} out of range "
            f"[{SCORE_FLOOR}, {SCORE_CEIL}]"
        )
    return value


def evaluate(
    *,
    dimensions: dict[str, float],
    tier: EvidenceTier,
    confidence_inputs: ConfidenceInputs,
    audited_text: str = "",
) -> Scorecard:
    """Score an artifact against the frozen rubric, fail-closed.

    Unsupplied dimensions default to the floor and are recorded as
    blocking facts. A CRITICAL firewall hit forces the class to BLOCKED.
    The score class can never reach the production tier without a real
    repeated-regression evidence tier.
    """
    backed: dict[str, float] = {}
    unbacked: list[str] = []
    blocking: list[str] = []

    for name in DIMENSIONS:
        if name in dimensions:
            backed[name] = _validate_dimension(name, dimensions[name])
        else:
            backed[name] = SCORE_FLOOR
            unbacked.append(name)

    unknown = set(dimensions) - set(DIMENSIONS)
    if unknown:
        raise ValueError(f"unknown dimensions: {sorted(unknown)}")

    if unbacked:
        blocking.append(
            f"{len(unbacked)} dimension(s) unbacked by evidence "
            f"(scored at floor {SCORE_FLOOR}): {', '.join(unbacked)}"
        )

    final = sum(WEIGHTS[name] * backed[name] for name in DIMENSIONS)

    firewall_hits = firewall_scan(audited_text)
    criticals = [h for h in firewall_hits if h["severity"] == "CRITICAL"]
    if criticals:
        blocking.append(
            f"{len(criticals)} CRITICAL anti-pseudo firewall hit(s); "
            "verdict forced to BLOCKED."
        )

    score_class, cap_reason = _classify(final, tier)
    if criticals:
        score_class = BLOCKED

    conf = confidence(confidence_inputs, tier)

    return Scorecard(
        dimensions=backed,
        final_score=final,
        score_class=score_class,
        tier=tier,
        final_confidence=conf,
        blocking_facts=blocking,
        unbacked_dimensions=unbacked,
        firewall_hits=firewall_hits,
        cap_reason=cap_reason,
    )


def weights_sum() -> float:
    """Exact sum of the frozen weights (rounded to kill float dust)."""
    return round(sum(WEIGHTS.values()), 10)
