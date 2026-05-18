# CTI-OS v7 diagnostics — Pre-registration (pinned before the run)

Context: v6 (precision-weighting) RED and v7 (reservoir/SSM) RED are two
surface-distinct, root-convergent negatives. Before grinding more model
lineages on the v7 environment, one diagnostic must discriminate the
root cause. This is pre-registered **before** observing the result.

## Hypothesis (our reading of the v6+v7 convergence)
**NO_HEADROOM:** on the v7 multi-regime, partially-observable rupture
environment, the disciplined scalar heuristic already operates within a
small margin of the information-theoretic floor (the regime-aware
oracle). Therefore no model class — precision-weighted, reservoir, SSM —
can pay its complexity, because there is almost nothing left to win.

## Null / falsifier
**LEARNABLE_GAP:** the oracle substantially outperforms the heuristic
(headroom is large) yet the learned models still lost. That would
*refute* the no-headroom reading and mean the negatives are a learning /
capacity failure, redirecting the line to better learners (not a new
environment).

## Decision metric (frozen before run)
`headroom_ratio = (agg_heuristic - agg_oracle) / agg_heuristic`
over the full 30 seeds × 3 shifts v7 grid (same `_drive`/`_env_stream`).

- `headroom_ratio <= 0.15`  → **NO_HEADROOM** (environment is the
  boundary; redirect: build an env where oracle ≫ heuristic, i.e.
  structure a scalar provably cannot represent — long-range / latent
  dependence — before any "stronger model" question is askable).
- `headroom_ratio > 0.15`   → **LEARNABLE_GAP** (model/optimization is
  the boundary; redirect: better learners on the same env).

Secondary, descriptive only: `esn_latent_separability` — variance ratio
of the reservoir hidden state across vs within the 3 regimes (smoothing
≈ low separability; representation ≈ higher). Not a gate.

## Threshold rationale (not tuned to pass)
0.15 = the heuristic is "near-oracle" if it is within 15% of the
irreducible floor; chosen on first principles (a sequence model needs a
materially larger gap than 15% to plausibly pay its complexity), pinned
before the run.

## Claim boundary
This diagnostic localizes a *boundary condition*, not a capability. No
intelligence / cognition / AGI claim. RED-as-product discipline applies:
whichever branch, it is preserved as a delivered convergence artifact.
