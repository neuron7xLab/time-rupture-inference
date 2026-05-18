# External Review Package — Read Me First

A focused entry point for an external technical reviewer. It exists to let
you evaluate one apparatus on its merits without any private research
material changing hands.

## What this is

A falsification-first **temporal-inference apparatus** plus a runnable
online adaptive agent and a reusable falsification engine
(`ctios.falsify`). The dominant deliverable is not a result; it is the
machinery that produces honest negatives: a pinned hypothesis
(claim / null / assumptions / variables / falsifier checks) is run
through an adversarial battery, sealed into a reproducible verdict
artifact, and — when it does not pass — turned into an auto-proposed,
decision-gated next experiment.

The system does not ask for your private theorem. It provides the
machinery that can test one.

## What this is not

It is not a cognitive system, a model of the brain, a general
intelligence, or a theory of time. It does not claim
learned-representation superiority. It does not auto-run the next
experiment. It does not need your private mechanism, dataset, or
strategy to be useful — see `docs/PRIVATE_RND_PROTOCOL.md`. The
boundaries of every surviving positive are stated in `docs/SPEC.md`
and `docs/INDI_LIMITATIONS.md`, not implied.

## Why this exists

LLM-style systems can produce a fluent, plausible self-evaluation of
almost any hypothesis. That fluency is not evidence. The purpose of
this apparatus is to make the difference between *plausible* and
*falsified-and-survived* mechanically enforced rather than rhetorical:
a claim is admitted only because its pre-registered kill-test was run
and did not trigger, and the evidence is a sealed artifact, not prose.

## What problem it solves

Self-deception in research that uses capable models as instruments.
The concrete failure modes it closes: a threshold quietly tuned to
green; a metric that is decorative rather than load-bearing; a
negative control that also "passes" so the gate is not discriminative;
a non-deterministic probe reported as a result; a claim whose text
exceeds the implemented mechanism. Each of these is caught by a
specific, testable gate, not by reviewer goodwill.

## How it maps to private R&D

The engine takes a *redacted* hypothesis interface. A collaborator
supplies only the structural skeleton — claim, null, assumptions,
variables, falsifier checks, forbidden inferences, acceptable
evidence — and plugs the private mechanism in locally as an opaque
`Probe`. The engine never reads the mechanism, the data, or the
proprietary reasoning. The protocol for this is specified field by
field in `docs/PRIVATE_RND_PROTOCOL.md`, with an example skeleton in
`examples/indi_redacted_cognitive_time.yaml`.

## How to run it

```bash
pip install -e ".[dev]"
bash scripts/indi_demo.sh
```

The script runs the claim lexicon lint, provenance attestation, the
full test suite, the frozen temporal-adaptation runner (byte-identical
numbers on any machine), and — when present — the causal-action and
streaming-agent demos. It fails loud on any hard gate and prints a
single explicit success line at the end. Full walkthrough:
`docs/DEMO.md`. Formal claim → falsifier → evidence → boundary map:
`docs/SPEC.md`.

## What feedback is requested

Concrete, adversarial, and specific. The reviewer checklist
(`docs/INDI_REVIEWER_CHECKLIST.md`) lists what would *falsify* this
package and what would make it useful for private research. The
single highest-value input: identify a path by which a false positive
could survive the battery, or a redacted-interface field that would
have to leak private structure for the engine to be useful. If neither
exists, say which part is the load-bearing one for your own work.
