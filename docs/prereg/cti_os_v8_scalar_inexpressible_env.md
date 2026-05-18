# CTI-OS v8 — Scalar-inexpressible environment (pre-registration)

Pinned **before** the diagnostic run. No learned model is trained in
this lineage: PR scope is environment validity + oracle headroom only.

## Formal scalar-inexpressibility
An environment is *scalar-inexpressible* iff there exist two histories
H₁, H₂ such that:
- the current observation O(t) is identical or statistically aliased,
- any single online scalar estimate m(t) is indistinguishable,
- yet the optimal prediction for S(t+Δ) differs.

Hence `P(future | current scalar)` stays ambiguous while
`P(future | history / latent state)` is disambiguated.

## Environment: `latent_context_temporal_rupture`
- Intervals ~ Normal(μ, σ). A hidden binary context `z ∈ {A, B}`.
- A **trigger** = the categorized last-3 window equals
  (short, short, long) (thresholds fixed vs μ). Outside triggers both
  contexts emit the *same* distribution → locally aliased.
- At the step **after** a trigger the interval is shifted by
  `sign(z)·δ` (z=A → +δ, z=B → −δ). Same recent observation window,
  opposite correct future, depending only on hidden z.
- `z` is unobserved and flips once at a hidden step `t_z`; after a flip
  the correct sign reverses → history must be *re-inferred*, short
  windows cannot.

## Pinned parameters (pre-run, not tuned to pass)
μ=10.0, σ=1.0, δ=8.0, n_steps=600, hidden flip at t_z=n//2,
short<μ−2, long>μ+2, seeds=30. δ≫σ on first principles: the aliased
prediction error at a trigger is ≈ δ, far above the σ floor — so a real
scalar-inexpressibility gap must appear if the construction is sound.

## Oracle hierarchy
- `scalar_oracle` — best scalar-only predictor (running regime mean; no
  trigger anticipation: at a trigger it must hedge to the mean).
- `history_oracle` — infers the current sign from the most recent
  observed post-trigger jump (no z access); correct except a one-trigger
  transient after a hidden z-flip.
- `regime_oracle` — upper bound: knows z, residual = σ noise only.

## Metrics
scalar_oracle_mae · history_oracle_mae · regime_oracle_mae ·
scalar_inexpressibility_gap = (scalar_mae − history_mae)/scalar_mae ·
aliasing_rate · history_disambiguation_gain · context_recovery_score ·
same_observation_different_future_rate.

## GREEN (environment is valid for later stronger-model work)
1. scalar_inexpressibility_gap ≥ 0.25
2. history_oracle materially beats scalar_oracle
3. history_oracle approaches regime_oracle (within ~15%)
4. aliasing_rate > 0 and measured
5. same_observation_different_future_rate > 0 and measured
6. deterministic replay stable
7. all artifacts emitted; no learned model run

## RED (environment complexity is decorative — preserve, stop)
scalar≈history, no aliasing, history adds nothing, heuristic still
near-oracle, artifacts missing, or any threshold changed after results.

## Claim boundary
This validates a *task property*, not a capability. No intelligence /
cognition / AGI claim. RED is preserved as a delivered artifact.
