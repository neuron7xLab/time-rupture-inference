# Preserved Negative — Predictive Simulation vs Imitation

**Status: PARTIAL (not GREEN). Pinned before the run; not nudged.**
Spec: `prereg/predictive_simulation.yaml` (sha recorded in the sealed
`evidence/FALSIFY_predictive_simulation_vs_imitation.json`).

This is a result, not a defect. It is kept under closure-before-restart
(V2) and verdict-isolation (V7): a legitimate non-GREEN keeps CI green
because the scientific verdict is never asserted in tests.

## Reasoning-contract trace

1. **Falsification anchor.** "simulation ⊳ imitation" is FALSE if
   `imit_detect_rate ≥ sim_detect_rate`, or `sim_null_false_alarm > α`,
   or `leakage > 0`. Tested by a 3-arm run (predictive cycle / echo
   imitation / clairvoyant-leak) over rupture **and** null streams.
2. **Operational distinction (pre-committed).** Self-detection of the
   regime change from the agent's *own* one-step prediction error via a
   frozen-reference Page-Hinkley statistic; hit window `[t*, t*+0.2n]`,
   12 seeds. MAE is reported, never gated (the echo is a strong MAE
   baseline — gating MAE would be dishonest).
3. **Pre-registered metrics.** `sim_detect_rate ≥ 0.50`,
   `imit_detect_rate ≤ 0.0`, `sim_null_false_alarm ≤ 0.10`,
   `leakage ≤ 0.0`; `separation`, `sim_post_mae` report-only.
4. **Adversarial probe (designed first).** `ClairvoyantEchoProbe`: a
   model-free echo that hard-codes detection at `t*`. It can only know
   `t*` by being handed it → `leakage > 0` → RED. A detect-rate-only
   gate would pass it; this spec's leakage + null-false-alarm checks
   block it.
5. **Boundary — enumerated forbidden claims.** This is NOT a model of
   the brain, neurons, or biological cognition; NOT consciousness,
   sentience, intelligence, or AGI; NOT a universal theory of time or
   perception; it does NOT claim MAE superiority over the imitation;
   a GREEN would NOT prove any real-world or private theorem.
6. **Minimal kill test.** Inject `t*` into the echo (clairvoyant leak):
   a correct implementation MUST flip to RED via the leakage check.
   Verified: `tests/test_predictive_simulation.py`.

## Verdict (single pinned run)

| metric | value | threshold | result |
|---|---:|---|---|
| sim_detect_rate | 0.417 | ≥ 0.50 | **FAIL** |
| imit_detect_rate | 0.000 | ≤ 0.00 | OK |
| sim_null_false_alarm | 0.750 | ≤ 0.10 | **FAIL** |
| leakage | 0.000 | ≤ 0.00 | OK |
| separation (report) | 0.233 | — | — |
| sim_post_mae (report) | 0.901 | — | — |

Battery: deterministic ✓ finite ✓ thresholds-load-bearing ✓
negative-control-fails ✓ (the clairvoyant-leak kill test fires).

## What this proves and does not

**Verified (survives its falsifier):** the *structural dissociation* —
a surface imitator provably cannot self-detect the rupture
(`imit_detect_rate = 0.0`, by construction it forms no expectation),
and the leakage kill test is active and discriminative.

**Falsified (the honest negative):** the naive predictive-error
detector as built is **not** a verified simulation under the
pre-registered criterion. It false-alarms on no-rupture streams at
**0.75** and reaches only **0.417** rupture-detection — a frozen-PH
statistic on a single re-converging scalar is not a valid change
detector at these bounds. This is the informative content: a
predictive cycle is necessary but not sufficient for a *verified*
simulation; the detection layer is the open boundary.

## Auto-proposed next experiment (decision-gated, NOT run)

`prereg/NEXT_predictive_simulation_vs_imitation.yaml` is emitted by the
engine: surviving checks tightened ×0.9, the failed boundary
(false-alarm control + detection power) becomes the focus. It is a
proposal; no next experiment auto-runs.
