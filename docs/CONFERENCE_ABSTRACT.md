# TRI-Falsify: A Claim-Boundary-Enforced Falsification Apparatus for Hypothesis Auditing

**Workshop track: AI evaluation / research tooling. ~320 words.**

**Problem.** Evaluation of capable models and agents routinely confuses
three things with admissible evidence: a plausible generated argument,
a benchmark score, and a model's own self-evaluation. Each can be
fluent and internally coherent while being epistemically empty. The
practical failure is not a wrong number; it is a research loop in which
a threshold is quietly tuned to pass, a metric is decorative, a
negative control also passes, or a claim's prose exceeds the mechanism
it rests on — and nothing in the tooling objects.

**Contribution.** This repository implements a falsification-first
temporal-inference apparatus and a generalized hypothesis-falsification
loop (`ctios.falsify`). The contribution is not falsification, CI, or
temporal prediction in isolation — none of which are new — but their
*integration as an enforced discipline*: a pinned, hashed hypothesis
specification; an adversarial battery that rejects non-deterministic
probes, decorative thresholds, and non-discriminative negative
controls; a sealed reproducible verdict; a machine-checked claim
boundary; and a human-gated next-experiment proposal.

**Method.** A hidden temporal rupture benchmark (an inter-event
interval that silently changes regime at an unseen step; the agent sees
only the realized signal) instantiates the discipline. Claims are
admitted only via the chain claim → falsifier → evidence → boundary.
Every RED and GREEN lineage is preserved as a sealed artifact, never
overwritten.

**Result.** Frozen, byte-identical on any machine:
`learned post_mae=0.8830 injected=8.0028 oracle=0.7933`;
`gain=0.8680 null_gap=0.0000`. Several lineages are preserved negatives;
none tuned to pass.

**Boundary.** Not cognition, not AGI, not biological fidelity, not a
universal theory of time. No learned-representation-superiority claim.

**Reuse.** Any private hypothesis is expressible as a redacted
specification plus a local opaque probe plus a falsifier; the apparatus
audits the *shape*, never the mechanism or data.
