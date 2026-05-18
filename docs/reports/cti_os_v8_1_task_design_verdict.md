# CTI-OS v8.1 — Task-Design Verdict

## 1. Parent v8 RED
v8 RED preserved (evidence/V8_PARENT_RED.md): rare trigger (~1.2e-5/step) made aliasing decorative, gap 0.0004.

## 2. v8.1 preregistered correction
Construction B: deterministic alias schedule (period 12), frequency derived BEFORE the run.

## 3. Trigger-frequency derivation
```json
{
  "expected_trigger_probability": 0.08333333333333333,
  "expected_trigger_count_per_seed": 50,
  "expected_trigger_count_total_grid": 1500,
  "expected_same_observation_different_future_rate": 1.0,
  "expected_aliasing_rate": 0.08333333333333333,
  "minimum_required_trigger_count": 300,
  "frequency_precheck_passed": true
}
```

## 4. Oracle hierarchy
scalar=2.0338  history=1.7237  regime=0.7926

## 5. Metrics table
| metric | value |
|---|---|
| scalar_inexpressibility_gap | 0.1525 (min 0.25) |
| aliasing_rate | 0.0833 |
| same_obs_diff_future_rate | 1.0 |
| observed_trigger_count | 1500 |
| context_recovery_score | 0.5547 |

## 6. Verdict
**RED**

## 7. Stronger-model testing
v8.1 failed to establish scalar-inexpressibility; stronger-model testing remains not askable.

## 8. Reproduction
```
PYTHONPATH=src python scripts/derive_v8_1_trigger_frequency.py
PYTHONPATH=src python scripts/run_v8_1_scalar_inexpressibility_diagnostic.py
```

## 9. Claim boundary
Validated task property only. No intelligence / cognition / AGI / model-advantage claim.

## 10. Next allowed step
RED -> preserve; do NOT train models; diagnose the construction before any further lineage.
