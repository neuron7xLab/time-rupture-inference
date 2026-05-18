# Audit: "Доказова часова адаптація без інфляції"

Date: 2026-05-18 (UTC)
Scope: full repository static + test audit

## One-sentence problem statement
Ensure adaptive interval learning remains evidence-grounded, reproducible, and resistant to metric/claim inflation under distribution shifts.

## Findings and debt status

### Closed in this patch
1. **Hyperparameter contract debt (P1)**
   - `LearnedAgent` accepted out-of-range gains/scales and negative horizons without explicit failure.
   - **Fix:** constructor guards now enforce valid ranges and fail fast with `ValueError`.

2. **Single-seed validation fragility (P1)**
   - Anti-divergence regression test relied on a single deterministic seed, vulnerable to accidental pass/fail inversion.
   - **Fix:** regression now evaluates a seed set and compares median late-regime peak error (robust central tendency).

3. **Type-contract debt (P1, added)**
   - `mypy --strict` was not met (16 errors). **Fix:** full annotation pass; strict enforced via `[tool.mypy]` + CI on 3.11/3.12.

### Deliberate deviation from the proposed patch (integrity)
- The proposed patch defaulted `anti_divergence=True`. That changes the
  `LearnedAgent` update law and would have **silently mutated the frozen,
  tagged, released v4 number** (`0.8830`) — exactly the silent-baseline-
  drift / pseudo-GREEN class eliminated in prior cycles. **Resolution:**
  the mechanism is implemented but defaults **OFF**; it is opt-in and
  must earn its place through its own pre-registered improvement lineage,
  not by folding into the frozen baseline. Frozen v4 attestation holds.

### Closed in the v0.1.1 production cycle
4. **Config/logic separation debt (P2) — CLOSED**
   - `anti_divergence` / `min_gain_scale` surfaced in `configs/agents.yaml`;
     `test_governance_surface` asserts code default == YAML (single source).
5. **Artifact contract debt (P3) — CLOSED**
   - `invariants.yaml` machine-readable register added; test asserts every
     `enforced_by` reference resolves to a real gate/test file.

6. **Property-based stress debt (P2) — CLOSED**
   - `tests/test_property_bounded_adaptation.py`: universally-quantified
     property over a deterministically-sampled slice of the manifold
     (shift × noise × warmup × seed) asserts `post_shift_mae <= 2.0·sigma`
     for every combo. Zero new dependency (deterministic rng sweep, not
     Hypothesis). BOUND derived from a 120-combo calibration (worst
     observed 1.089) with ~1.8x safety envelope — a real invariant, not
     tuned-to-pass.

### Still open
- None. All audit P-items (P0/P1/P2/P3) and listed debts are CLOSED.
  Residual scientific frontiers (causal world-model, larger confounder
  matrix) are future *lineages*, not debt — they have their own
  pre-registration discipline, not a backlog entry.

## Checklist mapping (condensed)
- PRE-WORK: mostly satisfied; explicit falsifier contracts exist in `prereg/`.
- MATH: partially satisfied; numeric validation exists via tests, but magic thresholds still largely heuristic.
- IMPLEMENTATION: improved (constructor contract + strict typing + less fragile tests).
- VALIDATION: improved with multi-seed adversariality.
- FALSIFICATION: partial; negative results documented, but broader confounder matrix can expand.
- ARTIFACT/GOVERNANCE: good evidence trail; recommend adding invariants artifact (P3, open).
