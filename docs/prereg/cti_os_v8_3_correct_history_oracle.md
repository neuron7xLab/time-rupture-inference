# CTI-OS v8.3 — Correctly-specified history oracle (pre-registration)

Pinned **before** the diagnostic. No learned model. Parent:
evidence/V8_2_PARENT_PARTIAL_RED.md. v8.2 thresholds REUSED unchanged.

## 1. Parent
v8.2 PARTIAL_RED: signal real & carrier-robust (tc 0.470, cc 0.465);
reference history oracle h2r=4.22 ≫ pinned 0.35.

## 2. Hypothesis
A correctly-specified causal history oracle (robust sign re-locking from
observed post-trigger deviations, fast recovery after the hidden flip,
no z/future/schedule access) reaches the trigger-channel noise floor
(`history_to_regime_distance ≤ 0.35`), turning v8.2 PARTIAL_RED into
GREEN under the **already-pinned** v8.2 thresholds.

## 3. Null hypothesis
Even a correctly-specified causal oracle cannot reach h2r ≤ 0.35,
because one hidden context flip with δ≫σ forces ≥1 unavoidable large
error whose amortized cost alone exceeds the pinned distance — i.e. the
v8.2 gate is information-theoretically unattainable by ANY causal oracle
under these env parameters (a benchmark-design boundary, not an oracle
bug).

## 4. Pre-run analytic discriminator (decisive)
Before the diagnostic, derive the causal lower bound:
`h2r_causal_min = (E[forced-error MAE contribution per seed]) /
regime_trigger_mae`, where the forced contribution = (number of
unavoidable wrong-sign triggers from one hidden flip and the cold prior)
× ~2δ, amortized over triggers/seed. Emit it as an artifact BEFORE
running the oracle. If `h2r_causal_min > 0.35` the null is proven
analytically and no oracle can pass — reported honestly.

## 5. Correctly-specified history oracle (spec, frozen)
- Detect trigger from observed (short,short,long) categorized window
  (obs-only, identical to scalar's detectability).
- Maintain the observed post-trigger sign stream; current sign estimate
  = most-recent observed post-trigger sign (Bayes-optimal for a
  piecewise-constant sign that flips once — proven, not heuristic).
- No access to z / future / schedule / trigger labels.
- This is the causal optimum for sign; it cannot beat the analytic
  bound. Implementing it makes (a) vs (b) measurable.

## 6. Thresholds (REUSED from v8.2, pinned, unchanged)
trigger_context_gap_ratio_min=0.35, carrier_controlled_gap_ratio_min=0.25,
history_to_regime_distance_max=0.35, trigger_count_min=300,
aliasing_rate_min=0.05, same_obs_diff_future_rate_min=0.05.

## 7. Verdicts
- GREEN: structural ∧ tc≥0.35 ∧ cc≥0.25 ∧ h2r≤0.35 ∧ ordering ∧
  deterministic ∧ no model. Then stronger-model testing is, for the
  first time, scientifically askable.
- BOUNDARY_RED: correctly-specified oracle ≈ analytic causal minimum AND
  that minimum > 0.35 → the gate is unattainable by construction; the
  defect is benchmark parameterization (δ/σ/flip/threshold), NOT the
  oracle. Next = a NEW v8.4 pre-registration re-deriving env params or
  the h2r gate from first principles. NOT a v8.3 edit.
- RED: any other failure.
RED/BOUNDARY_RED preserved, never tuned.

## 8. No-learned-model rule
No GRU/SSM/reservoir/transformer/MLP/policy learner.

## 9. Claim boundary
Allowed if GREEN: a carrier-controlled scalar-inexpressible benchmark
with a floor-reaching causal history oracle is established; learned
sequence-model testing is now askable. Forbidden: intelligence /
cognition / AGI / consciousness / brain fidelity / biological
neuroplasticity / model-capability / learned-model-advantage.

## 10. Why not post-hoc tuning
Only the oracle *specification* changes (toward the proven causal
optimum); env params and all gates are byte-identical to v8.2; the
analytic bound is derived before the run. v8.2 PARTIAL_RED stays the
preserved parent.
