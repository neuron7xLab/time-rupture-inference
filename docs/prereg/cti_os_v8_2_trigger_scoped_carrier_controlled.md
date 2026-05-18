# CTI-OS v8.2 — Trigger-scoped / carrier-controlled (pre-registration)

Pinned **before** the diagnostic. No learned model runs. Parent:
evidence/V8_1_PARENT_RED.md (PR #6 RED preserved).

## 1. Parent v8.1 failure
Trigger frequency fixed (1500 triggers); history beat scalar
(1.7237<2.0338) → real scalar-inexpressibility. But whole-stream MAE was
carrier-dominated → gap 0.1525 < 0.25, history far from regime.

## 2. Hypothesis
A trigger-scoped + carrier-controlled metric reveals a material history
advantage exactly on aliased trigger windows where scalar state is
insufficient.

## 3. Null hypothesis
Even trigger-scoped and carrier-controlled, history does not materially
beat scalar nor approach regime; stronger-model testing stays not
askable.

## 4. Metric definitions
For each oracle O, MAE on disjoint channels {trigger, carrier,
background} and total. trigger_context_gap = trig_mae(scalar) −
trig_mae(history); carrier_controlled_gap = carrier-aware
trig_mae(scalar) − carrier-aware trig_mae(history); whole_stream_gap =
total(scalar) − total(history). Ratios = gap / scalar side.

## 5–7. Windows
trigger = scheduled aliased step (slot%period==3); carrier = forced
marker steps (slot%period∈{0,1,2}); background = remaining filler.
Disjoint by construction. Masks emitted as artifacts.

## 8. Oracle hierarchy
scalar (obs + scalar/phase estimate, NO z/future/schedule), history
(sufficient past, NO z), regime (z; floor, not the claim).

## 9. Pinned thresholds
trigger_context_gap_ratio_min=0.35, carrier_controlled_gap_ratio_min=0.25,
whole_stream_gap_ratio_min=0.10, history_to_regime_distance_max=0.35,
trigger_count_min=300, aliasing_rate_min=0.05,
same_obs_diff_future_rate_min=0.05.

## 10. Verdicts
GREEN: structural ok ∧ tc_ratio≥0.35 ∧ cc_ratio≥0.25 ∧ h2r≤0.35 ∧
ordering valid ∧ deterministic ∧ no model. PARTIAL_RED: tc GREEN but
cc RED or history not near regime (signal exists, evaluation still
fragile). RED otherwise. RED/PARTIAL preserved, never tuned.

## 11. No-learned-model rule
No GRU/SSM/reservoir/transformer/MLP/policy learner in this lineage.

## 12. Claim boundary
Allowed if GREEN: a carrier-controlled scalar-inexpressible benchmark is
established; learned sequence-model testing is now askable. Forbidden:
intelligence / cognition / AGI / consciousness / brain fidelity /
biological neuroplasticity / model-capability / learned-model-advantage.

## 13. Reproduction
`PYTHONPATH=src python scripts/run_v8_2_trigger_scoped_diagnostic.py`

## 14. Why this is not post-hoc tuning
The decomposition targets a pre-stated nuisance variable (the carrier)
identified by the v8.1 RED *before* v8.2; thresholds are pinned here
before any v8.2 run; env parameters are unchanged from v8.1 (only the
evaluation is corrected). v8.1 RED remains the parent.
