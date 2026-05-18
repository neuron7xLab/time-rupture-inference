# Scalar-Inexpressibility Diagnostic (v8)

**VERDICT: RED**

## Hypothesis
A latent-context rupture environment makes a single scalar estimate insufficient: identical (short,short,long) windows precede opposite futures depending on hidden z.

## Oracle hierarchy (MAE, lower better)
- scalar_oracle = 0.7973
- history_oracle = 0.7970
- regime_oracle (floor) = 0.7926

## Metrics
- scalar_inexpressibility_gap = 0.0004 (pinned min 0.25)
- aliasing_rate = 0.0001
- same_observation_different_future_rate = 0.0
- history_disambiguation_gain = 0.0003
- context_recovery_score = 1.0000

## Checks
- [ ] gap_ge_min
- [x] history_beats_scalar
- [x] history_approaches_regime
- [x] aliasing_measured
- [ ] same_obs_diff_future_measured
- [x] deterministic_replay

## Is stronger-model testing now askable?
Stronger-model testing remains NOT askable: the environment does not prove scalar-inexpressibility (preserved RED).

Claim boundary: a validated task property, not a capability. No intelligence / cognition / AGI claim. No learned model was run.
```json
{
  "verdict": "RED",
  "scalar_oracle_mae": 0.7973388192413225,
  "history_oracle_mae": 0.7970187318103893,
  "regime_oracle_mae": 0.79258118880934,
  "scalar_inexpressibility_gap": 0.00040144468475500166,
  "gap_min_pinned": 0.25,
  "aliasing_rate": 5.555555555555556e-05,
  "history_disambiguation_gain": 0.000320087430933258,
  "context_recovery_score": 1.0,
  "same_observation_different_future_rate": 0.0,
  "checks": {
    "gap_ge_min": false,
    "history_beats_scalar": true,
    "history_approaches_regime": true,
    "aliasing_measured": true,
    "same_obs_diff_future_measured": false,
    "deterministic_replay": true
  },
  "grid": "30 seeds x 600 steps",
  "no_learned_model_run": true
}
```
