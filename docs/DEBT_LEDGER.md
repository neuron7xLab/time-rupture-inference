# DEBT LEDGER — explicit, honest, no hiding

Two CI-hardening mega-protocols (v2.0: phases 0–12 / PRs A–F; v3.0:
phases 1–12 / PRs G–J) were specified. Delivered so far: **PR #34**
(v3 Phase 1–3, verifier trust boundary) + **this PR** (two closed
shortcuts + this ledger). Everything else below is **open debt**,
named, with status and priority. Deferral was a one-PR-one-purpose
choice; it is still *not done*, and is recorded as such.

## Closed in this PR (were genuine shortcuts)

| id | item | status |
|---|---|---|
| S1 | Phase 0 baseline snapshot (skipped before the PR #34 ci.yml edit) | CLOSED (`docs/reports/CI_BASELINE_SNAPSHOT.md`, late + honestly marked) |
| S2 | CI invoked bare `mypy` (config-dependent) while ci.yml was edited | CLOSED (`mypy --strict src/ctios` + `tests/test_ci_mypy_explicit.py`) |

## Open debt — v2.0 (TRI-CI-MECHANISM-HARDENING)

| id | phase | item | priority | note |
|---|---|---|---|---|
| D1 | 1 | `workflow_inventory` module+tests+docs | HIGH | gates Phase 10; do before any trigger change |
| D2 | 2 | deterministic dependency contract (CI consumes a lock) | HIGH | `requirements-lock.txt` exists but CI still loose-pips; coherence unproven |
| D3 | 3 | pip cache (perf only, no semantic role) | LOW | safe, low value |
| D4 | 4 | action-runtime warning audit (measure, not assume) | MED | Node-X premise still unverified |
| D5 | 5 | fetch-depth safety experiment | MED | `fetch-depth: 0` kept until proven safe to cut |
| D6 | 6 | typed-tests strict path (`mypy --strict … tests`) | LOW | src strict done; tests strict is a separate hardening |
| D7 | 7 | claims-lint erosion guard + baseline + tests | HIGH | real anti-erosion mechanism, not yet built |
| D8 | 8 | adversarial trace audit (structural) | MED | superseded scope by v3 Phase 8 (semantic) |
| D9 | 9 | artifact-freshness in CI | MED | functionality exists in `artifact_assertions.assert_fresh_for_commit`; no standalone `ctios.artifact_freshness` module — protocol reference is to a non-existent module; record, do not invent decoration |
| D10 | 10 | workflow trigger consolidation | MED | blocked on D1 |
| D11 | 11 | badge accuracy + `test_readme_badges` | LOW | README badges still static |
| D12 | 12 | CI hardening report | LOW | emit after D1–D7 |

## Open debt — v3.0 (ANTI-SELF-DECEPTION)

| id | phase | item | priority |
|---|---|---|---|
| D13 | 4 | hermeticity model + audit + level classification | HIGH |
| D14 | 5 | hash-locked dependency contract (`--require-hashes`) | HIGH |
| D15 | 6 | offline wheelhouse experiment | LOW |
| D16 | 7 | container pinning (digest) experiment | LOW |
| D17 | 8 | adversarial trace semantic invariants | HIGH |
| D18 | 9 | trace-forgery probes | HIGH |
| D19 | 10 | trace provenance binding | MED |
| D20 | 11 | CI integration of hermeticity + trace gates | MED | verifier-root in CI = done (PR #34) |
| D21 | 12 | trust-boundary docs sweep (SECURITY_AND_TRUST_BOUNDARY, HERMETICITY_MODEL, TRACE_INVARIANT_CONTRACT, RESIDUAL_RISKS update) | MED |

## Honest summary

Open: **21 items** (D1–D21) + 0 hidden. Recommended order: D7 (claims
erosion) → D2/D14 (deterministic+hash-locked deps, the real
supply-chain debt) → D17/D18 (semantic trace, kills trace-forgery) →
D1→D10 (inventory then triggers). Each is its own evidence-producing
PR; no batch. Status ceiling unchanged:
**CONDITIONALLY_READY_HARDENED_CI_PLUS** — none of this reaches READY,
which still needs a real external collaborator proof bundle.
