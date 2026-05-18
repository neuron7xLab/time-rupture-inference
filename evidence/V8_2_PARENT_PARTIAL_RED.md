# V8.2 PARENT PARTIAL_RED — preserved (v8.3 lineage parent)

PR #7 (v8.2) merged as preserved PARTIAL_RED. Not erased, not tuned.
v8.3 is a NEW pre-registration; v8.2's pinned thresholds are REUSED
unchanged (only the history-oracle specification changes).

## v8.2 facts (verbatim)
- trigger_context_gap_ratio = 0.4704 (≥0.35) — signal real
- carrier_controlled_gap_ratio = 0.4650 (≥0.25) — carrier-robust
- history_to_regime_distance = 4.2199 (≫ pinned 0.35) — the *reference*
  history oracle ("reuse last observed sign") does NOT reach the noise
  floor on the trigger channel.
- Verdict: scalar-inexpressibility CONFIRMED & carrier-robust; benchmark
  still evaluation-fragile because the reference oracle is
  under-specified. Stronger-model testing NOT askable.

## v8.3 question
Is the v8.2 h2r failure (a) a fixable history-oracle mis-specification,
or (b) an information-theoretic floor: with one hidden context flip and
δ≫σ, *any causal* oracle must eat ≥1 unavoidable large error, so the
pinned h2r≤0.35 may be unattainable by construction? v8.3 implements a
correctly-specified oracle AND derives the analytic causal lower bound
on h2r BEFORE the run to discriminate (a) vs (b). No threshold edited.
