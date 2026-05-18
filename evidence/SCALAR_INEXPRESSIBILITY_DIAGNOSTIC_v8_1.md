# v8.1 Scalar-Inexpressibility Diagnostic

**VERDICT: RED**

- scalar_oracle = 2.0338
- history_oracle = 1.7237
- regime_oracle (floor) = 0.7926
- scalar_inexpressibility_gap = 0.1525 (pinned min 0.25)
- aliasing_rate = 0.0833  observed_triggers = 1500
- same_observation_different_future_rate = 1.0
- history_disambiguation_gain = 0.3101
- context_recovery_score = 0.5547

## Checks
- [x] precheck_passed
- [x] observed_trigger_count_nonneg
- [x] same_obs_diff_future_gt_min
- [x] aliasing_gt_min
- [ ] gap_ge_min
- [x] history_beats_scalar
- [ ] history_approaches_regime
- [x] oracle_ordering_valid
- [x] deterministic_replay

v8.1 failed to establish scalar-inexpressibility; stronger-model testing remains not askable.

Claim boundary: a validated task property, not a capability. No intelligence / cognition / AGI / model-advantage claim. No learned model was run.
```json
{
  "verdict": "RED",
  "scalar_oracle_mae": 2.0337864351921597,
  "history_oracle_mae": 1.7236708363028448,
  "regime_oracle_mae": 0.7925811888093401,
  "scalar_inexpressibility_gap": 0.1524818897024525,
  "scalar_inexpressibility_gap_ratio": 0.1524818897024525,
  "gap_min_pinned": 0.25,
  "aliasing_rate": 0.08333333333333333,
  "expected_trigger_probability": 0.08333333333333333,
  "observed_trigger_count": 1500,
  "expected_trigger_count_total_grid": 1500,
  "same_observation_different_future_rate": 1.0,
  "history_disambiguation_gain": 0.31011559888931495,
  "context_recovery_score": 0.5546666666666666,
  "deterministic_replay_hash": "c0a9cbe5970236d4f90886a1dc9ce26226ec5ca68bb6c96773bb283a08412cf4",
  "oracle_ordering_valid": true,
  "checks": {
    "precheck_passed": true,
    "observed_trigger_count_nonneg": true,
    "same_obs_diff_future_gt_min": true,
    "aliasing_gt_min": true,
    "gap_ge_min": false,
    "history_beats_scalar": true,
    "history_approaches_regime": false,
    "oracle_ordering_valid": true,
    "deterministic_replay": true
  },
  "no_learned_model_run": true
}
```
