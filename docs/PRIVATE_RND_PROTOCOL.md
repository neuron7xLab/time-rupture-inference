# Private R&D Protocol — Redacted Hypothesis Interface

How a private research line runs through `ctios.falsify` **without
disclosing the private mechanism, dataset, strategy, or theorem
content**. This is a contract, not a courtesy.

## The guarantee, in one place

- I do not need your private theorem.
- I do not need your proprietary data.
- I do not need your company strategy.
- You provide only a redacted structure.
- Human approval is required before any next experiment.
- Nothing auto-runs.
- Nothing private gets committed to this repository.

## What is safe to share

| Field | Safe to share? | Reason | Example |
|---|---|---|---|
| claim | yes | a sentence about the question, not the method | "estimator infers regime change faster than baseline" |
| assumptions | yes | conditions, not mechanism | "estimator never sees the switch time" |
| variables | yes | abstract names only | `manipulated: shift_magnitude` |
| falsifiers | yes | metric/op/threshold-key, not how metric is produced | `post_error <= ceiling` |
| forbidden inferences | yes | a boundary list strengthens trust | "no cognition/AGI claim" |
| evidence type | yes | what artifact must exist, not its contents | `sealed_verdict_json` |
| private mechanism | **no** | this is the IP; supplied as a local opaque probe | *never in repo* |
| proprietary data | **no** | reconstructable signal | *never in repo* |
| company strategy | **no** | not needed to test a claim | *never in repo* |
| theorem content | **no** | the engine tests shape, not proof | *never in repo* |

## 1. No private IP required

The engine consumes the *shape* of a hypothesis, never its content. It
needs to know a claim exists, what falsifies it, and how to call a
function that returns metrics. It never learns how that function works,
what data built it, or why you believe the claim.

## 2. Redacted hypothesis interface

A hypothesis enters as a pinned skeleton with the fields in
`examples/indi_redacted_cognitive_time.yaml`: `hypothesis_id`, `claim`,
`null`, `assumptions`, `variables`, `falsifiers`, `forbidden_claims`,
`required_artifacts`, `human_review_required` (must be `true`),
`next_experiment_policy`. The private mechanism is supplied separately
and locally as a `Probe`: a callable `probe(thresholds) -> {metric:
value}`. The engine imports nothing from your private code; you wire
the probe in your own environment.

## 3. Safe-to-share fields

The "yes" rows of the table above, plus the pinned `spec_sha256` and
the verdict status. A reviewer can audit all of it and learn nothing
proprietary.

## 4. Never-share fields

The "no" rows: the probe implementation, raw/derived private data, the
strategy or model logic, the theorem content or its proof, and any
numeric realization that would let the mechanism be reconstructed.
Private notes stay with you, marked redacted. If a verdict artifact
would contain any of these, the run is misconfigured — stop before it
seals.

## 5. Evidence without disclosure

The sealed verdict (`FALSIFY_<hid>.json`) carries the pinned hash,
check outcomes, battery outcomes (deterministic / finite /
thresholds-load-bearing / negative-control-fails), metric values, and
reasons. A metric value is a scalar you chose to expose as the
falsifier surface — it is not the mechanism. The reviewer verifies the
*process*, never the *method*.

## 6. Human approval gates

Every restart is gated. On a non-green outcome the engine writes a
*proposed* `NEXT_<hid>.yaml` and stops. It does not run it.
`human_review_required: true` is mandatory; a skeleton without it is
rejected.

## 7. Claim-boundary policy

A claim's external text cannot exceed its mechanism. A machine-checkable
lexicon blocks cognition / general-intelligence / consciousness
language outside an explicit disclaimer, enforced in CI and tests. A
skeleton's `forbidden_claims` list is honored as a hard boundary.

## 8. Failure logging

Every non-green outcome is sealed, not discarded — a first-class
artifact with a reproduction path. A failed lineage closes before the
next opens. The pinned hash makes post-hoc threshold changes detectable.

## 9. Next-experiment governance

On failure the proposal follows fixed rules in `next_experiment_policy`:
`auto_run: false`; `tighten_surviving_checks: true` (×0.9, never
loosened); `loosen_failed_checks: false`;
`failed_boundary_becomes_focus: true`; failed assumptions demoted to
open questions. You decide whether to run it. The engine only proposes.
