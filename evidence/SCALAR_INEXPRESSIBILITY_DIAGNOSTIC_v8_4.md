# v8.4 — Re-derived benchmark diagnostic

**VERDICT: GREEN**

- analytic h2r_causal_min = 0.1588 (attainable@0.35=True, proven pre-run)
- empirical h2r (warm) = 0.1851 (gate ≤0.35) -> True
- empirical_near_analytic = True
- trigger_context_gap_ratio = 0.8824 (≥0.35) -> True
- carrier_controlled_gap_ratio = 0.8819 (≥0.25) -> True
- warm trigger MAE: scalar=7.978 history=0.938 regime=0.792  triggers=3600

## Finding
GREEN — env re-derived so the causal floor is reachable (analytic h2r_min=0.1588 ≤ 0.35), the correctly-specified causal oracle attains it (h2r=0.1851) at the analytic optimum, with the scalar-inexpressible signal still real & carrier-robust (tc=0.8824, cc=0.8819). Learned sequence-model testing is, for the first time, scientifically askable.

Claim boundary: validated task-design property only. No intelligence / cognition / AGI / model-advantage claim. No learned model was run.
```json
{
  "verdict": "GREEN",
  "trigger_context_gap_ratio": 0.8823639283213114,
  "carrier_controlled_gap_ratio": 0.8818701858247437,
  "history_to_regime_distance": 0.18510321445298838,
  "h2r_causal_min_analytic": 0.15877521830873326,
  "analytic_attainable_at_0_35": true,
  "empirical_near_analytic": true,
  "h_trigger_mae_warm": 0.938462338549522,
  "r_trigger_mae_warm": 0.7918823669571184,
  "s_trigger_mae_warm": 7.977674918564434,
  "trigger_count": 3600,
  "structural_ok": true,
  "deterministic_replay_hash": "335c8da0699277a907e916efbd489b718ae527efff3a84267c932ff5c86f2dd1",
  "no_learned_model_run": true
}
```
