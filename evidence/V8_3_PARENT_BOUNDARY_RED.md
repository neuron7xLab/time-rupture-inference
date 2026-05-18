# V8.3 PARENT BOUNDARY_RED — preserved (v8.4 lineage parent)

PR #9 (v8.3) merged as preserved BOUNDARY_RED. Not erased, not tuned.
v8.4 is a NEW pre-registration; the h2r gate (0.35) is REUSED unchanged.

## v8.3 facts (verbatim, decisive)
- analytic `h2r_causal_min` = 0.5716 > pinned 0.35 → the gate was
  **information-theoretically unattainable by ANY causal oracle** under
  the v8.1/v8.2 env params (one hidden flip + cold prior at δ≫σ).
- tc=0.4704, cc=0.4650 → scalar-inexpressibility real & carrier-robust.
- Empirical correct-oracle h2r=4.22 ≫ analytic 0.57 → a *second* defect:
  the forced marker value (`short_thresh−1`=7) sat only 1σ from the
  categorization threshold (8) at σ=1, so trigger DETECTION failed on
  ≈22% of triggers (oracle then predicted the mean → ≈δ error).

## v8.4 corrective principle (all first-principles, proven pre-run)
1. **Separate the marker** ≥3σ from thresholds → detection reliability
   P(miss)≲0.1% → empirical converges to the analytic optimum.
2. **Warm-score** the trigger channel (exclude pre-first-trigger
   cold-prior step) — an evaluation artifact, not the science (mirrors
   the v1 warmup discipline).
3. **Derive T_min** so the single unavoidable post-flip error amortizes
   below the gate: with warm scoring + 1 hidden flip,
   `h2r_causal_min = (2δ−floor)/(T·floor)`. Pinned n_steps=1200,
   period=10 → T=120 → h2r_causal_min ≈ 0.159 ≤ 0.35 (proven BEFORE
   the run). The gate is unchanged; the env is sized to make the causal
   floor reachable.

v8.3 BOUNDARY_RED stays the preserved parent. No threshold edited.
