# Private R&D Protocol — Redacted Hypothesis Interface

This document specifies, field by field, how a private research line
is run through `ctios.falsify` **without disclosing the private
mechanism, dataset, strategy, or theorem content**. It is a contract:
if a step would require leaking private structure, that is a defect in
this protocol, not an accepted cost.

## 1. No private IP required

The engine consumes the *shape* of a hypothesis, never its content.
It needs to know that a claim exists, what would falsify it, and how
to call a function that produces metrics. It does not need to know how
that function works, what data it was built from, or why the
collaborator believes the claim. The private mechanism is a black box
the engine calls and never inspects.

## 2. Redacted hypothesis interface

A hypothesis enters as a pinned skeleton with exactly these fields
(see `examples/indi_redacted_cognitive_time.yaml`):

- `hypothesis_id` — an opaque label; no semantic leakage required.
- `claim` — one sentence, structural, no mechanism.
- `null` — the hypothesis held if the claim is not supported.
- `assumptions` — conditions taken as given (part of the pinned hash).
- `variables` — what is manipulated/measured, by abstract name only.
- `falsifiers` — metric / operator / threshold-key triples that, if
  they trigger, kill the claim.
- `forbidden_claims` — inferences the result may **never** be used to
  support, regardless of outcome.
- `required_artifacts` — what evidence must exist for a verdict.
- `human_review_required` — must be `true`; no autonomous restart.
- `next_experiment_policy` — governance for a non-green outcome.

The private mechanism is supplied separately and locally as a `Probe`:
a callable `probe(thresholds) -> {metric: value}`. The engine imports
nothing from the collaborator's private code; the collaborator wires
the probe in their own environment.

## 3. Safe-to-share fields

These may live in a shared or public repository without risk, because
they describe the *question*, not the *answer or method*:

- the claim and null as abstract sentences,
- assumption and variable **names** (not their realizations),
- falsifier metric names, operators, and threshold keys,
- forbidden-claim list,
- required-artifact list,
- the pinned specification hash (`spec_sha256`),
- the resulting verdict status and battery outcomes.

A reviewer can audit all of the above and learn nothing proprietary.

## 4. Never-share fields

These never enter the public repository, the engine, or any artifact
the engine emits:

- the implementation of the probe (the private mechanism),
- raw or derived private datasets,
- the proprietary strategy, model weights, or trade/research logic,
- the actual content of the private theorem or its proof,
- any numeric realization that would let the mechanism be reconstructed,
- private notes (carried by the collaborator only, marked redacted).

If a verdict artifact would contain any of the above, the run is
misconfigured and must be stopped before it is sealed.

## 5. Evidence without disclosure

The engine emits a sealed verdict (`FALSIFY_<hid>.json`) containing:
the pinned spec hash, the check outcomes, the adversarial battery
outcomes (deterministic / finite / thresholds-load-bearing /
negative-control-fails), the metric values, and the reasons. A metric
value is a scalar the collaborator chose to expose as the falsifier
surface; it is not the mechanism. The reviewer verifies the *process*
(was the kill-test run, did the battery hold, is the threshold
load-bearing) without ever seeing the *method*.

## 6. Human approval gates

Every restart is gated. On a non-green outcome the engine writes a
*proposed* next experiment (`NEXT_<hid>.yaml`) and stops. It does not
run it. `human_review_required: true` is mandatory in the skeleton; a
skeleton without it is rejected. The apparatus is a falsification loop
with a human at every boundary, explicitly not an autonomous research
agent.

## 7. Claim-boundary policy

A claim's external-facing text cannot exceed the implemented
mechanism. A machine-checkable lexicon blocks cognition /
general-intelligence / neural-equivalence / consciousness language
outside an explicit disclaimer, enforced in CI and tests. A redacted
skeleton inherits this: its `forbidden_claims` list is honored as a
hard boundary, and the engine will not let a survived check be
narrated as more than the check actually tested.

## 8. Failure logging

Every non-green outcome is sealed, not discarded. A negative is a
first-class artifact with a reproduction path. A failed lineage is
closed before the next one opens. There is no mechanism by which a red
result can be silently overwritten, and the pinned hash makes
post-hoc threshold changes detectable.

## 9. Next-experiment governance

When a hypothesis does not pass, the proposed next experiment follows
fixed rules, encoded in `next_experiment_policy`:

- `auto_run: false` — never executed automatically.
- `tighten_surviving_checks: true` — checks that survived are made
  stricter (×0.9), never loosened.
- `loosen_failed_checks: false` — a failed check is never relaxed to
  manufacture a pass.
- `failed_boundary_becomes_focus: true` — the boundary that broke is
  the subject of the next experiment.
- assumptions behind a failure are demoted to explicit open questions.

The collaborator decides whether to run the proposal. The engine only
proposes.
