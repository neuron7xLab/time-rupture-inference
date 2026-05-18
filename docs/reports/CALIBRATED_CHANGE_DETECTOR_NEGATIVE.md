# Preserved Negative #2 — Calibrated Change Detector

**Status: PARTIAL (not GREEN). Pinned before the run; not nudged.**
Spec: `prereg/calibrated_change_detector.yaml`. Lineage parent: the
predictive-simulation PARTIAL (`docs/reports/PREDICTIVE_SIMULATION_NEGATIVE.md`).

## Verdict (single pinned run)

| metric | value | threshold | result |
|---|---:|---|---|
| calib_lambda (report) | 59.996 | — | — |
| eval_null_false_alarm | 0.167 | ≤ 0.10 | **FAIL** |
| detect_rate | 0.083 | ≥ 0.50 | **FAIL** |
| always_fake_blocked | 1.0 | ≥ 1.0 | OK |
| never_fake_blocked | 1.0 | ≥ 1.0 | OK |
| leakage | 0.0 | ≤ 0.0 | OK |

Battery: deterministic ✓ finite ✓ load-bearing ✓ negative-control-fails ✓
(the detect-everything fake is rejected by the false-alarm check —
the pinned kill test fires).

## Root-cause (why calibration cannot rescue this)

The obvious fix to Negative #1's 0.75 false-alarm was to calibrate λ to
a held-out null bound. It fails for a **structural** reason, not a
tuning one: the single re-converging scalar predictor's *own
cold-start / tracking transient on a NULL stream* produces a
Page-Hinkley peak (`calib_lambda ≈ 60`) that is **as large as or larger
than the post-rupture excursion**. Therefore no single λ can
simultaneously (a) bound disjoint-null false-alarm ≤ 0.10 and
(b) detect the rupture ≥ 0.50 — raising λ to kill false alarms also
kills detection (`detect_rate` collapses to 0.083).

## Manifestation → boundary escalation

Two surface-distinct mechanism failures (Negative #1 fixed-λ PH;
Negative #2 calibrated-λ PH) share one **root-convergent attribute**:
*the observable itself* — a single scalar's |one-step error| — does not
carry a change signal separable from its own convergence dynamics.
Per closure discipline, iteration STOPS at the manifestation layer
(detector tuning). The open question moves to the **boundary layer**:
the observable, not the threshold.

## What is verified vs falsified

**Verified (survives falsifier):** the falsifier is discriminative —
both degenerate fakes (detect-everything, detect-nothing) are rejected
by the pinned checks; the kill test works; calibration uses strictly
disjoint held-out seeds (no in-sample leakage).

**Falsified (the negative):** a calibrated PH detector on a single
re-converging scalar is not a valid change detector at the pinned
bounds — and the cause is the observable, so calibration is the wrong
layer to fix. Quantified, preserved, not nudged.

## Auto-proposed next experiment (decision-gated, NOT run)

`prereg/NEXT_calibrated_change_detector.yaml` (engine-emitted): tighten
survivors ×0.9, failed boundary = focus. The decision (not taken here)
is a boundary-layer change: a *different observable* (e.g. a windowed /
variance-normalised statistic, or a two-state residual model) — to be
pinned before any future run. No next experiment auto-runs.
