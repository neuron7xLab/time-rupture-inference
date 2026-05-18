# CTI-OS / time-rupture-inference — Lineage State (stage closure)

Single canonical state-of-the-research-line. Every lineage is preserved;
no RED erased; no threshold ever tuned to green. This document closes
the current stage — it is a convergence artifact, not new science.

## Lineage ledger

| line | verdict | what it established / localized |
|---|---|---|
| v1 | 🔴 RED | drift detector poisoned by cold-start (instrument bug) |
| v2 | 🟢 GREEN | base proof of life |
| v3 | 🔴 RED | two new controls mis-specified (instrument bugs) |
| v4 | 🟢 GREEN | doctoral critique closed → released `v0.1.0`, **frozen** |
| v5 | 🟢 GREEN | minimal causal-action: gain 0.868, action_null 0.000 |
| v6 | 🔴 RED | precision-weighting (Kalman) ≠ better — no headroom |
| v7 | 🔴 RED | learned reservoir/SSM ≤ heuristic on near-oracle bench |
| v7-diag | — | **NO_HEADROOM**: heuristic within 14.1% of oracle floor → boundary is the *task*, not the model |
| v8 | 🔴 RED | scalar-inexpressible env: trigger ~1.2e-5/step → decorative |
| v8.1 | 🔴 RED | frequency fixed (1500 triggers); inexpressibility *real* but carrier-masked (gap 0.15<0.25) |
| v8.2 | 🟠 PARTIAL_RED | trigger-scoped+carrier-controlled: signal **confirmed & carrier-robust** (tc 0.470, cc 0.465); reference history-oracle under-specified (h2r 4.22) |

## What is proven (cumulative, honest)

1. v4 prediction-error temporal adaptation: GREEN, frozen, byte-identical
   across every subsequent commit (`learned 0.8830 / injected 8.0028 /
   oracle 0.7933`).
2. v5 minimal causal-action: GREEN, opt-in, claim-bounded.
3. On the original rupture class, added model complexity (precision,
   reservoir, SSM) **cannot pay** — the disciplined scalar heuristic is
   ~oracle (NO_HEADROOM). Three root-convergent negatives.
4. A scalar-inexpressible signal **can** be constructed and is **real
   and carrier-robust** (v8.2: confirmed under trigger-scoped and
   carrier-controlled diagnostics, not a noise artifact).

## Precise current open question (narrowest in the whole line)

Not "is a stronger model better" and not "does the environment have
structure". Exactly: **does a correctly-specified history oracle reach
the noise floor on the trigger channel** (`history_to_regime_distance ≤
0.35`)? v8.2 reference oracle (naive "reuse last sign") does not
(h2r=4.22) because of post-hidden-flip sign-recovery.

## Exact next pre-registered step (decision-gated, NOT auto-run)

v8.3 — pre-register a correctly-specified history oracle (fast
hidden-flip detection / sufficient context statistic) and test
`h2r ≤ 0.35` on the trigger channel under the **already-pinned** v8.2
gap thresholds. Inventing that oracle now, post-hoc, to flip
PARTIAL_RED→GREEN is forbidden tuning; it requires its own
pre-registration with v8.2 PARTIAL_RED as the preserved parent
(closure-before-restart). Only a v8.3 GREEN makes learned
sequence-model testing scientifically askable for the first time.

## Frozen invariants (verified this stage)

v4 `0.8830/8.0028/0.7933` byte-identical · v5 `gain 0.8680` · v6 RED ·
ruff + mypy --strict + claims-lint + provenance + 116 tests green · CI
(gate 3.11/3.12 + v7-readiness) green · every research verdict isolated
from CI (a legitimate RED/PARTIAL keeps main green) · all negatives in
`evidence/` preserved.

## Claim boundary (unchanged)

A narrow, gate-enforced, falsifiable temporal-adaptation result and a
validated task-design diagnostic line. **Not** intelligence / cognition
/ AGI / a learned-model-advantage claim. No learned model has been
trained anywhere in v6–v8.2.
