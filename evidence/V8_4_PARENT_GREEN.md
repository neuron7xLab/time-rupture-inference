# V8.4 PARENT GREEN — the benchmark v9 is allowed to use

PR #10 (v8.4) merged GREEN: a carrier-controlled scalar-inexpressible
benchmark whose causal floor is **proven reachable** (analytic
h2r_causal_min=0.1588 ≤ 0.35; correctly-specified causal oracle attains
it empirically 0.1851; tc=0.882, cc=0.882). Gates byte-identical to
v8.2/v8.3; only the env was re-derived from first principles.

## Why v9 may now run a learned model
The "no learned model" hard rule applied to the *benchmark-validation*
lineage (v6–v8.4) — a learner must not be tested until the task
provably rewards latent state. v8.4 established exactly that:
- a scalar oracle provably CANNOT sign the trigger (orthogonal to any
  observable scalar);
- a history/causal oracle CAN reach the floor (proven, attained).

So "can a *learned* sequence model recover the scalar-inexpressible
structure from observations alone?" is, for the first time,
scientifically well-posed. v9 is a NEW lineage with v8.4 GREEN as the
preserved parent; the v8.4 gates (h2r 0.35) are reused unchanged.
