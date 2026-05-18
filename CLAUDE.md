# CLAUDE.md — project operating contract

## Project identity

TRI-Falsify: a falsification-first temporal-inference and
hypothesis-auditing apparatus. Core abstraction:
`RedactedHypothesisSpec + Probe + FalsifierBattery → SealedVerdict +
EvidenceLedger + NextExperimentProposal`. The deliverable is the
discipline, not a result.

## Forbidden claims (hard)

Never assert — anywhere outside an explicit non-claim / limitation /
`<!-- claims:disclaimer -->` block — that the system has cognition,
consciousness, AGI, general intelligence, biological fidelity, a
universal theory of time, or that any private theorem is correct, or
that results have real-world validity. Originality is integration-only;
do not assert novelty beyond integration (external originality is OPEN).

## Allowed claim grammar

A claim is admissible only as: **claim → falsifier → evidence →
boundary**, where the falsifier was pinned (hashed) before the run and
did not trigger, and the evidence is a sealed artifact. Scope every
positive to exactly what the test measured. Forbidden vocabulary is
permitted only when negated/bounded on the same line or inside a
disclaimer block.

## Rules

- **Test-before-doc.** No new claim enters docs until it maps to a
  passing test, a sealed artifact, or an explicit limitation entry.
- **No frozen-artifact rewrite.** Never modify frozen v4/v5 numbers
  (`learned 0.8830 / injected 8.0028 / oracle 0.7933`,
  `gain 0.8680 / null_gap 0.0000`) or any preserved RED/NEGATIVE
  artifact. Touching `evidence/` frozen files requires the literal
  token `PR21_ALLOW_FROZEN_TOUCH` in the request.
- **No network in CI/tests.** No download/fetch in tests or CI; all
  runs are CPU-only, deterministic, offline.
- **Evidence-ledger update.** Every non-GREEN path writes a *proposed*
  next experiment and stops; it never auto-runs. Sealed artifacts are
  append-only; REDs are preserved.
- **Fail closed.** Ambiguity, missing falsifier, or boundary expansion
  → block, do not proceed.

## Final response checklist

Before reporting done, confirm: ruff clean · mypy --strict clean ·
extended claims-lint PASS · provenance PASS · pytest exit 0 · frozen
v4/v5 byte-identical · no preserved RED deleted · no next experiment
auto-run · every new claim mapped to test/artifact/limitation.
