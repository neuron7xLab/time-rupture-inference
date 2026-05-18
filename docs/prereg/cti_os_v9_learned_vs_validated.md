# CTI-OS v9 — Learned model vs the validated v8.4 benchmark (pre-reg)

Pinned **before** the run. Parent: evidence/V8_4_PARENT_GREEN.md. v8.4
env + gates (h2r≤0.35) REUSED unchanged. This lineage **does** train a
learned model — that is now scientifically well-posed (v8.4 proved the
task rewards latent state a scalar provably cannot represent).

## 1. Hypothesis
A small online-learned recurrent sequence model (fixed nonlinear
recurrent feature map + online-RLS readout — weights learned from data,
no z / schedule / trigger-label / future access) recovers the latent
context from observations and reaches the trigger-channel causal floor
(`h2r ≤ 0.35`), materially beating the scalar oracle.

## 2. Null hypothesis
The learned model does NOT reach h2r ≤ 0.35, or does not beat the
scalar oracle on the trigger channel — i.e. the scalar-inexpressible
structure is discoverable by a correctly-specified oracle but NOT
recovered by this learned model from data. Preserved RED.

## 3. Model (frozen spec, deterministic, no leakage)
`EchoStateLearner(dim, seed, leak, ridge)`: seeded fixed random
recurrent weights; leaky-tanh state driven by the observed interval
only; readout fit ONLINE by recursive least squares. It receives
exactly the observation stream — no z, no schedule, no trigger labels,
no future. Genuinely learned (readout learned from data), not a
hand-coded sign rule.

## 4. Pinned thresholds (reused from v8.4, unchanged)
history/learned_to_regime_distance_max = 0.35 ; learned must beat scalar
oracle on the warm trigger channel (gap_ratio > 0) ; structural gates:
trigger_count ≥ 300, aliasing ≥ 0.05, sodf ≥ 0.05 ; deterministic
replay stable. Analytic causal floor (v8.4) = 0.1588 emitted for
reference (a learner cannot beat it).

## 5. Verdicts
- GREEN: structural ∧ deterministic ∧ learned warm-trigger h2r ≤ 0.35 ∧
  learned beats scalar oracle on the warm trigger channel ∧ learned ≥
  analytic floor (sanity: not below the information limit). ⇒ a learned
  sequence model recovers scalar-inexpressible temporal structure under
  preregistered oracle-anchored diagnostics.
- RED: any of the above fails. Preserved, not tuned. A learner that
  fails on a *provably solvable* task is itself a precise, valuable
  negative.

## 6. Claim boundary
Allowed if GREEN: "a small online-learned recurrent model recovers the
latent-context scalar-inexpressible structure of the v8.4 benchmark,
reaching the causal floor under preregistered diagnostics." Forbidden:
intelligence / cognition / AGI / consciousness / brain fidelity /
biological neuroplasticity / general capability / understanding.

## 7. Verdict isolation & no tuning
Verdict lives in the diagnostic (research lineage), never a CI gate; a
legitimate RED keeps `main` green. No threshold/env edited after
results. v8.4 GREEN stays the preserved parent.
