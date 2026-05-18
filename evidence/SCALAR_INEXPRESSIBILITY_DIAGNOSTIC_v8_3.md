# v8.3 — Correctly-specified history oracle vs causal bound

**VERDICT: BOUNDARY_RED**

- trigger_context_gap_ratio = 0.4704 (≥0.35) -> True
- carrier_controlled_gap_ratio = 0.4650 (≥0.25) -> True
- history_to_regime_distance = 4.2199 (≤0.35) -> False
- analytic h2r_causal_min = 0.5716 (attainable@0.35=False)
- empirical_at_causal_bound = True
- h_trig=4.190 r_trig=0.803 s_trig=7.911 triggers=1500

## Finding
BOUNDARY_RED — the correctly-specified oracle sits at the analytic causal optimum, and that optimum (h2r_min=0.5716) EXCEEDS the pinned 0.35. One hidden flip + cold prior force unavoidable wrong-sign triggers; NO causal oracle can pass. The v8.2 PARTIAL_RED was NOT an oracle defect — it is an information-theoretic mis-pinning of the h2r gate vs the env (δ/σ/flip/trigger-count). Defect = benchmark parameterization.

Claim boundary: validated task-design/identifiability property only. No intelligence / cognition / AGI / model-advantage claim. No learned model was run.
```json
{
  "verdict": "BOUNDARY_RED",
  "trigger_context_gap_ratio": 0.4703902891120579,
  "carrier_controlled_gap_ratio": 0.4650297827919057,
  "history_to_regime_distance": 4.219945203136456,
  "h2r_causal_min_analytic": 0.5715907859114401,
  "analytic_attainable_at_0_35": false,
  "empirical_at_causal_bound": true,
  "trigger_count": 1500,
  "h_trigger_mae": 4.18988834942939,
  "r_trigger_mae": 0.802669029343805,
  "s_trigger_mae": 7.91127553610117,
  "structural_ok": true,
  "deterministic_replay_hash": "c0a9cbe5970236d4f90886a1dc9ce26226ec5ca68bb6c96773bb283a08412cf4",
  "no_learned_model_run": true
}
```
