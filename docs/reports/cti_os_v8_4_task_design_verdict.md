# CTI-OS v8.4 — Task-Design Verdict

## Parent
v8.3 BOUNDARY_RED preserved.

## Pre-run analytic causal bound (proven ≤ gate)
```json
{
  "triggers_per_seed": 120,
  "expected_forced_wrong": 1.0,
  "regime_trigger_floor": 0.7978845608028654,
  "history_trigger_mae_min": 0.9245688561295081,
  "h2r_causal_min": 0.15877521830873326,
  "attainable_at_0_35": true
}
```

## Verdict
**GREEN**

GREEN — env re-derived so the causal floor is reachable (analytic h2r_min=0.1588 ≤ 0.35), the correctly-specified causal oracle attains it (h2r=0.1851) at the analytic optimum, with the scalar-inexpressible signal still real & carrier-robust (tc=0.8824, cc=0.8819). Learned sequence-model testing is, for the first time, scientifically askable.

## Next permitted step
GREEN -> the benchmark is valid; a future PR may test learned sequence models (the question is finally well-posed).

## Claim boundary
No capability / cognition / AGI claim.
