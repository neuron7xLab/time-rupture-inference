# SPDX-License-Identifier: MIT
"""ctios.fractal_invariants — the seven power points of the apparatus.

A *power point* here is a single principle that the apparatus is hardened
around. It is *fractal* when the same principle recurs, unchanged, at more
than one scale — a metric line, a module, the repository as a whole. That
self-similarity is the apparatus's structural integrity: a system inside a
system of systems, governed everywhere by the same small set of laws.

This module is not rhetoric. Each power point declares the concrete sites
where it manifests; an entry is admissible only if it manifests at **two
or more** real, on-disk scales. `validate()` is the proof: if a principle
cannot be shown to recur, it is not fractal and the gate rejects it.

It holds principle names as enforcement data (incl. the bounded-non-claim
principle) and is exempt from claims-lint, like :mod:`scripts.claims_lint`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

MIN_SCALES = 2  # below this, a principle is not self-similar -> not fractal


@dataclass(frozen=True)
class Manifestation:
    """One site where a principle is enforced, at a named scale."""

    scale: str  # "metric" | "module" | "repo" | "config" | "test"
    where: str  # repo-relative path
    note: str

    def exists(self) -> bool:
        return (_ROOT / self.where).exists()


@dataclass(frozen=True)
class PowerPoint:
    """A fractal principle: one law, recurring across scales."""

    id: str
    name: str
    principle: str
    deepening: str  # the operational depth this lock adds now
    manifestations: tuple[Manifestation, ...]

    def live_scales(self) -> list[Manifestation]:
        return [m for m in self.manifestations if m.exists()]

    def is_fractal(self) -> bool:
        scales = {m.scale for m in self.live_scales()}
        return len(self.live_scales()) >= MIN_SCALES and len(scales) >= 2


def _m(scale: str, where: str, note: str) -> Manifestation:
    return Manifestation(scale, where, note)


POINTS: tuple[PowerPoint, ...] = (
    PowerPoint(
        id="P1",
        name="fail_closed",
        principle="Ambiguity, a missing falsifier, or boundary expansion "
        "halts the path; the default is refusal, never optimistic progress.",
        deepening="The scorecard floors any unbacked dimension and forces "
        "BLOCKED on a CRITICAL firewall hit — refusal is computed, not hoped.",
        manifestations=(
            _m("repo", "CLAUDE.md", "fail-closed is the operating contract"),
            _m("module", "src/ctios/architecture_scorecard.py",
               "unbacked -> floor; CRITICAL -> BLOCKED"),
            _m("module", "src/ctios/human_gate.py",
               "non-GREEN proposes next experiment and stops"),
            _m("test", "scripts/claims_lint.py", "exit 1 on any violation"),
        ),
    ),
    PowerPoint(
        id="P2",
        name="claim_falsifier_evidence_boundary",
        principle="A claim is admissible only as claim -> falsifier -> "
        "evidence -> boundary, scoped to exactly what was measured.",
        deepening="Every locked definition now carries a falsifier anchor, so "
        "the grammar is enforced even at the level of a single term.",
        manifestations=(
            _m("repo", "CLAUDE.md", "the admissible claim grammar"),
            _m("module", "src/ctios/falsify.py", "HypothesisSpec + verdict"),
            _m("metric", "src/ctios/definition_lock.py",
               "each term binds to a test"),
            _m("repo", "docs/CLAIM_SOURCE_MATRIX.md", "claim->source binding"),
        ),
    ),
    PowerPoint(
        id="P3",
        name="pinned_before_run",
        principle="The judge is fixed before it sees the data: hashes are "
        "pinned pre-run so nothing can be retrofitted to pass.",
        deepening="The same pin-before-observe law spans the prereg hash, the "
        "config sha, and the provenance manifest — one law, three scales.",
        manifestations=(
            _m("module", "src/ctios/falsify.py", "falsifier hashed pre-run"),
            _m("test", "scripts/provenance_attest.py", "source manifest hash"),
            _m("config", "configs/ms_sn_v1_0_0.sha256", "pinned config digest"),
            _m("repo", "scripts_prereg.py", "pre-registration entrypoint"),
        ),
    ),
    PowerPoint(
        id="P4",
        name="blindness",
        principle="The inferrer never sees the answer: it must work from its "
        "own error, never from the hidden quantity.",
        deepening="Blindness recurs as an epistemic law — the learner is blind "
        "to tau/T*, the scorecard is blind to optimism (floors the unbacked), "
        "confidence is blind beyond its evidence tier.",
        manifestations=(
            _m("module", "src/ctios/envs/latent_context_temporal_rupture.py",
               "learner blind to tau0/tau1/T*"),
            _m("test", "tests/test_no_leakage.py", "no hidden quantity leaks"),
            _m("module", "src/ctios/architecture_scorecard.py",
               "blind to optimism: silence scores at floor"),
        ),
    ),
    PowerPoint(
        id="P5",
        name="append_only_preserved_red",
        principle="Evidence is append-only and negatives are preserved: a RED "
        "is never deleted, a sealed artifact never rewritten.",
        deepening="The same preservation law guards the live ledger, the "
        "sealed release gate, and the frozen v4/v5 numbers across scales.",
        manifestations=(
            _m("module", "src/ctios/ledger.py", "append-only evidence ledger"),
            _m("repo", "CLAUDE.md", "no frozen rewrite; REDs preserved"),
            _m("config", "evidence/release_gate.md", "sealed verdict artifact"),
        ),
    ),
    PowerPoint(
        id="P6",
        name="number_subordinate_to_fact",
        principle="The number is never the verdict: a score or confidence is "
        "always capped by a blocking fact and an evidence tier.",
        deepening="Two independent scorers obey the identical subordination "
        "law — readiness and the architecture scorecard — proving it is "
        "structural, not local.",
        manifestations=(
            _m("module", "src/ctios/readiness_score.py",
               "status decided by blocking facts, not the number"),
            _m("module", "src/ctios/architecture_scorecard.py",
               "production unreachable below the regression tier"),
            _m("test", "tests/test_readiness_score.py",
               "score cannot override a blocking fact"),
            _m("repo", "docs/FRONTIER_READINESS_REPORT.md",
               "headline is the blocking fact, not the number"),
        ),
    ),
    PowerPoint(
        id="P7",
        name="bounded_non_claim",
        principle="Forbidden vocabulary is permitted only when negated or "
        "bounded; the metaphor may never become an assertion.",
        deepening="The bounding law recurs from the lexicon linter to the "
        "design-lineage boundary doc to the locked cognition/neural "
        "non-claims — the same wall at every scale.",
        manifestations=(
            _m("test", "scripts/claims_lint.py", "lexicon gate"),
            _m("config", "claims.yaml", "forbidden/qualifier lexicon as data"),
            _m("module", "src/ctios/design_lineage.py", "boundary doc text"),
            _m("metric", "src/ctios/definition_lock.py",
               "cognition/neural locked as non-claims"),
        ),
    ),
)

IDS: tuple[str, ...] = tuple(p.id for p in POINTS)


def get(point_id: str) -> PowerPoint:
    for p in POINTS:
        if p.id == point_id:
            return p
    raise KeyError(point_id)


def validate() -> list[str]:
    """Return one violation per non-fractal or malformed power point.

    Empty list == all seven principles are proven self-similar: each
    recurs at >= 2 real scales spanning >= 2 distinct scale kinds.
    """
    violations: list[str] = []
    if len(POINTS) != 7:
        violations.append(f"expected 7 power points, found {len(POINTS)}")
    seen: set[str] = set()
    for p in POINTS:
        if p.id in seen:
            violations.append(f"{p.id}: duplicate id")
        seen.add(p.id)
        for field in ("name", "principle", "deepening"):
            if not getattr(p, field).strip():
                violations.append(f"{p.id}: empty field {field!r}")
        missing = [m.where for m in p.manifestations if not m.exists()]
        if missing:
            violations.append(f"{p.id}: dead anchors: {missing}")
        if not p.is_fractal():
            violations.append(
                f"{p.id} ({p.name}): not fractal — needs >= {MIN_SCALES} live "
                f"sites across >= 2 scale kinds"
            )
    return violations


def report() -> dict[str, object]:
    """Machine-readable digest of the seven power points."""
    return {
        "power_points": [
            {
                "id": p.id,
                "name": p.name,
                "principle": p.principle,
                "deepening": p.deepening,
                "live_scales": sorted({m.scale for m in p.live_scales()}),
                "sites": [m.where for m in p.live_scales()],
                "fractal": p.is_fractal(),
            }
            for p in POINTS
        ],
        "all_fractal": validate() == [],
    }
