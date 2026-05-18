# TRI-Falsify — Reviewer One-Pager

*For a reviewer who will not read the full README. ~420 words.*

**System identity.** TRI-Falsify is a falsification-first
temporal-inference and hypothesis-auditing apparatus. A pinned,
hashed hypothesis runs through an adversarial battery into a sealed,
reproducible verdict; on failure it auto-proposes a human-gated next
experiment. It never auto-runs anything.

**Why it exists.** Capable models can produce a fluent, coherent
defense of almost any hypothesis — including their own evaluation of
it. That fluency is not evidence. This apparatus makes the difference
between *plausible* and *falsified-and-survived* a mechanical property,
not a rhetorical one.

**One-line contribution.** Not falsification, CI, or temporal
prediction (all prior art) — but their integration into one
fail-closed loop: redacted hypothesis spec + local opaque probe +
adversarial falsifier battery + sealed verdict + preserved evidence
ledger + human-gated next experiment, runnable on a private hypothesis
without disclosing its mechanism.

**How to run (≈10 min, CPU, no network).**

```bash
pip install -e ".[dev]"
bash scripts/conference_smoke.sh
```

**What to inspect.** `docs/SYSTEM_CARD.md` (abstraction + boundaries),
`ctios.falsify` (`HypothesisSpec`, `run_battery`, `next_experiment`),
`examples/indi_redacted_cognitive_time.yaml` (redacted skeleton),
`docs/CONTRIBUTION_CLAIMS.md` (original vs prior art),
`docs/FAILURE_TAXONOMY.md` (defenses + residual risk).

**Strongest claim.** A frozen, byte-identical positive on any machine:
`learned post_mae=0.8830 injected=8.0028 oracle=0.7933`,
win-rate 1.000, ablation-necessary, no-leakage; and an engine whose
battery mechanically rejects non-deterministic probes, decorative
thresholds, and pseudo-GREEN negative controls.

**Hard non-claims.** No cognition, consciousness, AGI,
biological-fidelity, or universal-theory-of-time claim. No
learned-representation-superiority claim. It does not certify any
private theorem correct.

**What would falsify this package.** A threshold changeable after a run
without the spec hash changing; the battery passing a deliberately
non-deterministic or pseudo-discriminative probe; a frozen number not
byte-identical on a clean clone; a RED lineage with no sealed artifact;
the smoke script reporting success while a hard gate failed; a real
hypothesis class that cannot be redacted without leaking a never-share
field.

**How to extend.** Write a pinned spec, implement a local
`probe(thresholds) -> {metric: value}`, add a discriminative negative
control, call `ctios.falsify.falsify(...)`, inspect the sealed verdict
and the proposed next experiment. For a *redacted private* hypothesis
use the typed platform layer (`ctios.redacted` / `redacted_io` /
`opaque_probe` / `falsifier_battery` / `spec_compiler` / `human_gate` /
`report`); end-to-end demo: `bash scripts/platform_demo.sh`. Full
steps: `docs/REPRODUCIBILITY_CONTRACT.md`. Adversarial self-review:
`docs/OPENAI_STYLE_REVIEW.md`.
