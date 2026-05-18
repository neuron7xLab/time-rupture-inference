# v9 — Learned model vs validated v8.4 benchmark

**VERDICT: RED**

- warm-trigger MAE: learned=5.9183 scalar=7.9777 regime=0.7919
- learned_to_regime_distance = 6.4737 (gate ≤0.35) -> False
- learned_vs_scalar_gap_ratio = 0.2581 (>0) -> True
- analytic causal floor = 0.1588 (not-below = True)
- triggers=3600 structural=True replay=True

## Finding
RED — the learned model does NOT recover the structure on a PROVABLY solvable task: h2r=6.4737 (gate 0.35), learned_vs_scalar=0.2581, learned_trig=5.918 scalar_trig=7.978 regime_trig=0.792. A precise negative: discoverable ≠ discovered by this model. Preserved, not tuned.

Claim boundary: a preregistered, oracle-anchored recovery result only. No intelligence / cognition / AGI / general-capability claim.
```json
{
  "verdict": "RED",
  "learned_trigger_mae_warm": 5.918283952274109,
  "scalar_trigger_mae_warm": 7.977674918564434,
  "regime_trigger_mae_warm": 0.7918823669571184,
  "learned_to_regime_distance": 6.4736907894737765,
  "learned_vs_scalar_gap_ratio": 0.2581442572318938,
  "analytic_h2r_causal_min": 0.15877521830873326,
  "beats_scalar": true,
  "h2r_within_gate": false,
  "not_below_information_floor": true,
  "trigger_count": 3600,
  "structural_ok": true,
  "deterministic_replay_hash": "11716c87ca6ec1c46932bf3bdd1f1048d662abd8977c06f3ddc07accc5df28ff",
  "learned_model_run": true
}
```
