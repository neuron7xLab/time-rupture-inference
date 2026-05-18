# CTI-OS v8.3 — Task-Design Verdict

## Parent
v8.2 PARTIAL_RED preserved (evidence/V8_2_PARENT_PARTIAL_RED.md).

## Pre-run analytic causal bound
```json
{
  "triggers_per_seed": 50,
  "expected_forced_wrong": 1.5,
  "regime_trigger_floor": 0.7978845608028654,
  "history_trigger_mae_min": 1.2539480239787795,
  "h2r_causal_min": 0.5715907859114401,
  "attainable_at_0_35": false
}
```

## Verdict
**BOUNDARY_RED**

BOUNDARY_RED — the correctly-specified oracle sits at the analytic causal optimum, and that optimum (h2r_min=0.5716) EXCEEDS the pinned 0.35. One hidden flip + cold prior force unavoidable wrong-sign triggers; NO causal oracle can pass. The v8.2 PARTIAL_RED was NOT an oracle defect — it is an information-theoretic mis-pinning of the h2r gate vs the env (δ/σ/flip/trigger-count). Defect = benchmark parameterization.

## Next permitted step
BOUNDARY_RED/RED -> NEW v8.4 pre-registration that re-derives env δ/σ/flip-policy OR the h2r gate from first principles so a causal oracle CAN reach the floor. NOT a v8.3 edit. v8.2/v8.3 preserved.

## Claim boundary
No capability / cognition / AGI claim.
