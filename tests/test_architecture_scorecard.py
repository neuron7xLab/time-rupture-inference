"""Contract tests for ctios.architecture_scorecard — the canonical
architecture contract rendered as fail-closed mechanism.

Every guarantee the module promises is pinned here: the weights are a
frozen partition of unity; the score classes have exact bands; the
production class is unreachable without a real regression tier; the
confidence ceilings are hard; an unbacked dimension and a CRITICAL
firewall hit are blocking facts.
"""

from __future__ import annotations

import pytest

from ctios.architecture_scorecard import (
    BLOCKED,
    CONFIDENCE_CEILING,
    DIMENSIONS,
    ELITE_PRODUCTION,
    ELITE_SYNTHETIC,
    PARTIAL,
    PRODUCTION_MIN_TIER,
    REJECTED,
    VALIDATED,
    WEIGHTS,
    ConfidenceInputs,
    EvidenceTier,
    confidence,
    evaluate,
    firewall_scan,
    weights_sum,
)


def _all(value: float) -> dict[str, float]:
    return {d: value for d in DIMENSIONS}


# --------------------------------------------------------------------------
# STAGE 11 — weights.
# --------------------------------------------------------------------------
def test_weights_are_a_partition_of_unity():
    assert weights_sum() == 1.0


def test_weights_cover_exactly_the_nine_dimensions():
    assert len(WEIGHTS) == 9
    assert set(WEIGHTS) == set(DIMENSIONS)


def test_perfect_artifact_scores_five():
    card = evaluate(
        dimensions=_all(5.0),
        tier=EvidenceTier.INDEPENDENT_VALIDATION,
        confidence_inputs=ConfidenceInputs(),
    )
    assert card.final_score == pytest.approx(5.0)


def test_floor_artifact_scores_one():
    card = evaluate(
        dimensions=_all(1.0),
        tier=EvidenceTier.NONE,
        confidence_inputs=ConfidenceInputs(),
    )
    assert card.final_score == pytest.approx(1.0)
    assert card.score_class == REJECTED


# --------------------------------------------------------------------------
# Score-class bands.
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "value,expected",
    [
        (3.9, REJECTED),
        (4.0, PARTIAL),
        (4.49, PARTIAL),
        (4.5, VALIDATED),
        (4.79, VALIDATED),
        (4.8, ELITE_SYNTHETIC),
        (4.94, ELITE_SYNTHETIC),
    ],
)
def test_score_class_bands(value, expected):
    card = evaluate(
        dimensions=_all(value),
        tier=EvidenceTier.REPEATED_REGRESSION,
        confidence_inputs=ConfidenceInputs(),
    )
    assert card.score_class == expected


# --------------------------------------------------------------------------
# Production gate — the central fail-closed guarantee.
# --------------------------------------------------------------------------
def test_production_class_requires_repeated_regression_tier():
    card = evaluate(
        dimensions=_all(5.0),
        tier=EvidenceTier.REPEATED_REGRESSION,
        confidence_inputs=ConfidenceInputs(),
    )
    assert card.score_class == ELITE_PRODUCTION
    assert card.cap_reason == ""


@pytest.mark.parametrize(
    "tier", [EvidenceTier.NONE, EvidenceTier.SYNTHETIC_ONLY, EvidenceTier.LOCAL_REGRESSION]
)
def test_production_score_is_capped_below_regression_tier(tier):
    assert tier < PRODUCTION_MIN_TIER
    card = evaluate(
        dimensions=_all(5.0),
        tier=tier,
        confidence_inputs=ConfidenceInputs(),
    )
    assert card.score_class == ELITE_SYNTHETIC
    assert "capped" in card.cap_reason


def test_independent_validation_also_unlocks_production():
    card = evaluate(
        dimensions=_all(4.96),
        tier=EvidenceTier.INDEPENDENT_VALIDATION,
        confidence_inputs=ConfidenceInputs(),
    )
    assert card.score_class == ELITE_PRODUCTION


# --------------------------------------------------------------------------
# STAGE 13 — confidence ceilings are hard.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("tier", list(EvidenceTier))
def test_confidence_never_exceeds_tier_ceiling(tier):
    saturated = ConfidenceInputs(
        evidence_directness=1.0,
        test_coverage=1.0,
        reproducibility=1.0,
        ambiguity_level=0.0,
        safety_risk=0.0,
        uncertainty_penalty=0.0,
    )
    assert saturated.raw() == pytest.approx(1.0)
    assert confidence(saturated, tier) == CONFIDENCE_CEILING[tier]


def test_confidence_ceilings_match_contract():
    assert CONFIDENCE_CEILING[EvidenceTier.NONE] == 0.60
    assert CONFIDENCE_CEILING[EvidenceTier.SYNTHETIC_ONLY] == 0.75
    assert CONFIDENCE_CEILING[EvidenceTier.LOCAL_REGRESSION] == 0.90
    assert CONFIDENCE_CEILING[EvidenceTier.REPEATED_REGRESSION] == 0.95
    assert CONFIDENCE_CEILING[EvidenceTier.INDEPENDENT_VALIDATION] == 0.99


def test_confidence_ceilings_are_monotonic_in_tier():
    vals = [CONFIDENCE_CEILING[t] for t in EvidenceTier]
    assert vals == sorted(vals)


def test_penalties_reduce_confidence():
    base = ConfidenceInputs(evidence_directness=0.8, test_coverage=0.8, reproducibility=0.8)
    penalised = ConfidenceInputs(
        evidence_directness=0.8, test_coverage=0.8, reproducibility=0.8,
        ambiguity_level=0.5, safety_risk=0.5, uncertainty_penalty=0.2,
    )
    assert penalised.raw() < base.raw()


# --------------------------------------------------------------------------
# Fail-closed: unbacked dimensions.
# --------------------------------------------------------------------------
def test_unbacked_dimension_is_floored_and_blocking():
    partial = {d: 5.0 for d in DIMENSIONS if d != "verification_strength"}
    card = evaluate(
        dimensions=partial,
        tier=EvidenceTier.REPEATED_REGRESSION,
        confidence_inputs=ConfidenceInputs(),
    )
    assert "verification_strength" in card.unbacked_dimensions
    assert card.dimensions["verification_strength"] == 1.0
    assert any("unbacked" in f for f in card.blocking_facts)
    assert card.final_score < 5.0


def test_empty_evidence_floors_everything():
    card = evaluate(
        dimensions={},
        tier=EvidenceTier.NONE,
        confidence_inputs=ConfidenceInputs(),
    )
    assert len(card.unbacked_dimensions) == len(DIMENSIONS)
    assert card.final_score == pytest.approx(1.0)
    assert card.score_class == REJECTED


def test_out_of_range_dimension_rejected():
    with pytest.raises(ValueError, match="out of range"):
        evaluate(
            dimensions={**_all(4.0), "adaptivity": 9.0},
            tier=EvidenceTier.NONE,
            confidence_inputs=ConfidenceInputs(),
        )


def test_unknown_dimension_rejected():
    with pytest.raises(ValueError, match="unknown dimensions"):
        evaluate(
            dimensions={**_all(4.0), "bogus": 4.0},
            tier=EvidenceTier.NONE,
            confidence_inputs=ConfidenceInputs(),
        )


# --------------------------------------------------------------------------
# Anti-pseudo firewall.
# --------------------------------------------------------------------------
def test_firewall_flags_praise_without_metric():
    hits = firewall_scan("This module is powerful and revolutionary.")
    assert any(h["rule"] == "praise_without_metric" for h in hits)


def test_firewall_exonerates_praise_with_metric():
    hits = firewall_scan("Powerful: cut latency to 12 ms on the benchmark.")
    assert not any(h["rule"] == "praise_without_metric" for h in hits)


def test_firewall_flags_truth_without_evidence_as_critical():
    hits = firewall_scan("This proves the theorem is correct.")
    crit = [h for h in hits if h["rule"] == "truth_without_evidence"]
    assert crit and crit[0]["severity"] == "CRITICAL"


def test_firewall_exonerates_proof_bound_to_artifact():
    hits = firewall_scan(
        "The pinned falsifier did not trigger; evidence proves the bound under scope."
    )
    assert not any(h["rule"] == "truth_without_evidence" for h in hits)


def test_firewall_flags_neural_without_mechanism():
    hits = firewall_scan("A neural approach to time.")
    assert any(h["rule"] == "neural_without_mechanism" for h in hits)


def test_firewall_exonerates_neural_with_mechanism():
    hits = firewall_scan("neural-like label only; no biological weight or activation here.")
    assert not any(h["rule"] == "neural_without_mechanism" for h in hits)


def test_firewall_flags_generalizes_without_ood():
    hits = firewall_scan("The model generalizes to everything.")
    assert any(h["rule"] == "generalizes_without_ood" for h in hits)


def test_firewall_reports_line_numbers():
    hits = firewall_scan("clean line\nThis proves it is correct\n")
    assert any(h["line"] == 2 for h in hits)


# --------------------------------------------------------------------------
# Firewall + verdict integration.
# --------------------------------------------------------------------------
def test_critical_firewall_hit_forces_blocked():
    card = evaluate(
        dimensions=_all(5.0),
        tier=EvidenceTier.INDEPENDENT_VALIDATION,
        confidence_inputs=ConfidenceInputs(),
        audited_text="This proves the result is certain.",
    )
    assert card.score_class == BLOCKED
    assert any("CRITICAL" in f for f in card.blocking_facts)


def test_clean_text_does_not_block_high_score():
    card = evaluate(
        dimensions=_all(5.0),
        tier=EvidenceTier.REPEATED_REGRESSION,
        confidence_inputs=ConfidenceInputs(),
        audited_text="The agent adapts under preregistered metrics, bounded to the synthetic env.",
    )
    assert card.score_class == ELITE_PRODUCTION


# --------------------------------------------------------------------------
# Determinism + machine-readable contract.
# --------------------------------------------------------------------------
def test_evaluate_is_deterministic():
    kw = dict(
        dimensions=_all(4.6),
        tier=EvidenceTier.REPEATED_REGRESSION,
        confidence_inputs=ConfidenceInputs(evidence_directness=0.8),
    )
    assert evaluate(**kw).as_dict() == evaluate(**kw).as_dict()


def test_as_dict_has_contract_keys():
    card = evaluate(
        dimensions=_all(4.6),
        tier=EvidenceTier.REPEATED_REGRESSION,
        confidence_inputs=ConfidenceInputs(),
    )
    d = card.as_dict()
    for key in ("scoring_model", "evidence_tier", "final_confidence",
                "blocking_facts", "unbacked_dimensions", "firewall_hits"):
        assert key in d
    assert d["scoring_model"]["score_class"] == card.score_class
    assert set(WEIGHTS) <= set(d["scoring_model"])
