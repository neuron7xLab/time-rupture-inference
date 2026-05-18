# Reviewer Checklist

## Fastest useful path

1. Read `docs/INDI_README.md`.
2. Run `bash scripts/indi_demo.sh`.
3. Open `examples/indi_redacted_cognitive_time.yaml`.
4. Answer the three feedback questions (in INDI_README and at the end
   of the demo script).

That is enough to decide if this is worth a conversation. The tiers
below are for going deeper, not prerequisites.

---

A graded path. Each tier is self-contained; stop at the depth your
time allows. Every box is a concrete, checkable thing — not an opinion.

## 10-minute review

- [ ] Read `docs/INDI_README.md` — confirm the claim/non-claim split is
      explicit, not implied.
- [ ] Read `docs/INDI_EXECUTIVE_SUMMARY.md` — confirm the asset stated
      is the discipline (claim → falsifier → evidence → boundary), not
      a result.
- [ ] Skim `docs/INDI_LIMITATIONS.md` — confirm the "does not prove"
      list includes cognition, consciousness, biological fidelity,
      general intelligence, universal theory of time, commercial value,
      and correctness of any private theorem.
- [ ] Confirm no hype vocabulary (breakthrough / genius / AGI /
      understanding) appears as an asserted capability anywhere.

## 30-minute review

- [ ] `pip install -e ".[dev]"` then `bash scripts/indi_demo.sh`;
      confirm it ends with the single explicit success line.
- [ ] Confirm the frozen runner prints byte-identical
      `learned post_mae=0.8830 injected=8.0028 oracle=0.7933`.
- [ ] Read `examples/indi_redacted_cognitive_time.yaml` — confirm it
      carries no mechanism, dataset, or theorem content, and that
      `human_review_required: true` and `auto_run: false`.
- [ ] Read `docs/PRIVATE_RND_PROTOCOL.md` §3/§4 — confirm the
      safe-to-share vs never-share split is unambiguous.
- [ ] Confirm `python scripts/claims_lint.py` passes (no claim
      inflation in README or source).

## Full technical review

- [ ] Inspect `ctios.falsify`: confirm the pinned `spec_sha256` covers
      assumptions and variables, so a post-hoc threshold change is
      detectable.
- [ ] Inspect the adversarial battery: confirm it rejects a
      non-deterministic probe, a non-finite metric, a non-load-bearing
      threshold, and a non-discriminative negative control.
- [ ] Run `pytest tests -q`; confirm the engine contract tests
      (`tests/test_falsify_engine.py`) and the verdict-isolation
      property both hold.
- [ ] Trace a non-green path: confirm `NEXT_<hid>.yaml` is *proposed*
      (tightened survivors, failed boundary as focus) and never
      auto-run.
- [ ] Read `docs/SPEC.md` S1–S7 and `docs/reports/LINEAGE_STATE.md`;
      confirm every red is a preserved artifact with a reproduction
      command and no threshold was tuned to green.

## What would falsify this package

- A threshold can be changed after a run without the pinned hash
  changing.
- The battery passes a deliberately non-deterministic or
  pseudo-discriminative probe.
- A frozen number is not byte-identical on a clean clone.
- A red lineage exists with no sealed artifact or no reproduction path.
- `scripts/indi_demo.sh` reports success while a hard gate actually
  failed.
- A claims-lint-forbidden term is asserted as a capability outside a
  disclaimer block.
- The redacted interface cannot be filled for a real hypothesis without
  writing private structure into a never-share field.

## What would make it useful for private R&D

- The redacted skeleton + opaque probe interface holds for a
  hypothesis structurally unlike the bundled temporal one.
- The negative-control authoring cost is acceptable for the
  reviewer's own research cadence.
- The mandatory human gate is a feature, not a bottleneck, at the
  reviewer's experiment rate.
- A sealed verdict + decision-gated next experiment measurably reduces
  self-deception on a line that currently lives as intuition.

## Questions for Inderjit

1. Where does an autonomous research loop genuinely help versus where
   does the mandatory human approval gate need to stay hard — is the
   gate a feature or a limit for the way you work?
2. Is the redacted-theorem interface (claim / null / assumptions /
   variables / falsifiers / forbidden inferences / acceptable
   evidence + opaque local probe) sufficient to express a real private
   hypothesis of yours without leaking structure?
3. Which part of this matters most to you — the falsification engine,
   the redacted private-R&D protocol, the frozen reproducible positive,
   or the preserved-negatives discipline?
4. What concretely would make this useful for your own private
   research, and what is currently missing for that?
