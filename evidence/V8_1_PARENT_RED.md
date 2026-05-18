# V8.1 PARENT RED — preserved (v8.2 lineage parent)

PR #6 (v8.1) was merged as a **preserved RED**. It is part of the
lineage, not erased, not metric-edited after the fact. v8.2 is a NEW
pre-registration.

## v8.1 facts (verbatim)
- Trigger-frequency defect of v8 FIXED: expected=observed=1500 triggers,
  aliasing_rate=0.0833, same_observation_different_future_rate=1.0.
- `history_oracle` (1.7237) materially beat `scalar_oracle` (2.0338) →
  scalar-inexpressibility is **real, not decorative**.
- Still RED: `scalar_inexpressibility_gap` = 0.1525 < pinned 0.25;
  `history_oracle` far from `regime_oracle` (0.7926).
- Root cause: whole-stream MAE is dominated by the deterministic carrier
  (short,short,long,mid×8) that the stationary-stream oracles do not
  model, **diluting** the trigger-specific advantage below threshold.

## Why v8.2 is a new lineage, not a tweak
The v8.1 RED may be an **evaluation-design artifact**, not absence of
signal. v8.2 pre-registers (before any run) a trigger-scoped and
carrier-controlled metric decomposition to test exactly that. v8.1 RED
remains the parent; thresholds are pinned before the run.
