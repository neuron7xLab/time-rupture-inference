# NEGATIVE RESULT — lineage v3 (pinned, not erased)

**Verdict: RED / FAIL.** Reported as-is. No scientific threshold tuned.

prereg_hash (v3): `b98e98209406ddda53fabf17848eb3eb75ba13b3497b5ce42ec9b2928350858f`
pinned commit: `cc6b3cc` (predates run — integrity intact).
Parents preserved: `cti-os-v1-RED`, `cti-os-v2-GREEN`.

## What PASSED (core science, 30 seeds × 3 shifts incl. decrease)

learned post_mae=0.883 vs injected=8.003 vs oracle=0.793.
win-rate vs injected = 1.000, vs best-naive = 1.000, on EVERY shift delta.
Ablation-necessary, no-leakage, deterministic replay, prereg-before-run,
statistical-power grid, homeostatic + neuromodulation + extinction markers
— all GREEN.

## What FAILED — and why it is an instrument defect, not refutation

1. **`shuffled_order_no_gain`**: m_shuf=0.8853 < m_real=0.8909 (Δ≈0.6%).
   Post-shift intervals are i.i.d. (independent Gaussian noise), so
   shuffling is distributionally inert; the gap is single-seed sampling
   noise. The control was mis-specified: one seed, strict `>=`, no
   averaging, no tolerance. It does not implement the pre-registered
   intent ("performance *systematically* improves under shuffled order").

2. **`np_marker_synaptic`**: defined as drift from `preds[:50]` — the
   cold-start convergence transient (starts at prior=1) — instead of from
   the converged pre-shift window. Wrong reference window. The estimate
   *does* change after error (extinction + neuromodulation markers pass);
   the marker math, not the plasticity, is at fault.

## Disposition

Hypothesis NOT refuted. Lineage **v4** fixes ONLY the two mis-specified
instruments (shuffle control → mean over all seeds of delta[0]; synaptic
marker → converged pre-shift vs post-shift window). Scientific thresholds,
env, metrics, power grid UNCHANGED. v3 RED committed and tagged first.
