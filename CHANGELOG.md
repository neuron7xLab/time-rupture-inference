# Changelog

All notable changes to this project. Format: falsification lineage —
every RED is preserved, never rewritten.

## [unreleased] — research lineage v7 → v8.2 (stage closure)

Post-0.1.1 falsification arc. Zero release behaviour change (v4 frozen
byte-identical `0.8830/8.0028/0.7933`, v5 `gain 0.8680`). Every verdict
isolated from CI; a legitimate RED keeps `main` green.

- **v7 RED** — learned reservoir/SSM ≤ frozen heuristic on the rupture
  class (`NEGATIVE_RESULT_v7.md`).
- **v7-diagnostics NO_HEADROOM** — heuristic within 14.1% of the
  regime-aware oracle; boundary localized to the *task*, not the model
  (`CONVERGENCE_v6_v7.md`).
- **v8 RED** — scalar-inexpressible env, trigger ≈1.2e-5/step →
  decorative (`NEGATIVE_RESULT_v8.md`).
- **v8.1 RED** — trigger frequency fixed (1500); inexpressibility *real*
  but whole-stream carrier-masked (`V8_PARENT_RED.md`).
- **v8.2 PARTIAL_RED** — trigger-scoped + carrier-controlled diagnostic:
  scalar-inexpressibility **confirmed & carrier-robust** (tc 0.470,
  cc 0.465); reference history-oracle under-specified (h2r 4.22).
  Stronger-model testing remains not askable.
- Added GCP-readiness (`v0.1.1`), automation gateway, and the
  oracle-hierarchy / trigger-frequency / carrier-decomposition
  diagnostic modules. No learned model trained anywhere in v6–v8.2.
- Canonical state: `docs/reports/LINEAGE_STATE.md`. Next step (v8.3,
  correctly-specified history oracle) is decision-gated, not auto-run.

## [0.1.1] — 2026-05-18

Production-hardening cycle. **Zero behaviour change**: v4 byte-identical
(`learned 0.8830 / injected 8.0028 / oracle 0.7933`), v5 `gain 0.8680`.

### Added
- `mypy --strict` clean on `src/ctios` (16 files); enforced via
  `[tool.mypy]` + CI step + 3.11/3.12 matrix.
- `LearnedAgent` constructor guards: out-of-range gains/scales/horizons
  now fail fast with `ValueError`.
- Opt-in `anti_divergence` convergence guard (sign-flip gain damping).
  **Default OFF by deliberate deviation from the proposed patch** —
  enabling it changes the update law and would silently mutate the
  frozen, tagged v4 number; it is a separate pre-registered improvement
  line, never folded into the v4 baseline.
- Multi-seed robustness for the overshoot regression (median late-regime
  peak across a seed set, not a single fragile seed).
- `requirements-lock.txt` (pinned), `.gitignore` cache/coverage entries.

- Single-source `eval_horizon` contract + fail-loud `validate_window`
  (kills the silent-pseudo-GREEN window-drift class); E0 follow-up adds
  window-overflow + cross-series alignment guards.
- AST gate: every post-shift slice site must call `validate_window`.
- v5 minimal causal-action line merged (PR #1): `causal_action_gain
  0.868`, action_null gap 0.000, win 1.000 — opt-in, claim-bounded.
- v5 `action_counts` made window-scoped (+ total/pre/post views) —
  closes the same scope-ambiguity class; v5 verdict unchanged.
- Automation gateway `ctios.automation` (one-command CI-contract repro,
  UTC ledger to gitignored `runs/`); stale-base regressions from the
  proposed patch rejected.
- README test-count drift killed structurally via enforced
  `test_readme_sync` (CI fails on drift).

### Lineage outcomes (negatives preserved, never erased)
- **v6 precision-weighting (Kalman / predictive-coding analogy) — RED.**
  Pre-registered; regret precision 0.5422 vs fixed 0.0897, win 1/90.
  The heuristic drift-boost is near-oracle (no headroom); brain-inspired
  ≠ better here. `evidence/NEGATIVE_RESULT_v6.md`, not tagged, opt-in OFF.

### Governance
- Audit P0/P1/P2/P3 closed: `claims.yaml` lexicon + lint, taxonomy card,
  SPDX + `provenance_manifest.json` (internal CLOSED; external scan
  honestly OPEN), `invariants.yaml` register, config-surface single
  source. Ledgers: `docs/AUDIT_CLOSURE_LEDGER.md`,
  `docs/AUDIT_DEBTS_2026-05-18.md` (PARTIAL never rounded to GREEN).

## [0.1.0] — 2026-05-18

First canonical release. Convergence of the full proof-of-life lineage
into one coherent system, local ≡ cloud.

### Lineage (git tags, all public)

| tag | verdict | meaning |
|---|---|---|
| `cti-os-v1-RED` | RED | Page-Hinkley poisoned by cold-start transient |
| `cti-os-v2-GREEN` | GREEN | base proof of life, 16 seeds |
| `cti-os-v3-RED` | RED | two new doctoral-critique controls mis-specified |
| `cti-os-v4-GREEN` | GREEN | full doctoral critique closed, 19/19, 30×3 grid |

### Added
- 30 seeds × 3 shift magnitudes (incl. a decrease shift) power grid.
- Shuffled-order leakage kill-control (mean over seeds, 2% noise band).
- Four measured neuroplasticity markers (synaptic / homeostatic /
  neuromodulation / extinction) — gated, never rhetorical.
- Hidden-parameter provenance hashes in the evidence ledger.
- Pre-registration sha-pinned and git-committed before every run.
- MIT license, packaging, `tri-gate` entry point, CI (cloud parity).

### Invariant
Scientific PASS thresholds byte-identical from `v2` to `v4`
(provable: `git show cti-os-v2-GREEN:prereg/preregistration.yaml`).
A RED verdict is reported as RED. No threshold was ever tuned to green.
