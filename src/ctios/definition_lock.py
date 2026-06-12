# SPDX-License-Identifier: MIT
"""ctios.definition_lock — STAGE 2 of the architecture contract as a
machine-checkable artifact.

A definition is a clear, deterministic statement of a term's essence: its
invariant boundary, its operational signal, and its failure criterion. It
fixes a single meaning for the term in this apparatus, separating it from
adjacent abstractions so the term can *control* the system and be
verified.

This module renders that standard as data + a fail-closed gate. Each
locked term carries six fields; an entry is admissible only if all six
are present AND its ``test`` anchor resolves to a real file in the repo
(test-before-doc). A term that cannot be defined, observed, failed, and
tested cannot control the system — `validate()` rejects it.

The forbidden lexicon ("cognition", "neural") appears here as locked
*non-claims* — bounded definitions whose `not_this` is the system itself.
This file is enforcement data, exempt from claims-lint like
:mod:`scripts.claims_lint`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Definition:
    """One locked term. Every field is load-bearing and non-optional."""

    term: str
    definition: str
    not_this: str
    observable_signal: str
    failure_condition: str
    test: str  # repo-relative path to the falsifier that anchors the term

    def anchor_exists(self) -> bool:
        return (_ROOT / self.test).exists()


# The lock. Ordering is stable; terms are the load-bearing vocabulary of
# the apparatus, plus the two bounded non-claims at the end.
LOCK: tuple[Definition, ...] = (
    Definition(
        term="rupture",
        definition="A change of the hidden inter-event interval from tau0 to "
        "tau1 at an unseen step T*, never shown to the learner.",
        not_this="A visible label, a gradual drift, or a noise excursion.",
        observable_signal="A sustained shift in the realised interval series "
        "after T*.",
        failure_condition="The post-T* regime is inferable from any input the "
        "learner is handed directly.",
        test="tests/test_change_detection.py",
    ),
    Definition(
        term="prediction_error",
        definition="The agent's own |predicted - realised| signal; the sole "
        "channel through which the rupture is detected.",
        not_this="A supervised target, an oracle distance, or a reward.",
        observable_signal="A spike in the error series concentrated after T*.",
        failure_condition="Adaptation is driven by anything other than the "
        "agent's prediction error.",
        test="tests/test_metrics.py",
    ),
    Definition(
        term="falsifier",
        definition="A predicate pinned (hashed) before a run that, if it "
        "triggers, refutes the hypothesis.",
        not_this="A metric computed after the fact, or a post-hoc threshold.",
        observable_signal="A pre-registered hash that matches the run config.",
        failure_condition="The predicate is defined or altered after seeing "
        "the data.",
        test="tests/test_falsify_engine.py",
    ),
    Definition(
        term="falsifier_battery",
        definition="The ordered set of falsifiers a hypothesis must survive "
        "before any claim is admissible.",
        not_this="A single test, or a battery assembled to pass.",
        observable_signal="Every battery member runs and none triggers.",
        failure_condition="A claim is promoted while a battery member is "
        "skipped or red.",
        test="tests/test_falsification_battery.py",
    ),
    Definition(
        term="probe",
        definition="A registered adversarial input that attacks a specific "
        "assumption of the hypothesis.",
        not_this="A random perturbation, or a probe with no target assumption.",
        observable_signal="A probe bound to a named assumption in the spec.",
        failure_condition="A probe runs without a declared target assumption.",
        test="tests/test_adversarial_probes.py",
    ),
    Definition(
        term="sealed_verdict",
        definition="An append-only artifact recording the run, its hashes, and "
        "the GREEN/RED outcome.",
        not_this="A mutable log, or a verdict editable after sealing.",
        observable_signal="A hash-stamped artifact that reproduces on replay.",
        failure_condition="A sealed artifact is rewritten or a RED is deleted.",
        test="tests/test_ci_evidence_seal.py",
    ),
    Definition(
        term="evidence_ledger",
        definition="The append-only record binding each claim to its falsifier, "
        "evidence, and boundary.",
        not_this="A summary, or a ledger that drops negative results.",
        observable_signal="Every claim row resolves to a real test/artifact.",
        failure_condition="A claim exists in docs with no ledger row.",
        test="tests/test_core_contract_audit.py",
    ),
    Definition(
        term="no_leakage",
        definition="The constraint that tau0, tau1, T*, and the noise never "
        "reach the learner directly.",
        not_this="Hiding a variable in the name while passing it numerically.",
        observable_signal="Ablating the hidden variables leaves inputs "
        "unchanged.",
        failure_condition="Any hidden quantity is reconstructable from the "
        "learner's inputs.",
        test="tests/test_no_leakage.py",
    ),
    Definition(
        term="determinism",
        definition="Byte-identical outputs for a fixed seed and config across "
        "replays.",
        not_this="Approximate reproducibility, or seed-dependent drift.",
        observable_signal="Two replays produce identical artifact bytes.",
        failure_condition="A replay diverges under the same seed and config.",
        test="tests/test_env_determinism.py",
    ),
    Definition(
        term="human_gate",
        definition="The control point where a non-GREEN path proposes the next "
        "experiment and stops, never auto-running it.",
        not_this="An automated retry, or silent continuation past a RED.",
        observable_signal="A proposed-next-experiment record with no auto-run.",
        failure_condition="An experiment runs without crossing the gate.",
        test="tests/test_human_gate.py",
    ),
    Definition(
        term="boundary_condition",
        definition="The exact scope a positive claim is allowed to cover — "
        "what the test measured, nothing more.",
        not_this="An extrapolation beyond the tested env or metric.",
        observable_signal="Each positive is scoped on the same line it appears.",
        failure_condition="A claim asserts validity outside what was measured.",
        test="tests/test_claims_lexicon.py",
    ),
    Definition(
        term="evidence_tier",
        definition="The strength class of backing evidence (NONE..INDEPENDENT) "
        "that hard-caps confidence and the score class.",
        not_this="A confidence number chosen independently of evidence.",
        observable_signal="Confidence never exceeds the tier ceiling.",
        failure_condition="A verdict claims a tier its evidence does not earn.",
        test="tests/test_architecture_scorecard.py",
    ),
    Definition(
        term="blocking_fact",
        definition="A condition (unbacked dimension, CRITICAL firewall hit, "
        "missing external run) that overrides the numeric score.",
        not_this="A soft caveat, or a fact the score can outvote.",
        observable_signal="The verdict is capped despite a high raw score.",
        failure_condition="A high score promotes a verdict past a blocking "
        "fact.",
        test="tests/test_architecture_scorecard.py",
    ),
    Definition(
        term="anti_pseudo_firewall",
        definition="The line-level gate that fires on unbacked rhetoric "
        "(praise without metric, proof without artifact).",
        not_this="A style preference, or a warning that does not block.",
        observable_signal="A CRITICAL hit forces the verdict to BLOCKED.",
        failure_condition="Unbacked rhetoric passes without a recorded hit.",
        test="tests/test_architecture_scorecard.py",
    ),
    Definition(
        term="representational_compression",
        definition="Mapping a high-entropy series to a fixed K_OUT-scalar state "
        "that keeps the rupture and discards the noise, deterministically.",
        not_this="Lossless coding, or a state that hides what it discarded.",
        observable_signal="bits_out < bits_in while the rupture stays "
        "detectable from the state alone.",
        failure_condition="A rupture-free series scores as high as a ruptured "
        "one (hallucinated structure).",
        test="tests/test_entropy_compression.py",
    ),
    # --- bounded non-claims: defined precisely so they can never inflate ---
    Definition(
        term="cognition",
        definition="A label for the perceive->predict->error->update loop, "
        "used operationally and metaphorically only.",
        not_this="The system itself; it is NOT claimed to have cognition, "
        "understanding, or consciousness.",
        observable_signal="The term appears only with a qualifier or in a "
        "disclaimer block.",
        failure_condition="The term is asserted of the system without a "
        "qualifier or boundary.",
        test="tests/test_claims_lexicon.py",
    ),
    Definition(
        term="neural",
        definition="A naming label for the estimator family; carries no "
        "biological or network-architecture claim.",
        not_this="A neural network, backprop, gradient descent, or biological "
        "fidelity.",
        observable_signal="The term carries a -like / label-only / not-"
        "biological qualifier.",
        failure_condition="The term implies a biological or backprop mechanism.",
        test="tests/test_claims_lexicon.py",
    ),
)

TERMS: tuple[str, ...] = tuple(d.term for d in LOCK)


def get(term: str) -> Definition:
    for d in LOCK:
        if d.term == term:
            return d
    raise KeyError(term)


def validate() -> list[str]:
    """Return one violation string per malformed or unanchored entry.

    An empty list means the lock is admissible: every term has all six
    fields populated and a falsifier anchor that exists on disk.
    """
    seen: set[str] = set()
    violations: list[str] = []
    for d in LOCK:
        if d.term in seen:
            violations.append(f"{d.term}: duplicate term")
        seen.add(d.term)
        for field in ("definition", "not_this", "observable_signal",
                      "failure_condition", "test"):
            if not getattr(d, field).strip():
                violations.append(f"{d.term}: empty field {field!r}")
        if not d.anchor_exists():
            violations.append(f"{d.term}: test anchor not found: {d.test}")
    return violations
