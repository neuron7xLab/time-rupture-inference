# The Change-Detection Arc — one inverse argument

Six pre-registered experiments, one logically-closed line. Each
falsifier was pinned before its run; no threshold was edited after a
result; every verdict — RED, PARTIAL, GREEN — is sealed and preserved.
`PYTHONPATH=src python -m ctios.change_detection_arc` runs the whole
thing in one command.

## Motivation (stated, never claimed)

A predictive system does not read a clock; it holds a model of what
comes next and is moved only by its **own prediction error**. The
honest engineering question is narrow and falsifiable: *can a system
infer that a hidden regime changed, from its own error alone, without
being told?* Everything below is that question, pinned. No biological,
cognition, AGI, consciousness, or theory-of-time claim is made or
implied — the framing is motivation; the artifacts are the only
evidence.

## The arc

| # | lineage | verdict | what it established |
|---|---|---|---|
| 24 | predictive_simulation | RED (PARTIAL) | error alone false-alarms 0.75; the simulation⊳imitation *dissociation* is real, the detector is not |
| 25 | calibrated_change_detector | RED (PARTIAL) | calibration cannot rescue it — the root cause is the **observable**, not the threshold |
| 26 | windowed_change_detector | **GREEN** | a stationary two-window contrast resolves it (Gaussian) — confirms #25's diagnosis |
| 27 | windowed_detector_ood | RED (PARTIAL) | replicates OOD, but a carrier confound defeats it (right alarm, wrong reason) |
| 28 | carrier_robust_observable | **GREEN** | a robust (median/MAD) observable resolves the confound — confirms #27's diagnosis |
| 29 | portfolio_falsifier | RED (PARTIAL) | consolidated: GREEN on every rupture family; one characterized residual — a location statistic cannot tell a stationary bimodal mixture from a shift |

Shape: **RED RED GREEN PARTIAL GREEN PARTIAL**. The inverse argument is
the spine: each RED *localised* a boundary, and the next GREEN
*confirmed that diagnosis* with a pre-registered mechanism — never a
tuned threshold. The two open PARTIALs are characterized, not hidden.

## The distilled primitive

All six collapse to one essence in `ctios.change_detection`:

```
detect = first_crossing( two_window_contrast(obs, loc, scale, w),
                          quantile_calibrated_threshold(·, null, α) )
```

The only thing that legitimately varies is the `(loc, scale)` pair —
`mean/std` (#26) vs `median/MAD` (#28) — and the window widths.
Everything else is shared, once. The earlier per-lineage duplication
was removed with **byte-identical** verdicts (guarded by
`tests/test_change_detection.py`): elegance without disturbing a single
sealed number.

## What is and is not

**Verified:** on synthetic families, a held-out-null-calibrated
two-window contrast detects a hidden rupture (incl. heavy-tail and a
bounded carrier confound) without false-alarming on the plain null,
dominating detect-everything / detect-nothing fakes — in one
consolidated sealed verdict.

**Characterized boundary (open, honest):** a location-contrast
statistic cannot separate a stationary bimodal mixture from a level
shift; closing it needs a distributional observable — a decision-gated
next lineage, proposed, not run.

**Not claimed:** anything about brains, neurons, cognition,
consciousness, intelligence, AGI, a theory of time, a private theorem,
real-world validity, or generality beyond these synthetic families.
