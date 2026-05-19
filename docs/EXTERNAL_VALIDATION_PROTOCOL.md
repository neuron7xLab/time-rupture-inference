# External Validation Protocol

The one thing standing between CONDITIONALLY_READY and READY is not
code — it is an independent person running the private redacted layer
without leaking IP. This defines exactly that run.

## Roles

- **Collaborator (external):** owns a private hypothesis and its
  mechanism/data. Never shares them.
- **Apparatus (this repo):** receives only a redacted skeleton + a
  reference to a *locally executed* opaque probe; emits only sanitized
  verdict artifacts.

## Steps

1. Collaborator copies `examples/external_reviewer_packet_template.yaml`
   and fills the **redacted skeleton only**: claim, null, assumptions,
   variables, falsifiers, forbidden inferences, evidence requirements.
   No mechanism, no data, no theorem text.
2. Collaborator implements an opaque probe **on their machine** behind
   `ctios.opaque_probe.OpaqueProbe` (a callable returning a
   `ProbeResult`). The repo core is NOT edited.
3. Collaborator runs the local pipeline (`ctios.spec_compiler` →
   probe → `ctios.falsifier_battery`) producing a sealed verdict.
4. Collaborator inspects every emitted artifact and confirms **no
   never-share field leaked** (mechanism, raw data, theorem content).
5. Collaborator returns only: the sanitized verdict JSON, the spec
   sha256, the battery outcomes, and a completed
   `EXTERNAL_REVIEW_FORM.md`.
6. A maintainer updates `evidence/external_validation_status.json`:
   `real_external_collaborator_run: true`,
   `status: EXTERNAL_RUN_COMPLETE`, `claim_upgrade_allowed: true`
   **only** if step 4 is attested.

## Status semantics

- `EXTERNAL_RUN_PENDING` — default. Mock/simulated pack only. Status
  capped at CONDITIONALLY_READY.
- `EXTERNAL_RUN_COMPLETE` — a real external run attested; READY becomes
  evaluable (still subject to all engineering gates).

A simulated external pack passing (`simulated_external_pack_passed`)
**does not** satisfy this protocol and never upgrades the claim. This
is enforced by `tests/test_external_validation_status.py` and
`ctios.readiness_score`.

## Hard rule

If `real_external_collaborator_run == false`, no document, report, or
scorer may present status as READY or PRODUCTIZABLE. Numerical scores
do not override this blocking fact.
