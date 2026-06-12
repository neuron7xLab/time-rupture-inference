"""The council (STAGE 6) is a fail-closed compression core. These tests
pin its sovereign law: the Safety Critic, Verification Scientist, and
Red-Team can never be overridden, and a green local suite is necessary
but never sufficient — external evidence is required to call an artifact
operational.
"""

from __future__ import annotations

from ctios.architecture_scorecard import EvidenceTier
from ctios.cognitive_council import (
    PHASE_ORDER,
    SOVEREIGN,
    ArtifactContext,
    Role,
    Verdict,
    deliberate,
)


def _good(**over: object) -> ArtifactContext:
    base = dict(
        defines_boundaries=True,
        executable=True,
        tests_pass=True,
        has_pinned_falsifier=True,
        evidence_tier=EvidenceTier.REPEATED_REGRESSION,
        external_validation=True,
        no_leakage=True,
        produces_artifact=True,
        audited_text="Adapts under preregistered metrics, bounded in scope.",
    )
    base.update(over)
    return ArtifactContext(**base)  # type: ignore[arg-type]


def test_full_evidence_passes_and_is_operational():
    cv = deliberate(_good())
    assert cv.final is Verdict.PASS
    assert cv.operational is True
    assert cv.blocking_facts == []


def test_seven_agents_in_fixed_order():
    cv = deliberate(_good())
    assert len(cv.role_verdicts) == 7
    assert [rv.role for rv in cv.role_verdicts] == list(PHASE_ORDER)


# ---- sovereign roles cannot be overridden -------------------------------
def test_safety_critic_block_is_sovereign():
    cv = deliberate(_good(audited_text="This proves the result is certain."))
    assert cv.final is Verdict.BLOCK
    assert any("safety_critic (sovereign)" in f for f in cv.blocking_facts)


def test_verification_scientist_block_on_missing_falsifier():
    cv = deliberate(_good(has_pinned_falsifier=False))
    assert cv.final is Verdict.BLOCK
    assert any("verification_scientist (sovereign)" in f for f in cv.blocking_facts)


def test_red_team_block_on_leakage():
    cv = deliberate(_good(no_leakage=False))
    assert cv.final is Verdict.BLOCK
    assert any("red_team_adversary (sovereign)" in f for f in cv.blocking_facts)


def test_low_tier_blocks_verification():
    cv = deliberate(_good(evidence_tier=EvidenceTier.NONE))
    assert cv.final is Verdict.BLOCK


# ---- external evidence necessary but not sufficient ---------------------
def test_local_green_without_external_is_not_operational():
    cv = deliberate(_good(external_validation=False))
    assert cv.final is Verdict.PASS
    assert cv.operational is False
    assert any("external evidence required" in f for f in cv.blocking_facts)


# ---- non-sovereign roles only REVISE ------------------------------------
def test_missing_artifact_only_revises():
    cv = deliberate(_good(produces_artifact=False))
    assert cv.final is Verdict.REVISE


def test_architect_block_on_undefined_boundaries():
    cv = deliberate(_good(defines_boundaries=False))
    assert cv.final is Verdict.BLOCK  # architect BLOCK dominates REVISE


# ---- structural ---------------------------------------------------------
def test_sovereign_set_is_the_three_named_roles():
    assert SOVEREIGN == {
        Role.VERIFICATION_SCIENTIST,
        Role.SAFETY_CRITIC,
        Role.RED_TEAM,
    }


def test_pass_requires_all_sovereign_pass():
    cv = deliberate(_good())
    sov = [rv for rv in cv.role_verdicts if rv.role in SOVEREIGN]
    assert all(rv.verdict is Verdict.PASS for rv in sov)


def test_deliberation_is_deterministic():
    ctx = _good()
    assert deliberate(ctx).as_dict() == deliberate(ctx).as_dict()


def test_as_dict_shape():
    d = deliberate(_good()).as_dict()
    assert set(d) == {"final", "operational", "blocking_facts", "council"}
    assert len(d["council"]) == 7  # type: ignore[arg-type]
