# Cognitive-Time R&D Demonstration for Inderjit

## Read this first

This repository is not a theory pitch. It is a runnable falsification
apparatus for testing redacted cognitive-time hypotheses without
exposing private IP.

In 10 minutes you can:

1. inspect the claim boundary (`docs/INDI_LIMITATIONS.md`),
2. run the demo (`bash scripts/indi_demo.sh`),
3. see the frozen, byte-identical numbers print,
4. decide whether this machinery is useful for your private
   theorem-to-experiment work.

The system does not ask for your private theorem. It provides the
machinery that can test one. Your mechanism, data, and theorem content
stay on your side — see `docs/PRIVATE_RND_PROTOCOL.md`.

**Three feedback questions** (this is the only thing asked of you):

- Is this close to the research loop you meant?
- Is the redacted hypothesis interface enough to protect your IP?
- What would make this useful for your next private experiment?

## What this is

A falsification-first temporal-inference apparatus, a runnable online
agent, and a reusable engine (`ctios.falsify`). A pinned hypothesis
(claim / null / assumptions / variables / falsifier checks) runs
through an adversarial battery, seals into a reproducible verdict, and
— on failure — auto-proposes a decision-gated next experiment that a
human must approve.

## What this is not

Not a cognitive system, brain model, general intelligence, or theory
of time. No learned-representation-superiority claim. Nothing auto-runs.
It does not need your private mechanism, dataset, or strategy to be
useful. Boundaries are stated in `docs/SPEC.md` and
`docs/INDI_LIMITATIONS.md`, not implied.

## Why this exists

A capable model can produce a fluent, plausible self-evaluation of any
hypothesis — including yours. That fluency is not evidence. This
apparatus makes the difference between *plausible* and
*falsified-and-survived* mechanically enforced: a claim is admitted
only because its pinned kill-test ran and did not trigger, and the
evidence is a sealed artifact, not prose.

## How it maps to private R&D

The engine takes a redacted skeleton — claim, null, assumptions,
variables, falsifier checks, forbidden inferences, acceptable evidence
— and calls your private mechanism as an opaque local `Probe` it never
inspects. Specified field by field in `docs/PRIVATE_RND_PROTOCOL.md`;
worked skeleton in `examples/indi_redacted_cognitive_time.yaml`.

## How to run it

```bash
pip install -e ".[dev]"
bash scripts/indi_demo.sh
```

Hard gates fail loud; the script ends by telling you what to read next
and the three questions above. Full walkthrough: `docs/DEMO.md`.
Formal claim → falsifier → evidence → boundary: `docs/SPEC.md`.
Fastest path: `docs/INDI_REVIEWER_CHECKLIST.md`.
