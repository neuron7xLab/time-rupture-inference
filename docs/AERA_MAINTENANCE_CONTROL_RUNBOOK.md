# AERA Maintenance-Control Runbook

## Purpose

This runbook converts the current post-PR #57 repository state into a bounded maintenance-control loop.

It is not a new scientific claim and does not promote the experimental adapter. It defines operator actions, automated checks, and promotion boundaries for the current repository state.

## Current state assumption

- `main` contains merged PR #55 and PR #57.
- PR #57 introduced an isolated experimental adapter under `ctios.experimental.*`.
- The canonical path remains `ctios.neural_agent.NeuralTemporalAgent` and `ctios.neural_runner.run_neural_demo`.
- Experimental code is not promoted by directory placement alone.

## Control-plane priorities

```text
P0: remove stale branch noise
P1: verify local main after merge
P2: define experimental provenance boundary
P3: define experimental promotion protocol
P4: add operator tools for branch and README count hygiene
P5: add narrow experimental contract checks before any promotion PR
```

## Execution-plane commands

### P0: stale branch removal

```bash
git fetch --prune origin
git ls-remote --heads origin 'pr-50/external-reproduction-bundle-intake-clean'
# after confirming no open PR and supersession by merged work:
git push origin --delete pr-50/external-reproduction-bundle-intake-clean
```

### P1: post-merge verification seal

```bash
git fetch --prune origin
git switch main
git pull --ff-only origin main

PYTHONPATH=src pytest tests -q
PYTHONPATH=src python scripts/provenance_attest.py
bash scripts/external_adversarial_demo.sh
bash scripts/conference_smoke.sh
bash scripts/indi_demo.sh
```

Pass condition:

```text
Local main reproduces the same verification surface expected from CI.
```

Fail condition:

```text
Any local drift, missing provenance entry, README count mismatch, or demo gate failure blocks further promotion work.
```

## Experimental adapter status

The experimental attention adapter is a candidate substrate only.

Allowed:

- narrow deterministic tests
- finite-output checks
- invalid-stream rejection checks
- bounded-history checks
- runner metric-key checks
- baseline comparison scaffolding

Forbidden before promotion:

- replacing canonical v9 path
- expanding public claims
- changing release-gate language
- adding provenance-root inclusion without policy decision
- treating successful import as evidence of capability

## AERA decision states

```text
experimental_candidate -> contract_checked -> preregistered -> sandbox_evaluated -> promotion_candidate -> canonical_or_rejected
```

No step may be skipped.

## Promotion trigger

The experimental adapter can enter a promotion PR only after:

- experimental contract checks exist
- a preregistration file exists
- baseline comparison is defined
- failure acceptance rule is documented
- provenance policy is explicit
- rollback path is trivial
- README claims remain unchanged unless evidence changes

## Operator escalation rule

Escalate to human only when a decision changes:

- claim boundary
- canonical model path
- public-facing README language
- provenance root policy
- release-gate semantics
- branch deletion of non-superseded work

Routine count sync, stale-branch listing, and local verification commands are operator-tool work, not research decisions.
