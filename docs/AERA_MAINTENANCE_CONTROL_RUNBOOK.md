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

The short local seal below is a maintenance smoke surface only. It does **not** claim full CI parity.

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

Pass condition for the short seal:

```text
Local main passes the selected maintenance smoke checks needed before starting additional operator work.
```

Fail condition for the short seal:

```text
Any local drift, missing provenance entry, README count mismatch, or demo gate failure blocks further promotion work.
```

### P1-full: CI-parity verification seal

Use this when the operator wants to reproduce the required hard gate surface from `.github/workflows/ci.yml` before trusting a merge candidate.

The CI job runs the proof-of-life surface on Python 3.11 and Python 3.12. For true parity, repeat the commands below under both versions.

```bash
git fetch --prune origin
git switch main
git pull --ff-only origin main

python tools/check_verifier_manifest_static.py --repo .
python tools/verifier_manifest.py
python scripts/audit_workflow_trust.py
python scripts/verify_ci_deps.py
python scripts/verify_scorecard_prerequisites.py
PYTHONPATH=src python -m ctios.supply_chain_audit

pip install -q -r requirements-ci.lock
ruff check src tests scripts
mypy --strict src/ctios
python scripts/claims_lint.py

python scripts/build_doc_trust_audit.py --verify-only
python scripts/check_doc_claim_sources.py
python scripts/check_doc_trust.py
python scripts/provenance_attest.py

PYTHONPATH=src pytest tests -q
PYTHONPATH=src python -m ctios.runner --mode full
bash scripts/external_adversarial_demo.sh
```

Pass condition for CI parity:

```text
The commands above pass under the same Python versions used by CI, and the GitHub PR checks are green.
```

Fail condition for CI parity:

```text
Any verifier trust, workflow trust, dependency trust, supply-chain, lint, type, claim, documentation, provenance, test, release-gate, or external-adversarial failure blocks merge readiness.
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
