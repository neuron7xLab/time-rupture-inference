# Doctoral critique → closure map (lineage v3)

Source: `Downloads/CTI_OS_RnD_Lab_Packet/docs/CTI_OS_RnD_Neurocognitive_Critique_Protocol_UA.md`.
Every actionable critique item is closed in the canonical project under a
new pre-registered lineage. v2-GREEN thresholds were **not relaxed**;
v3 only **adds** stricter conditions.

| Critique § | Defect / vulnerability | Closure in v3 | Where |
|---|---|---|---|
| 1.2.1 | No formal observation model | Documented generative + noise + forbidden surface | `prereg: observation_model` |
| 1.2.2 | Predictive ≠ causal world model | Explicitly NOT claimed; scoped | `release_gate` / `honest_failures` |
| 1.2.3, 4.5 | Underpowered (16 seeds, 1 shift) | **30 seeds × 3 shift magnitudes (incl. decrease)**; PASS must hold on every shift | `configs/experiment.yaml`, gate `pass_holds_on_every_shift` |
| 1.2.4, 5 | Leakage via order / autocorrelation | **Shuffled-order kill-control** + n_steps/T* non-exposure tests | `runner._run_on_series`, `test_leakage_hardening.py`, gate `shuffled_order_no_gain` |
| 1.2.5, 6 | "Neuroplasticity" rhetoric | **4 measured markers** (synaptic / homeostatic / neuromodulation / extinction) gated | `prereg: neuroplasticity_markers`, gate `np_marker_*` |
| 3 | Rhetorical overreach | Allowed/forbidden claim verbatim from §3 | `release_gate.md` |
| 7.2 | Reproducibility ledger incomplete | `tau0/tau1/T*_hidden_hash` (sha256+seed) — provenance, no leak | `env.hidden_provenance`, ledger |
| 5 (autocorr) | "Merely tracks autocorrelation" RED | Stationary negative control (battery rung 6) + shuffle control | tests + gate |

Not closed by design (declared, not hidden — separate falsification
lineages): non-stationary/multimodal shifts (v4), causal intervention
`do(A)->S(t+Δ)` world model, biological fidelity. These remain
hypotheses, not claims.
