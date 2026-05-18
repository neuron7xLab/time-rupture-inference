# v8.2 Trigger-Scoped / Carrier-Controlled Diagnostic

**VERDICT: PARTIAL_RED**

## Channel MAE (scalar / history / regime)
- total:   2.0338 / 1.7237 / 0.7926
- trigger: 7.9113 / 4.1899 / 0.8027
- carrier: 2.8933 / 2.8933 / 0.8091
- background: 0.9768 / 0.9768 / 0.7851

## Gap hierarchy
- trigger_context_gap_ratio = 0.4704 (min 0.35) -> True
- carrier_controlled_gap_ratio = 0.4650 (min 0.25) -> True
- whole_stream_gap_ratio = 0.1525 (min 0.1)
- history_to_regime_distance = 4.2199 (max 0.35) -> False
- structural_ok=True replay_ok=True

Stronger-model testing askable: no.

Claim boundary: a validated task-evaluation property only. No intelligence / cognition / AGI / model-advantage claim. No learned model was run.
```json
{
  "total_mae_scalar": 2.0337864351921597,
  "total_mae_history": 1.7236708363028448,
  "total_mae_regime": 0.7925811888093401,
  "trigger_context_mae_scalar": 7.91127553610117,
  "trigger_context_mae_history": 4.18988834942939,
  "trigger_context_mae_regime": 0.802669029343805,
  "carrier_mae_scalar": 2.893335099064547,
  "carrier_mae_history": 2.893335099064547,
  "carrier_mae_regime": 0.8090592746315491,
  "background_mae_scalar": 0.9767695486263881,
  "background_mae_history": 0.9767695486263881,
  "background_mae_regime": 0.7851409265592036,
  "trigger_context_gap": 3.7213871866717803,
  "trigger_context_gap_ratio": 0.4703902891120579,
  "carrier_controlled_gap": 3.721387186671782,
  "carrier_controlled_gap_ratio": 0.4650297827919057,
  "whole_stream_gap": 0.31011559888931495,
  "whole_stream_gap_ratio": 0.1524818897024525,
  "history_to_regime_distance": 4.219945203136456,
  "trigger_count": 1500,
  "aliasing_rate": 0.08333333333333333,
  "same_observation_different_future_rate": 1.0,
  "history_disambiguation_gain": 3.7213871866717803,
  "no_learned_model_run": true,
  "verdict": "PARTIAL_RED",
  "deterministic_replay_hash": "c0a9cbe5970236d4f90886a1dc9ce26226ec5ca68bb6c96773bb283a08412cf4",
  "structural_ok": true,
  "replay_ok": true
}
```
