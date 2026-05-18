# Surviving Positive — Carrier-Robust Observable (arc closure)

**Status: GREEN. Pinned before the run; not tuned.**
Spec: `prereg/carrier_robust_observable.yaml`. Closes the sharpest open
cell of #27's boundary map.

## The 5-experiment arc

| # | lineage | verdict | what it established |
|---|---|---|---|
| 24 | predictive_simulation | PARTIAL | naive PH-on-error false-alarms 0.75; dissociation holds |
| 25 | calibrated_change_detector | PARTIAL | calibration cannot rescue it — root cause is the **observable** |
| 26 | windowed_change_detector | GREEN | stationary two-window contrast resolves it (Gaussian) |
| 27 | windowed_detector_ood | PARTIAL | replicates OOD; **defeated by a carrier confound** (fire=1.0, detect=0.0) |
| 28 | carrier_robust_observable | **GREEN** | wide median/MAD observable resolves the carrier cell |

Each falsifier was pinned before its run; no threshold edited after
results; every negative and positive preserved.

## Verdict (single pinned run)

| metric | value | threshold | result |
|---|---:|---|---|
| calib_lambda (report) | 0.940 | — | — |
| carrier_detect_rate | 0.917 | ≥ 0.50 | OK |
| null_family_false_alarm | 0.000 | ≤ 0.10 | OK |
| gaussian_detect_rate | 1.000 | ≥ 0.50 | OK |
| always_fake_blocked | 1.0 | ≥ 1.0 | OK |
| never_fake_blocked | 1.0 | ≥ 1.0 | OK |
| leakage | 0.0 | ≤ 0.0 | OK |

Battery: deterministic / finite / load-bearing / negative-control-fails
OK. Verdict: **GREEN**.

## Inverse argument

#27 did not merely fail on the carrier family — it *localised* a new
root cause distinct from #24/#25: the mean two-window contrast is
**confound-fragile** (a bounded additive carrier moves the windowed
*mean* as much as a regime step). The pre-registered fix was a
**robust statistic** (wide median / MAD), with window sizes chosen a
priori as "wide enough for a bounded low-frequency confound" — never
fitted to the carrier period (the detector never sees it). The
identical falsifier shape now passes the previously-failed cell
(`carrier_detect_rate 0.00 → 0.917`) and, as a consequence of the
wider robust window, also tightens the OOD false-alarm
(`0.167 → 0.000`) while the in-scope Gaussian positive still replicates
(1.0). The GREEN confirms #27's boundary diagnosis was correct — that
is the scientific content.

## What is and is not claimed

**Verified (survives its pinned falsifier):** on these synthetic
families, a Gaussian-null-calibrated wide median/MAD two-window
contrast detects the rupture under an additive bounded carrier confound
(0.917), holds the OOD null false-alarm bound (0.0), replicates the
in-scope Gaussian positive (1.0), and dominates both degenerate fakes.

**Not claimed:** nothing about brains, neurons, cognition,
consciousness, intelligence, AGI, a theory of time, or any private
theorem; no real-world validity; no generalization beyond these
synthetic families. Untested: contextual-aliased and multimodal
families remain out of scope (see #27 boundary map) — decision-gated,
not run.

## Reproduction

```
PYTHONPATH=src python -m ctios.carrier_robust_observable
```

Deterministic, offline, numpy-only. Sealed verdict:
`evidence/FALSIFY_carrier_robust_observable.json` (regenerated;
gitignored). Spec hash recorded in the verdict.
