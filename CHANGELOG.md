# Changelog

All notable changes to this project. Format: falsification lineage —
every RED is preserved, never rewritten.

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

### Governance
- Audit debts ledger `docs/AUDIT_DEBTS_2026-05-18.md` (closed vs still
  open P2/P3, no rounding up).

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
