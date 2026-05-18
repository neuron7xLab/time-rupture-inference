# System Card: TRI-Falsify

**TRI-Falsify — Temporal Rupture Inference Falsification Apparatus.**
A research-systems card (model-card structure, applied to an apparatus,
not a model).

## System name

TRI-Falsify. Used consistently across all conference-grade documents.
The temporal benchmark inside it is *TRI — Temporal Rupture Inference*;
the apparatus that audits hypotheses (including TRI's own) is
*TRI-Falsify*.

## Intended use

Auditing a research hypothesis — public or privately redacted — by
forcing it through a pinned falsifier before any belief is updated.
Producing sealed, reproducible verdicts and decision-gated next
experiments. Demonstrating a falsification discipline that resists
self-deception in model-as-instrument research.

## Non-intended use

Not a benchmark leaderboard, not a model of cognition, not an
autonomous research agent, not a claim generator. It does not decide
whether a private theorem is true; it tests whether a pinned claim
survives its own kill-test.

## Core abstraction

```
RedactedHypothesisSpec + Probe + FalsifierBattery
    → SealedVerdict + EvidenceLedger + NextExperimentProposal
```

`RedactedHypothesisSpec` = `ctios.falsify.HypothesisSpec` (claim / null
/ assumptions / variables / falsifier checks), optionally authored as a
redacted YAML skeleton. `Probe` = an opaque callable `probe(thresholds)
-> {metric: value}` supplied locally. `FalsifierBattery` =
`run_battery` (deterministic / finite / thresholds-load-bearing /
negative-control-fails). `SealedVerdict` = `Verdict` +
`FALSIFY_<hid>.json`. `EvidenceLedger` = preserved RED/GREEN artifacts
under `evidence/`. `NextExperimentProposal` = `next_experiment` →
`NEXT_<hid>.yaml`, never auto-run.

**IP-safe platform layer** (the strongly-typed, redaction-first
realization of the same abstraction): `ctios.redacted`
(`RedactedHypothesisSpec` + structural invariants), `ctios.redacted_io`
(load / validate / deterministic `spec_sha256`, forbidden-key
fail-closed), `ctios.opaque_probe` (`OpaqueProbe` Protocol +
`ProbeResult`), `ctios.falsifier_battery` (battery v2, 10 checks →
INADMISSIBLE / CONDITIONAL / PASS), `ctios.spec_compiler`
(`BLOCKED_UNTIL_PROBED` compiled object), `ctios.human_gate` +
`ctios.review_cli` (append-only approval audit), `ctios.report`
(sealed `REVIEW_REPORT.md`). One command: `bash scripts/platform_demo.sh`.

## Inputs

A pinned hypothesis specification (hashed: claim, null, thresholds,
checks, assumptions, variables) and a probe callable. Optionally a
negative-control probe.

## Outputs

A sealed verdict (status + battery + metrics + reasons + spec sha256),
a preserved evidence artifact on non-GREEN, and a decision-gated next
experiment proposal.

## Evidence artifacts

`FALSIFY_<hid>.json` (sealed verdict), `NEGATIVE_FALSIFY_<hid>.md`
(sealed negative), `NEXT_<hid>.yaml` (proposal), the frozen v4/v5
runner outputs, and `provenance_manifest.json` (sha256 + SPDX).

## Failure modes caught

Non-deterministic probe; non-finite metric; decorative
(non-load-bearing) threshold; non-discriminative (pseudo-GREEN)
negative control; post-hoc threshold tuning (detected via spec sha256);
claim text exceeding mechanism (lexicon gate). Full taxonomy:
`docs/FAILURE_TAXONOMY.md`.

## Failure modes not caught

A probe that is deterministic and discriminative but encodes a hidden
degenerate solution; a hypothesis whose redaction is itself
ill-posed; external originality of the underlying ideas; real-world
validity of a synthetic benchmark. Stated, not hidden.

## Reproducibility contract

Clean clone → exact commands → byte-identical frozen numbers. Full
contract and the expected outputs: `docs/REPRODUCIBILITY_CONTRACT.md`.

## Human approval boundary

Nothing auto-runs. A non-GREEN outcome writes a *proposed* next
experiment and stops. `human_review_required: true` is mandatory in a
redacted skeleton; absent, it is rejected.

## Safety / misuse considerations

The redacted interface is designed so a private mechanism, dataset, or
theorem never enters the repository. Misuse to launder a weak claim is
resisted by the battery and the claim-boundary lexicon, not by trust.
The apparatus cannot certify correctness; asserting it does would
violate its own claim boundary.

## Claim boundary

No cognition, consciousness, AGI, biological-fidelity, or
universal-theory-of-time claim is made. The single claim: the
difference between a plausible story and a survived falsifier can be
made mechanical, reproducible, and safe to run on a private hypothesis
without disclosing it. Scope: `docs/INDI_LIMITATIONS.md`, `docs/SPEC.md`.
