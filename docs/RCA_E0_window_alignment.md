# RCA: E0 Silent Window/Alignment Distortion in Causal Metrics

## 1) One-sentence problem statement

Metric code accepted inputs where the **declared evaluation scope** and the
**effective computed scope** diverged, allowing valid-looking numbers to be
produced from structurally invalid slices.

## 2) Falsifiable hypothesis

If the metric contract is complete, then any run with:

- `t_star + eval_horizon > n`, or
- `len(errors) != len(actions)`

must fail before aggregation with `ValueError`; no partial/implicit truncation
is allowed.

**Refutation condition:** if such inputs ever produce a metric dict instead of
raising, the contract is incomplete.

## 3) Invariant (pre-code)

For every post-shift metric:

1. `window = [t_star, t_star + eval_horizon)` must be a subset of `[0, n)`.
2. Every paired series consumed by the metric must be index-aligned with length
   `n`.
3. The declared window and effective window must be identical.

## 4) Root cause vs key causes

### Root cause (first principle failure)

Contract incompleteness at the measurement boundary: slicing semantics were
trusted to behave as validation.

### Key causes (proximate contributors)

1. Bounds validation initially did not encode `t_star + eval_horizon <= n`.
2. Paired-series alignment (`errors` vs `actions`) was not guarded at the same
   contract boundary.
3. Contract concerns (window bounds vs cross-series alignment) were initially
   coupled in one path, increasing misuse risk.

## 5) Mechanism of distortion

1. Inputs violate scope/alignment.
2. Python slice semantics clamp implicitly instead of failing.
3. Aggregation returns finite values (`mean`, ratios).
4. Downstream logic treats outputs as valid evidence.

This is a **silent pseudo-validity channel**, not a loud failure.

## 6) What this diff changed structurally

- Window bounds are fail-loud in `validate_window` (adds the
  `t_star + eval_horizon <= n` clause).
- Cross-series alignment is fail-loud in `validate_aligned_lengths`.
- `run_metrics` now applies both guards before any post-shift aggregation.
- Regression tests encode both failure modes.

## 7) Incident classes prevented

1. **Overflow window incident:** post-shift metrics computed on fewer points than
   declared.
2. **Cross-series misalignment incident:** action-based post-shift summaries
   computed on a different effective support than error metrics.
3. **Pseudo-GREEN incident:** release criteria passed on numerically plausible
   but contract-invalid evidence.

## 8) Residual risk register (future incidents)

1. **New metric path bypasses contract helpers**
   - Leading indicator: post-shift slices in code without nearby validation call.
   - Control: static grep gate + review checklist item.

2. **Third series added (e.g., interventions/logits) without alignment guard**
   - Leading indicator: heterogeneous list/array inputs in metric API.
   - Control: require explicit alignment checks for each paired substrate.

3. **Semantic drift between docs and code contracts**
   - Leading indicator: README claims fixed horizon while tests allow implicit
     truncation.
   - Control: contract tests treated as release gate.

## 9) Repair protocol (max-impact intervention)

1. Keep contract primitives orthogonal:
   - bounds guard;
   - alignment guard.
2. Enforce "validate-before-slice" in all metric entry points.
3. Keep negative tests for adversarial boundaries and misalignment.
4. Treat any silent truncation path as a release blocker.

## 10) Success criteria (not just completion)

Success is achieved when:

- invalid windows and misaligned paired series are impossible to score
  silently (fail-loud everywhere),
- adding/removing any guard re-opens at least one failing test,
- metric claims remain traceable to explicit, enforced contracts.

## 11) Frozen-invariant attestation (this repo)

v4 numbers byte-identical after the hardening (`learned post_shift_mae 0.8830`,
`injected 8.0028`, `oracle 0.7933`); v5 `causal_action_gain 0.8680`,
`action_null_gap 0.0000`. The guard rejects only contract-invalid inputs; no
valid scientific path changed. The proof was not perturbed — only the
silent-failure surface was removed.
