# Documentation Style Contract

Documentation is not accepted unless it is testable. This contract is
enforced by `scripts/check_doc_trust.py` and
`tests/test_doc_trust.py`.

## Rules

1. **Every external-facing paragraph resolves to one of:** in-repo
   evidence, a canonical source, an explicit non-claim boundary, an
   open structural gap, or a logged downgrade/deletion.
2. **No claim without a claim_id.** Major claims live in
   `docs/CLAIM_SOURCE_MATRIX.md` with a class, evidence path, source,
   and falsifier.
3. **No source without a mapping.** A source in
   `evidence/SOURCE_REGISTRY.yaml` must support ≥1 claim_id or repo
   file. No prestige padding.
4. **Inspiration carries its boundary.** Any `INSPIRATION_ONLY` claim
   states "does not imply biological fidelity" on the same line or
   within a disclaimer block.
5. **Supply-chain claims carry their ceiling.** Any
   `SUPPLY_CHAIN_TRUST` claim states it is not hermetic and not SLSA
   L3 (unless machine-verified) and not complete supply-chain
   security.
6. **Open gaps link the register.** Any `OPEN_GAP` claim links
   `docs/OPEN_STRUCTURAL_GAPS.md`.
7. **Forbidden external-facing phrases fail closed** unless inside an
   explicit `<!-- claims:disclaimer -->` / `<!-- claims:end -->`
   block. The enforced lexicon (definitional list, not an assertion):
<!-- claims:disclaimer -->
   proven intelligence, modelled consciousness, brain-equivalence,
   AGI, biologically faithful, real-world validity proven,
   production ready, product ready, productizable, validates
   neuroscience, proves cognition.
<!-- claims:end -->
8. **README stays lean.** It carries a small Reviewer map and the
   one-sentence citation-scope note — never a long bibliography.
9. **Author notes stay human.** `docs/MANUAL_REVIEW_NOTES.md` (the
   single handcrafted note) is under 900 words, sober, no
   motivational language.
10. **Downgrades are recorded, not silent.** Every deleted or softened
    external-facing wording gets one line in
    `evidence/CLAIM_DOWNGRADE_LEDGER.jsonl`.

## Why a contract and not a guideline

A guideline is reviewer goodwill. A contract is a fail-closed gate in
CI. The difference is the entire point of this repository: the cheap
path of polishing a claim until it reads as true must cost a red
build, not a conversation.
