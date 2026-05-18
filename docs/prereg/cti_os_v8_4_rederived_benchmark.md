# CTI-OS v8.4 — Re-derived benchmark (pre-registration)

Pinned **before** the diagnostic. No learned model. Parent:
evidence/V8_3_PARENT_BOUNDARY_RED.md. The h2r/tc/cc gates are REUSED
from v8.2/v8.3 **unchanged**; only the environment is re-derived.

## 1. Parent
v8.3 BOUNDARY_RED: pinned h2r≤0.35 was information-theoretically
unattainable (analytic causal min 0.572 > 0.35) AND empirical (4.22) ≫
analytic (0.57) due to unreliable trigger detection (forced marker only
1σ from threshold at σ=1).

## 2. Hypothesis
An env re-derived so that (a) the marker is ≥3σ clear of thresholds
(reliable detection) and (b) `n_steps/period` are sized so the single
unavoidable post-flip error amortizes below the gate, makes the
correctly-specified causal oracle reach the trigger floor
(`h2r ≤ 0.35`) AND empirical ≈ analytic. Then learned sequence-model
testing is, for the first time, scientifically askable.

## 3. Null hypothesis
Even with reliable detection and a derived-attainable floor, the
correctly-specified causal oracle does not reach h2r ≤ 0.35, or
empirical ≫ analytic (a further unmodelled defect). Stronger-model
testing stays not askable.

## 4. Pre-run proof (the decisive derivation, computed before any run)
Warm-scored trigger channel (cold prior excluded) + 1 hidden flip ⇒
forced unavoidable wrong = 1. Floor = σ·√(2/π) = 0.7979 (σ=1).
`h2r_causal_min = (2δ − floor)/(T·floor)`. With δ=8, pinned
n_steps=1200, period=10 ⇒ T = 120 ⇒
**h2r_causal_min = 0.1588 ≤ 0.35** (proven BEFORE the run; emitted as
`artifacts/v8_4/causal_bound.json`). The gate is unchanged; the env is
sized so the causal floor is reachable.

## 5. Detection-reliability derivation
Forced short = μ−5 = 5, threshold = 8 ⇒ 3σ margin ⇒
P(misclassify a marker step) = P(N(5,1) > 8) ≈ 1.3e-3; per 3-step
window ≈ 4e-3. Detection is effectively deterministic ⇒ empirical
trigger MAE converges to the analytic causal optimum.

## 6. Pinned parameters
configs/v8_4_rederived_env.yaml: μ=10, σ=1, δ=8, n_steps=1200,
period=10, seed_count=30, marker_sep=5, warm_scored=true,
hidden_flips=1. Gates unchanged: h2r≤0.35, tc≥0.35, cc≥0.25,
trigger_count≥300, aliasing≥0.05, sodf≥0.05.

## 7. Verdicts
- GREEN: structural ∧ tc≥0.35 ∧ cc≥0.25 ∧ h2r≤0.35 ∧ ordering ∧
  deterministic ∧ empirical within 25% of analytic h2r_causal_min ∧ no
  model. ⇒ benchmark valid; learned-model testing askable.
- RED: any gate fails OR empirical ≫ analytic (further defect). RED
  preserved, not tuned. (No BOUNDARY_RED is possible here: the floor is
  proven ≤ gate before the run.)

## 8. No-learned-model rule
No GRU/SSM/reservoir/transformer/MLP/policy learner.

## 9. Claim boundary
Allowed if GREEN: "a carrier-controlled scalar-inexpressible benchmark
whose causal floor is reachable is established; learned sequence-model
testing is now scientifically askable." Forbidden: intelligence /
cognition / AGI / consciousness / brain fidelity / biological
neuroplasticity / model-capability / learned-model-advantage.

## 10. Why not post-hoc tuning
Gates are byte-identical to v8.2/v8.3. The env changes are each a
*derivation* (detection reliability from σ-margin; T from the amortized
forced-error formula) proven analytically **before** the run, not
selected from results. v8.3 BOUNDARY_RED stays the preserved parent.
