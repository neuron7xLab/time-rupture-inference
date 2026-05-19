# Arc Closure — Portfolio Falsifier (sealed PARTIAL)

**Status: PARTIAL. Pinned before the run; not tuned.**
Spec: `prereg/portfolio_falsifier.yaml`. Consolidates lineages
#24–#28 into one sealed portfolio verdict.

## The full arc

| # | lineage | verdict |
|---|---|---|
| 24 | predictive_simulation | PARTIAL |
| 25 | calibrated_change_detector | PARTIAL |
| 26 | windowed_change_detector | GREEN |
| 27 | windowed_detector_ood | PARTIAL |
| 28 | carrier_robust_observable | GREEN |
| 29 | portfolio_falsifier | **PARTIAL (this)** |

Every falsifier pinned before its run; no threshold edited after
results; every negative and positive preserved under `docs/reports/`.

## Consolidated verdict (one run, 7 families)

| gated metric | value | threshold | result |
|---|---:|---|---|
| gaussian_detect_rate | 1.000 | ≥ 0.50 | OK |
| heavytail_detect_rate | 1.000 | ≥ 0.50 | OK |
| carrier_detect_rate | 0.917 | ≥ 0.50 | OK |
| null_false_alarm | 0.000 | ≤ 0.10 | OK |
| multimodal_false_alarm | 1.000 | ≤ 0.10 | **FAIL** |
| always_fake_blocked | 1.0 | ≥ 1.0 | OK |
| never_fake_blocked | 1.0 | ≥ 1.0 | OK |
| leakage | 0.0 | ≤ 0.0 | OK |

Battery: deterministic / finite / load-bearing / negative-control-fails
OK. Verdict: **PARTIAL**.

Report-only (no single changepoint — not gatable honestly):
multi_regime_rupture, contextual_rupture (fire mapped only;
`evidence/PORTFOLIO_FALSIFIER_MAP.json`).

## The single characterized residual

The #28 carrier-robust detector is GREEN on **every rupture family**
(Gaussian, heavy-tail, carrier-confounded) and on the plain null. It
has exactly **one** false-positive boundary:
`multimodal_false_alarm = 1.0`. This is structural, not a tuning miss:
a location-contrast statistic (median difference of two windows) cannot
distinguish a *stationary bimodal mixture* from a level shift — the
random hi/lo mix ratio differs between windows, so the contrast spikes
exactly as it would for a real change. Raising λ to suppress it also
suppresses true detection (the same false-alarm↔power trade-off class
sealed in Negative #2, now characterized at portfolio scope). It is
**not** "fixed" by editing a threshold; it requires a distributional
(not location) observable — a decision-gated next lineage, proposed,
not run.

## What is and is not claimed

**Verified (survives its pinned falsifier):** on these synthetic
families, the carrier-robust detector detects every single-changepoint
rupture family and does not false-alarm on the plain no-rupture family,
while dominating both degenerate fakes — in one sealed consolidated
verdict.

**Characterized boundary (the honest negative):** a single residual
false-positive on bimodal stationary data, with a stated structural
cause. **Not claimed:** brains, cognition, consciousness, AGI, theory
of time, private theorem, real-world validity, or generalization beyond
these synthetic families.

## Reproduction

```
PYTHONPATH=src python -m ctios.portfolio_falsifier
```

Deterministic, offline. Portfolio map sealed at
`evidence/PORTFOLIO_FALSIFIER_MAP.json` (regenerated; gitignored).
