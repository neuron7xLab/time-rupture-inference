# Executive Summary — For a Busy Technical Founder

**Read time: ~4 minutes. No code required to follow this page.**

## The premise this is built against

A sufficiently capable language model can produce a confident,
internally coherent evaluation of almost any research hypothesis —
including yours, including its own. The evaluation will read as
rigorous. It is not, by itself, evidence. The gap between *a system
that can argue a claim is true* and *a claim whose falsifier was run
and did not trigger* is the entire problem this artifact addresses.
The deliverable is the machinery that enforces that distinction
mechanically, so it cannot be talked around.

## What the apparatus is

A falsification-first temporal-inference apparatus. Its concrete
benchmark is a hidden temporal rupture: an inter-event interval holds
one regime, then silently switches to another at an unseen step. The
agent never observes the regime, the switch time, or the noise — only
the realized signal. It must infer that the world changed from its own
prediction error and re-adapt. This is deliberately the smallest
environment in which fluent language cannot fake adaptation: either
the post-rupture error drops on pre-registered metrics across many
seeds and shift magnitudes, or it does not, and the negative is kept.

On that benchmark one positive is frozen and byte-identical on any
machine (a learned scalar estimator beats a hard-wired and the best
naive baseline post-rupture, win-rate 1.000, with an ablation proving
the drift mechanism necessary and a no-leakage check). Several other
lineages are preserved **negatives** — a precision-weighted variant
that was principled but not better, a learned sequence model that did
not exceed the heuristic, a constructed task whose first gate was
proven information-theoretically unattainable before it was re-derived
honestly. None of these were tuned to pass. Every red is a sealed
artifact with a reproduction command.

## The actual asset

The asset is not the frozen positive and not the benchmark. It is the
research discipline expressed as runnable code:
**claim → falsifier → evidence → boundary**, with each arrow
mechanically enforced. A claim must be pre-registered and hashed
before the run. The verdict goes through an adversarial battery: it
rejects a non-deterministic probe, a non-finite metric, a threshold
that is decorative rather than load-bearing, and a negative control
that also passes (which would mean the gate does not discriminate).
The pinned specification hash covers the assumptions and the variables,
so silently retuning a threshold changes the hash and is detectable.
A claim's external text cannot exceed the implemented mechanism: a
machine-checkable lexicon, enforced in CI and tests, blocks
cognition / general-intelligence / neural-equivalence language outside
an explicit disclaimer. When a hypothesis does not pass, the engine
auto-proposes the next experiment — surviving checks tightened, the
failed boundary made the focus, assumptions demoted to open
questions — and it never runs that next experiment itself. A human
gate is mandatory.

## Why it is safe for private collaboration

The engine consumes a *redacted hypothesis structure*, not your
research. A collaborator supplies only: the claim, the null, the
assumptions, the variables, the falsifier checks, the forbidden
inferences, and what counts as acceptable evidence. The private
mechanism is plugged in locally as an opaque probe — a function the
engine calls but never inspects. The proprietary mechanism, the
dataset, the strategy, and the content of the private theorem do not
need to enter the public repository at any point. The engine needs the
*shape* of the question, never the answer or the method. This is
specified field by field in `docs/PRIVATE_RND_PROTOCOL.md`, with a
worked redacted skeleton in
`examples/indi_redacted_cognitive_time.yaml`.

## The strongest next use

The highest-value application is private theorem-to-experiment
conversion: take a research claim that currently lives only as
intuition and prose, express it as a pinned redacted skeleton, attach
the private mechanism as a local probe, and let the apparatus force
the claim through its own kill-test before any belief is updated. The
output is a sealed verdict and, on failure, a decision-gated next
experiment — a falsification loop with a mandatory human approval gate
at every restart, not an autonomous research agent. The point is to
make a private research line *harder to fool itself*, while the IP
stays entirely on the collaborator's side.

## What this explicitly does not claim

This does not claim cognition, consciousness, artificial general
intelligence, biological fidelity, or a universal theory of time. It
does not claim that any private theorem is correct — it cannot, and
asserting otherwise would itself violate the lexicon gate. It claims
exactly one thing: that the difference between a plausible story and a
survived falsifier can be made mechanical, reproducible, and safe to
run on a private hypothesis without disclosing it. The scope and the
open questions are stated, not implied, in
`docs/INDI_LIMITATIONS.md`.

## What is asked of the reviewer

A short, adversarial pass: find a route by which a false positive
survives the battery, or a redacted field that cannot be filled
without leaking private structure. If neither exists, identify which
component is load-bearing for your own work. The structured checklist
is in `docs/INDI_REVIEWER_CHECKLIST.md`.
