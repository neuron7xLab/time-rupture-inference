# CTI-OS v8.1 — Trigger-frequency-corrected pre-registration

Pinned **before** the diagnostic. No learned model is run in this
lineage. Parent: evidence/V8_PARENT_RED.md (PR #5 RED preserved).

## 1. Hypothesis
A trigger-frequency-corrected latent-context rupture environment
(Construction B: deterministic alias schedule) creates non-negligible
scalar-inexpressible events such that `history_oracle` materially beats
`scalar_oracle` while `regime_oracle` stays the upper bound.

## 2. Null hypothesis
The environment does not create measurable scalar-inexpressibility;
`scalar_oracle ≈ history_oracle`; stronger-model testing stays not
askable.

## 3. Parent failure
v8 was formally correct but statistically decorative: the
(short,short,long) trigger at σ=1, μ±2 had P ≈ 1.2e-5/step → ≈0
triggers → history had nothing to disambiguate (gap 0.0004 ≪ 0.25).

## 4. Corrective principle
Trigger frequency is **derived (closed-form, exact) before** the oracle
diagnostic. Construction B schedules the aliased window deterministically
every `period` steps; the trigger count is exact, not stochastic. If the
derived frequency fails the pinned minimums the diagnostic does not run
(RED_PRECHECK).

## 5. Pinned parameters
configs/v8_1_scalar_inexpressible_env.yaml: μ=10, σ=1, δ=8, n=600,
period=12, seed_count=30, short=8, long=12, gap_min=0.25,
history_close_frac=0.15, min_trigger_count_total=300,
min_aliasing_rate=0.05, min_same_obs_diff_future_rate=0.05. Frozen
before any run; never edited after results.

## 6. No-learned-model rule
No GRU / SSM / reservoir / transformer / MLP / trainable model runs in
this PR. Oracle hierarchy only.

## 7. Verdict isolation
The scientific RED/GREEN verdict lives in the diagnostic report
(research lineage), never in pytest. pytest asserts contracts and
invariants only; a legitimate RED must keep CI green.

## 8. GREEN conditions
precheck passes · observed triggers ≥ 300 · same-obs-diff-future > 0.05
· aliasing > 0.05 · gap ≥ 0.25 · history beats scalar · history within
15% of regime · oracle ordering valid · deterministic replay stable ·
no model run · all artifacts emitted · no post-hoc threshold change.

## 9. RED conditions (preserve, stop)
precheck fails · negligible triggers · sodf == 0 · scalar ≈ history ·
history adds nothing · ordering invalid · post-hoc tuning · artifact
missing · any model run · pytest encoding the verdict.

## 10. Claim boundary
Allowed if GREEN: "the v8.1 environment exhibits measurable
scalar-inexpressibility under preregistered oracle diagnostics, making
learned sequence-model testing scientifically askable." Forbidden:
intelligence / cognition / AGI / consciousness / brain fidelity /
biological neuroplasticity / model-capability / learned-model-advantage.
