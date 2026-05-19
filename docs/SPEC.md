# time-rupture-inference — Formal Specification

Audience: an external evaluator. Every capability
is stated as **Claim → Falsifier → Evidence → Boundary**. Inverse
argumentation: a claim is admitted only because its falsifier was run
and did not trigger; the evidence is a reproducible artifact, not prose.
<!-- claims:disclaimer -->
No capability/cognition/AGI language — the repository's own
`claims-lint` enforces this.
<!-- claims:end -->

## 0. System identity (what it IS)

A falsification-first **temporal-inference apparatus** plus a runnable
**online adaptive agent**.
<!-- claims:disclaimer -->
It is NOT a cognitive system, neural-network
intelligence, or AGI; the dominant product is a chain of sealed
negatives + the infrastructure that produces them honestly.
<!-- claims:end -->
Two narrow positives survive (S1, S5).

## 1. Formal object

Hidden inter-event interval `τ(t)` with a regime rupture: `τ = τ₀` for
`t < T*`, `τ = τ₁` for `t ≥ T*`. Observation `o(t) = τ(t) + N(0,σ)`.
The agent receives only `o(t)` (never `τ₀, τ₁, T*, σ`) and must infer
the regime from its **own prediction error**. v8.x adds a hidden binary
context `z` aliasing identical observation windows to opposite futures.

## 2. Value functions (what the system optimises, onto inference)

| V | function | enforced by |
|---|---|---|
| V1 falsifiability | every claim has a pre-registered kill-test | `prereg/*`, pinned-before-run |
| V2 closure-before-restart | a failed lineage is sealed before the next opens | `evidence/NEGATIVE_RESULT_*`, git tags |
| V3 no-tuning | thresholds never edited after results | byte-identical `prereg_hash` v2→v4 |
| V4 frozen-invariant | a proven number cannot silently move | v4 `0.8830/8.0028/0.7933` byte-identical across all commits |
| V5 claim-boundary | text cannot exceed the implemented mechanism | `claims.yaml` + CI lint |
| V6 reproducibility | clean-clone re-run + provenance | `provenance_manifest.json`, deterministic replay hashes |
| V7 verdict-isolation | a legitimate RED keeps CI green | diagnostics are research lineages, not CI gates |

## 3. Capabilities (Claim → Falsifier → Evidence → Boundary)

### S1 — Prediction-error temporal adaptation (SURVIVING POSITIVE)
- **Claim.** A learner that infers the interval from its own error beats
  a hard-wired and the best naive baseline post-rupture.
- **Falsifier.** Lose to injected OR to best-naive on aggregate, or on
  any shift, or single-seed-only, or via leakage, or non-reproducible.
- **Evidence.** 30 seeds × 3 shifts: `learned 0.8830 < injected 8.0028`,
  win-rate 1.000 vs injected & best-naive on every shift; ablation
  proves the drift mechanism necessary; no-leakage introspection;
  deterministic replay. `git tag cti-os-v4-GREEN`, released `v0.1.0`.
- **Boundary.** A scalar adaptive estimator on a synthetic rupture.
  Explicitly not cognition. Oracle floor 0.7933 → 11% residual regret.

### S2 — Minimal causal-action (BOUNDED POSITIVE)
- **Claim.** Acting changes post-shift error only when actions causally
  modify the transition (interventional), not when merely logged.
- **Falsifier.** action_null gap > 0.02, or interventional ≈ logged.
- **Evidence.** `causal_action_gain 0.868`, `action_null_gap 0.000`,
  win 1.000/1.000 (PR #1). Opt-in; v4 path unchanged.
- **Boundary.** Predictive→causal on a synthetic family; not a world
  model.

### S3 — Falsification governance (THE PRIMARY ASSET)
- **Claim.** The apparatus makes inflation and silent pseudo-GREEN
  structurally impossible.
- **Falsifier.**
  <!-- claims:disclaimer -->
  A magic-literal/window drift, a cognition claim outside
  a disclaimer, an unattested file, a verdict tuned to green — any
  passes CI.
  <!-- claims:end -->
- **Evidence.** single-source `ctios.contract`; AST gate "every
  post-shift slice calls validate_window"; `claims.yaml`+`claims_lint`
  (planted-violation test); `provenance_attest` (sha256 + SPDX, external
  scan honestly OPEN); 150 tests; lineage `v1🔴 v2🟢 v3🔴 v4🟢 v5🟢
  v6🔴 v7🔴 v8🔴 v8.1🔴 v8.2🟠 v8.3🟥 v8.4🟢 v9🔴` — all preserved.
- **Boundary.** Governance, not truth-generation.

### S4 — Validated scalar-inexpressible benchmark (CONSTRUCTED INSTRUMENT)
- **Claim.** v8.4 is a task where a scalar is provably insufficient and
  the causal floor is reachable.
- **Falsifier.** analytic `h2r_causal_min > 0.35` (gate unattainable),
  or empirical ≫ analytic, or tc/cc < pinned.
- **Evidence.** pre-run proof `h2r_causal_min=0.1588 ≤ 0.35`; empirical
  `h2r=0.1851` at the causal optimum; `tc=0.882, cc=0.882`. The v8→v8.3
  negatives localised this boundary; gates byte-identical v8.2→v8.4.
- **Boundary.** A validated task property, not a capability.

### S5 — Negative of record: generic learner ≠ recovery (PRESERVED RED)
- **Claim (null held).** A small online recurrent learner does NOT
  recover the v8.4 structure to floor though it is provably discoverable.
- **Evidence.** v9: learned warm-trigger 5.92 vs scalar 7.98 (beats
  +26%) but `h2r 6.47 ≫ 0.35`, oracle floor 0.19. `discoverable ≠
  recovered`, quantified, preserved.
- **Boundary.** Statement about this learner class on this benchmark;
  not "models cannot".

### S6 — Runnable online adaptive agent (ENGINEERING ARTIFACT)
- **Claim.** `tri-agent` runs on an arbitrary numeric stream, adapts
  online, flags a regime shift.
- **Falsifier.** Non-deterministic, non-finite, or misses the synthetic
  shift.
- **Evidence.** SDK `TemporalAgent` + CLI; demo/echo_state 600 steps
  detected the hidden shift at step 301 (true 300); 5 contract tests.
- **Boundary.** A stream tool; measured hard-task capability modest (S5).

### S7 — Generalized falsification engine (THE REUSABLE PRIMITIVE)
- **Claim.** `ctios.falsify` runs the full loop on ANY pinned
  hypothesis: theorem (claim/null) + assumptions + variables + falsifier
  checks + Probe → adversarial battery → sealed verdict → auto-proposed
  next experiment.
- **Falsifier.** Battery does not catch a non-deterministic probe, a
  decorative (non-load-bearing) threshold, or a pseudo-GREEN negative
  control; or a tuned threshold is not detected by the spec sha.
- **Evidence.** `tri-falsify` demo GREEN with all 5 gates incl
  `thresholds_load_bearing` + `negative_control_fails`; assumptions &
  variables are part of the pinned `spec_sha256`; non-GREEN auto-emits a
  decision-gated `NEXT_*.yaml` (surviving checks tightened ×0.9, failed
  boundary = focus, assumptions demoted to open questions). 12 engine
  contract tests. Private hypotheses plug in locally as a `Probe`; the
  engine never needs the IP.
- **Boundary.** A discipline primitive that prevents self-deception; it
  does not generate truth, and it never auto-runs the next experiment.

### S8 — Change-detection arc (THE DISCIPLINE APPLIED TO ITSELF)

- **Claim.** A held-out-null-calibrated two-window contrast detects a
  hidden regime rupture from the observation alone — established by a
  six-experiment pinned arc, not a single run.
- **Falsifier.** Any threshold edited after a result; a GREEN whose
  negative control passes; a detect-everything fake reaching a clean
  pass; the shared primitive drifting a sealed number.
- **Evidence.** `RED RED GREEN PARTIAL GREEN PARTIAL` (#24–#29), every
  falsifier pinned before its run, every verdict sealed
  (`docs/reports/*`); the distilled primitive `ctios.change_detection`
  reproduces all sealed numbers byte-identically (guarded);
  `ctios.change_detection_arc` runs the whole arc in one command.
- **Boundary.** Synthetic families only. One characterized open
  residual (a location statistic cannot separate a stationary bimodal
  mixture from a shift). No generalization or real-world claim.

## 4. Inverse argument (why the surviving claims stand)

S1 would be false if a scalar heuristic were not near-oracle — it is
(v7 NO_HEADROOM: heuristic within 14% of oracle), so S1 is scoped to
*adaptation*, not superiority of representation. S4 would be false if
the floor were unattainable — v8.3 proved the prior gate WAS
unattainable and v8.4 re-derived params with the floor proven ≤ gate
*before* running. S5 stands precisely because S4 proved the structure
discoverable, so a learner failing it is informative, not ambiguous.

## 5. Non-claims (hard scope)

<!-- claims:disclaimer -->
No intelligence, cognition, consciousness, neuroplasticity, AGI,
world-model, or learned-model-superiority claim is made anywhere. No
biological fidelity. External plagiarism/originality: OPEN, not
asserted. Generality beyond the synthetic families: untested.
<!-- claims:end -->

## 6. Reproduction (clean clone)

```
pip install -e ".[dev]"
PYTHONPATH=src pytest tests -q                 # 150 tests
PYTHONPATH=src python -m ctios.runner --mode full   # v4 frozen GREEN
PYTHONPATH=src python -m ctios.causal_runner --mode full   # v5
python scripts/run_v8_4_rederived_diagnostic.py     # S4 GREEN
python scripts/run_v9_learned_diagnostic.py         # S5 preserved RED
PYTHONPATH=src python -m ctios.agent_cli --demo     # S6 agent
```
See `docs/reports/LINEAGE_STATE.md` for the canonical state.
