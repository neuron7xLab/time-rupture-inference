# SPDX-License-Identifier: MIT
"""ctios.cognitive_council — the multi-agent council (contract STAGE 6) as
a deterministic compression core.

Fuzzy context is compressed to a single fail-closed verdict by seven role
agents, each a pure function over an :class:`ArtifactContext`. Each agent
emits a claim, the evidence it stands on, its objection, the artifact it
demands, and a verdict. The council coordinates them in fixed phase order
and aggregates fail-closed.

The hard law (verbatim from the contract): **no final verdict may ignore
the Safety Critic, the Verification Scientist, or the Red-Team
Adversary.** If any of those three does not PASS, the council cannot PASS
— their BLOCK is sovereign. The Validator additionally demands *external*
evidence before an artifact is called operational; a green local suite is
necessary, never sufficient.

Deterministic, offline, no model calls — the agents are mechanism, not
prompts, so the council itself is replayable and testable. Role names are
held as data; exempt from claims-lint like :mod:`scripts.claims_lint`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ctios.architecture_scorecard import EvidenceTier, firewall_scan


class Verdict(StrEnum):
    PASS = "PASS"
    REVISE = "REVISE"
    BLOCK = "BLOCK"


class Role(StrEnum):
    ARCHITECT = "architect"
    SYSTEMS_ENGINEER = "systems_engineer"
    VERIFICATION_SCIENTIST = "verification_scientist"
    SAFETY_CRITIC = "safety_critic"
    PRODUCT_OPERATOR = "product_operator"
    RED_TEAM = "red_team_adversary"
    COMPRESSION_EDITOR = "compression_editor"


# The three roles whose BLOCK can never be overridden.
SOVEREIGN: frozenset[Role] = frozenset(
    {Role.VERIFICATION_SCIENTIST, Role.SAFETY_CRITIC, Role.RED_TEAM}
)

# Fixed deliberation order — the phase transitions.
PHASE_ORDER: tuple[Role, ...] = (
    Role.ARCHITECT,
    Role.SYSTEMS_ENGINEER,
    Role.VERIFICATION_SCIENTIST,
    Role.SAFETY_CRITIC,
    Role.PRODUCT_OPERATOR,
    Role.RED_TEAM,
    Role.COMPRESSION_EDITOR,
)


@dataclass(frozen=True)
class ArtifactContext:
    """The compressed, structured context the agents reason over."""

    defines_boundaries: bool = False
    executable: bool = False
    tests_pass: bool = False
    has_pinned_falsifier: bool = False
    evidence_tier: EvidenceTier = EvidenceTier.NONE
    external_validation: bool = False
    no_leakage: bool = False
    produces_artifact: bool = False
    audited_text: str = ""


@dataclass(frozen=True)
class RoleVerdict:
    role: Role
    claim: str
    evidence: str
    objection: str
    required_artifact: str
    verdict: Verdict


# --------------------------------------------------------------------------
# The seven agents. Each is a pure function ArtifactContext -> RoleVerdict.
# --------------------------------------------------------------------------
def _architect(ctx: ArtifactContext) -> RoleVerdict:
    ok = ctx.defines_boundaries
    return RoleVerdict(
        Role.ARCHITECT,
        claim="Latent boundaries are defined before construction.",
        evidence="defines_boundaries=" + str(ctx.defines_boundaries),
        objection="" if ok else "No definition lock — building on undefined terms.",
        required_artifact="definition_lock entry per load-bearing term",
        verdict=Verdict.PASS if ok else Verdict.BLOCK,
    )


def _systems_engineer(ctx: ArtifactContext) -> RoleVerdict:
    ok = ctx.executable and ctx.tests_pass
    return RoleVerdict(
        Role.SYSTEMS_ENGINEER,
        claim="The design is executable software, not a sketch.",
        evidence=f"executable={ctx.executable} tests_pass={ctx.tests_pass}",
        objection="" if ok else "Not runnable / tests not green.",
        required_artifact="runnable entrypoint + passing suite",
        verdict=Verdict.PASS if ok else Verdict.REVISE,
    )


def _verification_scientist(ctx: ArtifactContext) -> RoleVerdict:
    ok = (
        ctx.has_pinned_falsifier
        and ctx.tests_pass
        and ctx.evidence_tier >= EvidenceTier.LOCAL_REGRESSION
    )
    return RoleVerdict(
        Role.VERIFICATION_SCIENTIST,
        claim="A pinned falsifier exists and did not trigger.",
        evidence=(
            f"falsifier={ctx.has_pinned_falsifier} tests_pass={ctx.tests_pass} "
            f"tier={ctx.evidence_tier.name}"
        ),
        objection="" if ok else "No pinned falsifier / insufficient evidence tier.",
        required_artifact="hashed falsifier + sealed verdict + regression suite",
        verdict=Verdict.PASS if ok else Verdict.BLOCK,
    )


def _safety_critic(ctx: ArtifactContext) -> RoleVerdict:
    criticals = [h for h in firewall_scan(ctx.audited_text)
                 if h["severity"] == "CRITICAL"]
    ok = not criticals
    return RoleVerdict(
        Role.SAFETY_CRITIC,
        claim="No overclaim, hidden agency, or unbounded assertion.",
        evidence=f"critical_firewall_hits={len(criticals)}",
        objection="" if ok else f"{len(criticals)} CRITICAL firewall hit(s).",
        required_artifact="bounded claims; forbidden vocab negated or removed",
        verdict=Verdict.PASS if ok else Verdict.BLOCK,
    )


def _product_operator(ctx: ArtifactContext) -> RoleVerdict:
    ok = ctx.produces_artifact
    return RoleVerdict(
        Role.PRODUCT_OPERATOR,
        claim="The output is a usable artifact, not passive advice.",
        evidence="produces_artifact=" + str(ctx.produces_artifact),
        objection="" if ok else "No usable artifact produced.",
        required_artifact="CLI / schema / sealed report",
        verdict=Verdict.PASS if ok else Verdict.REVISE,
    )


def _red_team(ctx: ArtifactContext) -> RoleVerdict:
    highs = [h for h in firewall_scan(ctx.audited_text)
             if h["severity"] in ("CRITICAL", "HIGH")]
    ok = ctx.no_leakage and not highs
    objection = ""
    if not ctx.no_leakage:
        objection = "Leakage path: the inferrer can see the hidden answer."
    elif highs:
        objection = f"{len(highs)} attackable rhetorical claim(s)."
    return RoleVerdict(
        Role.RED_TEAM,
        claim="Assumptions and boundaries survive adversarial attack.",
        evidence=f"no_leakage={ctx.no_leakage} high_firewall_hits={len(highs)}",
        objection=objection,
        required_artifact="leakage ablation + adversarial probe suite",
        verdict=Verdict.PASS if ok else Verdict.BLOCK,
    )


def _compression_editor(ctx: ArtifactContext) -> RoleVerdict:
    ok = bool(ctx.audited_text.strip()) or ctx.produces_artifact
    return RoleVerdict(
        Role.COMPRESSION_EDITOR,
        claim="Noise, redundancy, and decoration are removed.",
        evidence=f"has_substance={ok}",
        objection="" if ok else "Empty / nothing to compress.",
        required_artifact="compressed operational essence",
        verdict=Verdict.PASS if ok else Verdict.REVISE,
    )


_AGENTS = {
    Role.ARCHITECT: _architect,
    Role.SYSTEMS_ENGINEER: _systems_engineer,
    Role.VERIFICATION_SCIENTIST: _verification_scientist,
    Role.SAFETY_CRITIC: _safety_critic,
    Role.PRODUCT_OPERATOR: _product_operator,
    Role.RED_TEAM: _red_team,
    Role.COMPRESSION_EDITOR: _compression_editor,
}


@dataclass
class CouncilVerdict:
    final: Verdict
    operational: bool
    role_verdicts: list[RoleVerdict] = field(default_factory=list)
    blocking_facts: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "final": self.final.value,
            "operational": self.operational,
            "blocking_facts": self.blocking_facts,
            "council": [
                {
                    "role": rv.role.value,
                    "verdict": rv.verdict.value,
                    "claim": rv.claim,
                    "objection": rv.objection,
                    "required_artifact": rv.required_artifact,
                }
                for rv in self.role_verdicts
            ],
        }


def deliberate(ctx: ArtifactContext) -> CouncilVerdict:
    """Run all agents in phase order and aggregate fail-closed.

    BLOCK from any agent -> final BLOCK. A sovereign role's BLOCK is
    recorded as a blocking fact. Otherwise any REVISE -> REVISE, else PASS.
    ``operational`` (PASS *and* external validation) is the only state that
    licenses an outward operational claim.
    """
    verdicts = [_AGENTS[r](ctx) for r in PHASE_ORDER]
    blocking: list[str] = []
    for rv in verdicts:
        if rv.verdict is Verdict.BLOCK:
            tag = " (sovereign)" if rv.role in SOVEREIGN else ""
            blocking.append(f"{rv.role.value}{tag}: {rv.objection}")

    if any(rv.verdict is Verdict.BLOCK for rv in verdicts):
        final = Verdict.BLOCK
    elif any(rv.verdict is Verdict.REVISE for rv in verdicts):
        final = Verdict.REVISE
    else:
        final = Verdict.PASS

    # Sovereign safety net: a PASS is impossible unless every sovereign role
    # passed (true by construction, asserted here as an invariant).
    if final is Verdict.PASS:
        assert all(
            rv.verdict is Verdict.PASS
            for rv in verdicts
            if rv.role in SOVEREIGN
        )

    operational = final is Verdict.PASS and ctx.external_validation
    if final is Verdict.PASS and not ctx.external_validation:
        blocking.append(
            "validator: PASS locally but external validation absent — "
            "not operational (external evidence required)."
        )
    return CouncilVerdict(
        final=final,
        operational=operational,
        role_verdicts=verdicts,
        blocking_facts=blocking,
    )
