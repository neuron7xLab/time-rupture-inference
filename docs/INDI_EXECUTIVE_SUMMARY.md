# Executive Summary

**~3 minutes. No code required.**

**The problem.** A capable language model can produce a confident,
internally coherent evaluation of almost any research hypothesis —
including yours, including its own. It reads as rigorous. It is not, by
itself, evidence. The gap between *a system that can argue a claim is
true* and *a claim whose falsifier was run and did not trigger* is the
entire problem this artifact addresses.

**The apparatus.** A falsification-first temporal-inference engine. Its
benchmark is a hidden temporal rupture: an inter-event interval holds
one regime, then silently switches at an unseen step. The agent sees
only the realized signal — never the regime, switch time, or noise —
and must infer the change from its own prediction error. This is the
smallest environment where fluent language cannot fake adaptation:
either post-rupture error drops on pre-registered metrics across many
seeds, or it does not and the negative is kept. One positive is frozen
byte-identical (win-rate 1.000, ablation-necessary, no-leakage);
several lineages are preserved *negatives*, none tuned to pass, each a
sealed artifact with a reproduction command. The real asset is the
discipline as runnable code: claim → falsifier → evidence → boundary,
each arrow mechanically enforced — a pre-run hash, an adversarial
battery (rejects non-deterministic probes, decorative thresholds,
non-discriminative controls), and a lexicon gate that stops a claim's
text from exceeding its mechanism.

**Private R&D.** The engine consumes a *redacted hypothesis structure*,
not your research. You supply only the claim, null, assumptions,
variables, falsifier checks, forbidden inferences, and acceptable
evidence. Your mechanism is plugged in locally as an opaque probe the
engine calls but never inspects. The proprietary mechanism, dataset,
strategy, and theorem content never enter the public repository. The
engine needs the *shape* of the question, never the answer or the
method. Specified field by field in `docs/PRIVATE_RND_PROTOCOL.md`.

**Why this matters to you.** Your private cognitive-time work currently
lives as intuition and prose, where a capable model will always agree
with you. This converts one such claim into a pinned redacted skeleton,
attaches your mechanism as a local probe, and forces the claim through
its own kill-test *before* any belief is updated — IP entirely on your
side, self-deception removed from the loop. The output is a sealed
verdict and, on failure, a decision-gated next experiment. It is a
falsification loop with a mandatory human gate at every restart, not an
autonomous research agent.

**Next step.** Run `bash scripts/indi_demo.sh`, read one redacted
skeleton (`examples/indi_redacted_cognitive_time.yaml`), and answer
three questions: is this the research loop you meant; is the redacted
interface enough to protect your IP; what would make it useful for your
next private experiment. If the answers are yes/yes/concrete, the first
collaborative task is one redacted hypothesis from you + one local
probe + one agreed falsifier → one sealed verdict. The structured path
is `docs/INDI_REVIEWER_CHECKLIST.md`.

**What this explicitly does not claim.** Not cognition, consciousness,
artificial general intelligence, biological fidelity, or a universal
theory of time. It does not claim any private theorem is correct — it
cannot. It claims one thing: the difference between a plausible story
and a survived falsifier can be made mechanical, reproducible, and safe
to run on a private hypothesis without disclosing it. Scope and open
questions are stated, not implied, in `docs/INDI_LIMITATIONS.md`.
