# CTI-OS v7 — Pre-registration (pinned before any v7 run)

**Status:** infrastructure-ready; scientific run NOT yet executed.
**Phase 1 policy:** CPU-only, no GPU, no paid cloud.

> **Pre-run model-definition correction (2026-05-18, before any full
> grid + before observing results).** The implemented learned candidates
> are numpy reservoir-readout recurrent learners with online-learned
> readouts: `esn_small` (echo-state-style) and `linear_ssm_small`
> (learned linear state-space). They are **not** a back-prop-trained
> GRU. To avoid a mislabeled-instrument verdict, model names are
> corrected to match the implementation **before** the run; thresholds,
> environment, seeds, and the decision rule are unchanged. A
> back-prop-trained GRU is a separate, later pre-registered lineage.
> Honest scoping, not a post-hoc tweak.

## Hypothesis
A learned sequence model (small GRU and/or small linear state-space
model) achieves lower post-shift error than (a) the frozen v4 heuristic
and (b) a from-scratch conventional baseline, on a harder
**multi-regime, partially-observable, nonstationary** environment where
a scalar estimator provably cannot represent the structure.

## Null hypothesis
The learned sequence model does **not** beat both the v4 heuristic and
the from-scratch baseline on the harder environment (no representational
advantage). The null is the default; it is rejected only by artifacted,
reproducible evidence.

## Model candidates
`heuristic_v4` (reference, not the claim) · `esn_small` ·
`linear_ssm_small` · `ar_baseline` (from-scratch conventional).

## Baselines
v4 heuristic (frozen, byte-identical) and the from-scratch conventional
baseline. A win must hold against **both**.

## Environment specification
`multi_regime_partial_observability`: ≥2 hidden regime switches,
observation = noisy + intermittently masked interval; agents never see
regime id, switch times, noise, or mask schedule.

## Shift magnitudes
`[7.0, 12.0, -5.0]` (includes a decrease), per `configs/v7_experiment.yaml`.

## Seed policy
`seed_start=0`, `seed_count=30` (smoke: 3). All seeds in
`seed_manifest.json`; deterministic replay required.

## Leakage prevention
Models receive only the observation stream + own prediction error.
Constructor-introspection + no hidden-parameter channel (inherits the
existing `claims.yaml` / no-leakage discipline).

## Metrics
`post_shift_mae`, `recovery_steps`, `win_rate_vs_heuristic`,
`win_rate_vs_baseline`, `calibration_error`.

## Acceptance thresholds (GREEN conditions)
1. learned model `post_shift_mae` < v4 heuristic (aggregate, ≥0.6 win-rate)
2. learned model `post_shift_mae` < from-scratch baseline (≥0.6 win-rate)
3. effect holds across all shift magnitudes and ≥30 seeds
4. deterministic replay hash stable
5. no leakage; metrics finite; artifacts complete

## RED conditions
Any of: learned ≤ heuristic OR ≤ baseline aggregate; single-seed-only
win; NaN/inf; leakage; metric changed after run; artifacts missing.
A RED is preserved as a negative artifact, never erased.

## Claim boundary
Allowed (only if GREEN): a learned sequence model has a representational
advantage over a scalar heuristic on a harder nonstationary task under
preregistered metrics. **Forbidden:** intelligence / consciousness /
biological neuroplasticity / brain fidelity / AGI / cognition.

## Artifact list
`metrics.csv`, `seed_manifest.json`, `run_config_resolved.yaml`,
`environment_fingerprint.json`, `git_commit.txt`.

## No-GPU phase-1 policy
Phase 1 runs CPU-only. GPU is a documented future phase, manually
unlocked **only** after the CPU phase produces a GREEN or an honest RED
— never speculatively.
