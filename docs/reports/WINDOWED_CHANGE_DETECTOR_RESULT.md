# Surviving Positive — Windowed Change Detector (boundary confirmed)

**Status: GREEN. Pinned before the run; not tuned.**
Spec: `prereg/windowed_change_detector.yaml`. Lineage:
Negative #1 (`PREDICTIVE_SIMULATION_NEGATIVE.md`) →
Negative #2 (`CALIBRATED_CHANGE_DETECTOR_NEGATIVE.md`) → this.

## Verdict (single pinned run)

| metric | value | threshold | result |
|---|---:|---|---|
| calib_lambda (report) | 0.901 | — | — |
| eval_null_false_alarm | 0.083 | ≤ 0.10 | OK |
| detect_rate | 1.000 | ≥ 0.50 | OK |
| always_fake_blocked | 1.0 | ≥ 1.0 | OK |
| never_fake_blocked | 1.0 | ≥ 1.0 | OK |
| leakage | 0.0 | ≤ 0.0 | OK |

Battery: deterministic ✓ finite ✓ thresholds-load-bearing ✓
negative-control-fails ✓. Verdict: **GREEN**.

## Inverse argument (why this GREEN is informative, not lucky)

Negatives #1/#2 did not merely fail — they *localised* the failure:
two surface-distinct mechanisms (fixed-λ, calibrated-λ Page-Hinkley on
a re-converging scalar's |error|) shared one root cause — the
**observable** carried a cold-start transient (`λ≈60` on null) that no
threshold could separate from the rupture. The pre-registered
prediction was: change the observable, not the threshold, and the same
falsifier should pass.

This experiment changed only the observable — a **stationary
two-window standardized contrast on the raw observation** (no
estimator, no re-convergence, hence no cold-start). The identical
falsifier shape now passes: `calib_lambda` drops from ≈60 to ≈0.90 (a
sane stationary scale), disjoint-null false-alarm holds at 0.083 ≤ α,
and detection is 1.0. The GREEN confirms the boundary diagnosis from
the two REDs was correct — that is the scientific content.

## What is and is not claimed

**Verified (survives its pinned falsifier):** on this synthetic
hidden-rupture family, a held-out-null-calibrated stationary two-window
contrast detects the rupture (rate 1.0) while holding false-alarm ≤ α
on disjoint null, and strictly dominates both degenerate fakes
(detect-everything rejected by the false-alarm check; detect-nothing by
the detection check). Calibration uses disjoint held-out seeds (no
in-sample leakage); structural leakage = 0.

**Not claimed:** nothing about brains, neurons, cognition,
consciousness, intelligence, AGI, a theory of time, or any private
theorem; no real-world validity; no superiority beyond this synthetic
family. Generality beyond it is untested (open).

## Reproduction

```
PYTHONPATH=src python -m ctios.windowed_change_detector
```

Deterministic, offline, numpy-only. Sealed verdict:
`evidence/FALSIFY_windowed_change_detector.json` (regenerated;
gitignored). Spec hash recorded in the verdict.

## Residual risks (open, stated)

Single synthetic rupture family; fixed window sizes (w=20, W=80) not
swept; one rupture magnitude; transfer to multi-regime / heavy-tail /
carrier-confounded families (see `ctios.benchmark_families`) untested
and is the natural decision-gated next experiment — proposed, not run.
