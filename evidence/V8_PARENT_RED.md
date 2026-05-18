# V8 PARENT RED — preserved (v8.1 lineage parent)

PR #5 was merged as a **preserved RED**. It is part of the lineage and
is NOT erased, edited, or tuned. v8.1 is a NEW pre-registration, not a
parameter edit of v8.

## v8 failure (verbatim facts)
- scalar_oracle = 0.7973, history_oracle = 0.7970, regime_oracle = 0.7926
- scalar_inexpressibility_gap = 0.0004 (pinned minimum 0.25)
- aliasing_rate ≈ 0.0001, same_observation_different_future_rate = 0.0
- Root cause: the (short,short,long) trigger at σ=1, short=μ−2,
  long=μ+2 has probability ≈ 0.0228³ ≈ 1.2e-5 per step → ≈0 triggers
  across the grid. The latent structure was formally correct but
  **statistically decorative** — history had almost nothing to
  disambiguate, so a scalar could not be defeated.
- Conclusion: stronger-model testing remained **not askable**.

## Why v8.1 is a new lineage, not a tweak
The defect is upstream of any model: the environment did not produce
ambiguous events at non-negligible frequency. v8.1 fixes this by
**deriving trigger frequency before the run** (closure-before-restart),
under a fresh pinned pre-registration, with the v8 RED kept as parent.
