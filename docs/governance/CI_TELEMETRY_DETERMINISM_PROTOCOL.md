# CI Telemetry Determinism Protocol

## 1) Purpose

Define a deterministic control-plane protocol for interpreting GitHub Actions as telemetry instruments. This protocol maps each CI signal to a concrete invariant and repair path so merge decisions are fail-closed, reproducible, and auditable.

## 2) Control-plane model

Canonical model:

`workflow -> job -> step -> command -> invariant -> artifact -> failure class -> repair path`

Rules:

- A green workflow is admissibility telemetry, not scientific validity proof.
- A failed step is classified by failure taxonomy before any fix attempt.
- Every merge decision requires verification-surface closure, not a subset of passing checks.
- Artifact-producing checks must either verify freshness/consistency or fail.

## 3) Workflow inventory

### gate (`.github/workflows/ci.yml`)

- **job: proof-of-life (matrix 3.11/3.12)**
  - verifier manifest static + runtime generation
  - workflow trust audit (`scripts/audit_workflow_trust.py`)
  - dependency trust audit (`scripts/verify_ci_deps.py`)
  - supply-chain aggregate (`scripts/verify_scorecard_prerequisites.py`, `python -m ctios.supply_chain_audit`)
  - lint (`ruff`), type (`mypy --strict src/ctios`), claims lint, doc trust bundle
  - provenance verification (`scripts/provenance_attest.py`)
  - full tests, full fail-closed runner, evidence artifact upload
- **job: external-adversarial**
  - external portability demo script
  - portability report artifact upload

### nctp-state-smoke

- Lint/type/smoke execution for `src/ctios/nctp_state` and `tools/nctp_state_smoke.py`.

### nctp-role-dynamics

- Lint/type/smoke execution for role dynamics subsystem and `tools/nctp_role_dynamics_smoke.py`.

### nctp-promotion-audit

- Lint + execution of `tools/nctp_promotion_audit.py`.

### latency-monitor

- Lint/type/check for observability latency monitor (`src/ctios/observability`, `tools/latency_monitor_check.py`).

### platform-demo

- Full pytest + platform demo shell workflow.

### v7-readiness

- CPU-only readiness checks for v7 + GCP dry-run shell scripts + artifact schema validation.

### conference-smoke

- Reviewer/conference smoke package build and run.

### indi-demo-gate

- External-review one-command demo gate.

## 4) Verification surface map

Primary instrument scripts and inferred invariants:

- `scripts/audit_workflow_trust.py`
  - Invariant: workflow actions are SHA pinned, tag-bound in evidence, explicit permissions, no unjustified write.
  - Artifact: `evidence/WORKFLOW_TRUST_AUDIT.json`.
- `scripts/verify_ci_deps.py`
  - Invariant: CI dependency consumption is lock-driven and declared trust level is not overclaimed.
  - Artifact: `evidence/DEPENDENCY_TRUST_AUDIT.json`.
- `scripts/check_doc_trust.py`
  - Invariant: doc claims are class-bounded, source-bound, boundary-qualified, with required trust-layer files.
  - Artifact: `evidence/DOC_TRUST_AUDIT.json` (validated).
- `scripts/claims_lint.py`
  - Invariant: no forbidden assertive claims, no unqualified metaphor leakage outside disclaimer boundaries.
- `scripts/provenance_attest.py`
  - Invariant: internal file hash manifest and SPDX headers are consistent; external similarity remains explicitly OPEN.
  - Artifact: `provenance_manifest.json`.
- `scripts/internal_adversarial_redteam.py`
  - Invariant: internal adversarial probes remain non-independent and cannot close independence gap by self-production.
  - Artifact: `evidence/INTERNAL_ADVERSARIAL_REDTEAM.json`.



## 4.1) Structured data-contract probes (mandatory)

The following probes are required during forensics and repair for NCTP-related failures.

- packet schema strictness
- unknown-key rejection
- NaN/inf rejection
- bool-as-number rejection
- ragged-shape rejection
- positive horizon contract
- delay distribution normalization
- counterfactual delta consistency
- TASK-05..07 stub honesty
- README test-count consistency
- provenance consistency

Each probe must map to one owning validator/test and one failure class before patching.

## 5) Failure taxonomy

- workflow trust failure
- dependency trust failure
- provenance drift
- claim-boundary violation
- documentation trust failure
- static type contract failure
- lint hygiene failure
- unit/integration test failure
- fail-closed runner failure
- demo portability failure
- nondeterministic behavior
- data-structure contract mismatch
- runtime boundary ambiguity
- stale README/test-count drift
- overly broad PR surface
- hidden scientific claim expansion
- missing instrumentation

Classification rule: first failing check defines primary class; correlated downstream failures are secondary classes.

## 6) Log-forensics procedure

1. Record run identifiers: workflow name, run id, head SHA, branch, matrix axis.
2. Identify first failing step chronologically in the failing job.
3. Map failing step command to this protocol's taxonomy and identify root cause class.
4. Extract artifact evidence (if produced) and inspect status/problematics fields.
5. Determine scope:
   - code invariant breach,
   - governance/documentation boundary breach,
   - artifact freshness/provenance drift,
   - environment/toolchain issue.
6. Define minimal patch candidate (single invariant closure; no cross-surface expansion).
7. Apply minimal repair in the owning scope.
8. Re-run local command parity with failing step.
9. Re-run full required verification surface before merge decision.
10. Document residual risk if any check is intentionally non-claiming (e.g., internal non-independence boundaries).




## 6.1) Workflow -> invariant -> root cause -> minimal patch map

- `gate` -> trust/deps/docs/provenance/tests/runner invariants -> trust drift, dependency drift, claim-boundary breach, runner nondeterminism -> patch only the failing verifier inputs or boundary docs/scripts.
- `nctp-state-smoke` -> packet/runtime state contracts -> schema mismatch, unknown-key acceptance, NaN/inf or ragged payload acceptance -> patch strict validators/tests in `src/ctios/nctp_state` + targeted tests only.
- `nctp-role-dynamics` -> role-transition and metrics contracts -> delay normalization drift, counterfactual delta inconsistency -> patch role-dynamics invariant logic/tests only.
- `nctp-promotion-audit` -> promotion-policy contract -> stale promotion evidence or policy mismatch -> patch promotion-audit rule/evidence mapping only.
- `latency-monitor` -> observability latency contract -> metric boundary/type mismatch -> patch observability checks only.
- `platform-demo` / `conference-smoke` / `indi-demo-gate` -> demo portability and honest boundary outputs -> portability break or stub dishonesty -> patch demo scripts/contracts only.
- `v7-readiness` -> CPU readiness + artifact schema + non-destructive dry-run -> readiness artifact/schema drift -> patch v7 validation path only.

## 7) Merge-readiness protocol

Fail-closed rule:

- Merge readiness is **BLOCKED** unless all required workflows for the PR are green and no required invariant remains unverified.
- “Green subset + skipped boundary check” is not merge-ready.
- Any claim/governance/provenance drift is blocking regardless of runtime test pass.
- Large multi-surface changes (docs+runtime+provenance+tests) require explicit promotion framing and scope justification.

Status outputs:

- `READY_PENDING_ACTIONS`: all checks green, only non-blocking follow-ups remain.
- `BLOCKED`: any required workflow red, any invariant unresolved, or verification-surface incomplete.

## 8) Codex repair protocol

For CI failures handled by Codex agent:

1. Classify failure using taxonomy before editing.
2. Patch only owning files for the classified invariant.
3. Avoid cross-surface expansion unless required by invariant coupling.
4. Re-run failing command first, then full required command set.
5. If provenance manifest drifts due to allowed file updates, regenerate only required provenance entries.
6. Commit with class-tagged message (`ci: fix <failure-class> ...`).
7. Report repaired invariant, commands executed, residual risk, and merge-readiness state.

## 9) Human supervisor checklist

- Workflow run inspected at job/step granularity, not badge-only.
- First-failure classification recorded.
- Repair mapped to explicit invariant.
- Evidence artifacts inspected where applicable.
- No hidden claim expansion in docs/spec/readme.
- PR surface limited to declared control-plane intent.
- Merge-readiness output explicitly set to BLOCKED or READY_PENDING_ACTIONS.

## 10) Anti-patterns found in current repository behavior

- Naming ambiguity: `gate` exists as `ci.yml`; direct file lookup by workflow nickname can fail unless mapped.
- Coverage overlap without explicit matrix rationale: multiple workflows execute overlapping lint/test surfaces; boundaries are implied but not centrally indexed.
- Artifact semantics are distributed across scripts; no single operator playbook previously bound all failure classes to repair paths.
- Demo/smoke workflows validate portability slices, but “green” can be misread as full-system correctness without this protocol.
- Some checks generate/validate artifacts, but operator discipline is required to distinguish stale-artifact drift from functional regressions.

## 11) Required future hardening recommendations

- Add machine-readable workflow-to-invariant index (single source of truth) under `docs/governance/`.
- Add owner mapping (`invariant -> owning file(s)/team`) to reduce triage latency.
- Add deterministic runbook links in each workflow step name (taxonomy key prefix).
- Add explicit “required for merge” policy document mapping branch type to required workflows.
- Add periodic CI drift audit that detects redundant workflow coverage and unexplained overlap.

## 12) Explicit non-claims

This protocol does **not** claim:

- scientific or external validity beyond instrumented checks,
- independence closure from internal self-produced adversarial checks,
- hermetic build guarantees beyond declared dependency trust level,
- production-readiness certification.

It only standardizes deterministic interpretation and repair of repository CI telemetry.
