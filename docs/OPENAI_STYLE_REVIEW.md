# Adversarial Self-Review

Written in the posture of hostile frontier-lab evals scrutiny. **No
lab has reviewed or endorsed this.** This document exists so the
strongest objections are stated by the author before a reviewer has to.

## Why this might be interesting

It targets a real, common failure: research loops that use capable
models as instruments and quietly let plausibility, a benchmark score,
or self-evaluation stand in for admissible evidence. The defenses are
mechanisms with tests, not principles. The redacted-hypothesis
interface is a concrete answer to "how do I let someone audit my claim
without showing them my method," which is a recurring blocker in
private/industrial research collaboration.

## Why this might be rejected

The benchmark is synthetic and small; the surviving positive is a
scalar estimator; there is no real-world dataset; the private
collaboration layer has not yet been exercised by an external
collaborator; and a skeptical reviewer may judge the documentation
stronger than the system. These are legitimate grounds for "not yet."

## Strongest objections

1. **Too synthetic.** A hidden-rupture toy may not transfer to real
   evaluation settings.
2. **Scalar estimator too simple.** The positive result may be trivial
   relative to what "adaptation" implies elsewhere.
3. **No real-world data.** Everything is in-silico.
4. **No biological validity.** The "temporal" framing invites a
   neuroscience reading the system does not support.
5. **Docs stronger than system.** Conference-grade prose can outrun a
   modest codebase.
6. **External originality unverified.** The integration may exist
   elsewhere under another name.
7. **Private layer unused.** The redacted interface has no external
   collaborator run yet — it is designed, not proven in practice.

## What evidence answers each objection

1/3. Scope is stated as a synthetic family in `docs/SPEC.md` and
`docs/INDI_LIMITATIONS.md`; no real-world claim is made, so this is a
boundary, not an overclaim. 2. The positive is deliberately scoped to
*adaptation*, not representational superiority; v7 NO_HEADROOM and v9
preserve the negative that a generic learner does not recover the hard
structure — the simplicity is acknowledged and bounded. 4. The
claim-boundary lexicon mechanically blocks cognition/biology language
in scanned files; "temporal" is defined formally, not biologically.
5. The smoke path makes the system runnable in ~10 minutes so prose can
be checked against behavior. 6. `docs/CONTRIBUTION_CLAIMS.md` disclaims
invention of falsification/evals/CI and scopes the claim to the
integration; external originality is marked OPEN, not asserted.
7. Stated as a residual risk in `docs/FAILURE_TAXONOMY.md`.

## What remains unresolved

External originality of the integrated pattern; whether the
redacted interface survives a genuinely adversarial real hypothesis;
whether the discipline transfers off the synthetic family; whether the
human-gate becomes a bottleneck at scale. None of these are claimed as
solved.

## Minimal next experiment

One external collaborator supplies one redacted hypothesis and one
local opaque probe; the apparatus produces one sealed verdict and one
human-gated next-experiment proposal; the collaborator confirms no
never-share field had to leak. That single run converts the private
layer from *designed* to *demonstrated* — and is the smallest result
that would answer objection 7.
