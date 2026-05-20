# Required Checks Matrix

## Purpose

This matrix maps required GitHub checks to the protection reason, local command, and failure meaning.

It is the reviewer's control map for deciding whether a PR is eligible to merge into `main`.

## Required checks

| GitHub check | Local equivalent | Protects | Failure meaning |
|---|---|---|---|
| `gate / proof-of-life (3.11)` | run CI parity commands under Python 3.11 | compatibility and trust boundary | merge blocked |
| `gate / proof-of-life (3.12)` | run CI parity commands under Python 3.12 | current primary runtime | merge blocked |
| `gate / external-adversarial` | `bash scripts/external_adversarial_demo.sh` | adversarial portability smoke | merge blocked |
| `v7-readiness / v7-readiness` | `make v7-prereg-check && make v7-cpu-smoke && make v7-artifact-check` or workflow commands | v7 cloud-readiness without cloud spend | merge blocked |
| `platform-demo / platform-demo` | `bash scripts/platform_demo.sh` | IP-safe public demo | merge blocked if public/demo surface touched |
| `conference-smoke / conference-smoke` | `bash scripts/conference_smoke.sh` | reviewer-facing reproducibility path | merge blocked if reviewer path touched |
| `indi-demo-gate / indi-demo` | `bash scripts/indi_demo.sh` | private-safe external review package | merge blocked if external review path touched |

## Proof-of-life surface

The proof-of-life job contains:

```text
verifier manifest static check
verifier manifest runtime check
workflow trust audit
dependency trust audit
scorecard prerequisite check
supply-chain audit
ruff
mypy --strict src/ctios
claims lint
documentation trust gates
provenance attestation
pytest
fail-closed runner
```

## Merge readiness rule

A PR may merge only when:

```text
all required checks are green
AND required conversations are resolved
AND CODEOWNER review requirement is satisfied
AND no claim boundary expansion is unsupported
AND rollback path is documented
```

## Status interpretation

```text
pending  -> wait
failure  -> block merge
cancelled -> rerun or block merge
skipped  -> acceptable only if workflow scope explicitly does not apply
success  -> admissible
```

## Manual exception protocol

A manual exception must record:

- check skipped or failed
- reason
- risk
- exact follow-up issue
- rollback plan

Exceptions are not allowed for:

- provenance failures
- trust-boundary failures
- claim-boundary failures
- direct evidence contradiction
- critical invariant failures
