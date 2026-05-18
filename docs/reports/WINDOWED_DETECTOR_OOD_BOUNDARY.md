# Boundary Map — Windowed Detector OOD Transfer (sealed PARTIAL)

**Status: PARTIAL. Pinned before the run; not tuned.**
Spec: `prereg/windowed_detector_ood_transfer.yaml`. Parent: the #26
GREEN (`WINDOWED_CHANGE_DETECTOR_RESULT.md`).

## Gated verdict (the falsifiable core)

| metric | value | threshold | result |
|---|---:|---|---|
| calib_lambda (report) | 0.901 | — | — |
| gaussian_detect_rate | 1.000 | ≥ 0.50 | **OK** |
| null_family_false_alarm | 0.167 | ≤ 0.10 | **FAIL** |
| always_fake_blocked | 1.0 | ≥ 1.0 | OK |
| never_fake_blocked | 1.0 | ≥ 1.0 | OK |
| leakage | 0.0 | ≤ 0.0 | OK |
| boundary_map_emitted | 1.0 | ≥ 1.0 | OK |

Battery: deterministic / finite / load-bearing / negative-control-fails
OK. Verdict: **PARTIAL**.

## What replicates, what does not

**Replicates (verified):** the #26 in-scope positive holds under the
independent 7-family portfolio harness — `gaussian_detect_rate = 1.0`.
This is real: a different harness, fresh seeds, same result.

**Honest negative:** the empirical-quantile calibration gives **no
finite-sample distribution-free false-alarm guarantee**. λ is the 0.90
quantile over 16 calibration null streams; on 12 fresh OOD null draws,
2 exceed → 0.167 > α. This is a property of quantile calibration, not a
tuning miss — it is not "fixed" by editing λ (that would be tuning to
green and would not change the finite-sample nature).

## Report-only boundary map (NOT gated — measured, not claimed)

| family | fire | detect | reading |
|---|---:|---:|---|
| single_rupture_gaussian | 1.00 | 1.00 | in-scope — holds |
| heavy_tail_rupture | 1.00 | 1.00 | transfers: the mean shift dominates Student-t tails |
| multi_regime_rupture | 1.00 | 1.00 | catches the first rupture (only one needed) |
| carrier_confounded_rupture | 1.00 | **0.00** | **fooled**: fires on the carrier, never in the rupture window — right alarm, wrong reason |
| contextual_rupture | 0.08 | 0.08 | out of scope (aliased context, no clean mean shift) |
| multimodal_interval | 0.17 | 0.17 | ~null level (no rupture, bimodal) |
| null_no_rupture | 0.17 | 0.17 | the finite-sample calibration gap |

## Inference (bounded, no generalization claim)

The Gaussian-null-calibrated windowed detector **replicates in-scope
and transfers to large-mean-shift ruptures even under heavy tails and
multi-regime**, but (1) its false-alarm bound is finite-sample
approximate, and (2) it is **defeated by a carrier confound** — it
fires confidently for the wrong reason. No generalization is claimed;
this is a measured boundary. The carrier-confound failure is the most
informative cell: a confident detector that is right about *when* but
wrong about *why* is exactly the failure class the apparatus exists to
surface.

## Reproduction

```
PYTHONPATH=src python -m ctios.windowed_detector_ood
```

Deterministic, offline. Boundary map sealed at
`evidence/WINDOWED_OOD_BOUNDARY_MAP.json` (regenerated; gitignored).

## Decision-gated next experiment (proposed, NOT run)

The carrier-confound cell (`detect=0.00` with `fire=1.00`) is the
sharpest open boundary: a contrast that is carrier-robust (e.g.
detrended or rank-based observable) — to be pinned before any run.
Closure-before-restart: this PARTIAL is sealed first.
