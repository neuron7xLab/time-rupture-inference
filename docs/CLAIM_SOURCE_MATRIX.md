# Claim → Source Matrix

Every important external-facing claim carries a stable
`TRI-CLAIM-0NN` ID resolving to in-repo evidence, a canonical source,
an explicit boundary, or a tracked open gap. Citations do not expand
scientific claims; they only map boundaries, prior art, and reviewer
context. Machine-parsed by `scripts/check_doc_trust.py`; `source_id`
resolves against `evidence/SOURCE_REGISTRY.yaml`; the human-readable
source page is `docs/REFERENCES.md`.

Classes: `EMPIRICAL_RESULT` · `ENGINEERING_MECHANISM` ·
`GOVERNANCE_MECHANISM` · `REPRODUCIBILITY_CONTRACT` ·
`SUPPLY_CHAIN_TRUST` · `INSPIRATION_ONLY` · `NON_CLAIM_BOUNDARY` ·
`OPEN_GAP`.

<!-- claims:disclaimer -->

| claim_id | exact_claim_text | claim_class | location | evidence_path | source_id | falsifier / downgrade condition | status |
|---|---|---|---|---|---|---|---|
| TRI-CLAIM-001 | The learned scalar agent beats the injected and best-naive baselines on post-rupture MAE under the pinned synthetic benchmark. | EMPIRICAL_RESULT | README, docs/SPEC.md S1 | `evidence/release_gate.md`; `docs/REPRODUCIBILITY_CONTRACT.md` | PAGE_HINKLEY_TEST, CUSUM_PAGE_1954 | Loss to injected/best-naive on aggregate or any shift; single-seed; leakage; non-reproducible. | ACTIVE |
| TRI-CLAIM-002 | The system makes no cognition / AGI / consciousness claim; scope is one synthetic rupture family. | NON_CLAIM_BOUNDARY | README taxonomy card, docs/SYSTEM_CARD.md | `claims.yaml`; `scripts/claims_lint.py` | MODEL_CARDS_2019 | Any scope-expanding wording outside a disclaimer. | ACTIVE |
| TRI-CLAIM-003 | The v4 frozen metrics (learned 0.8830 / injected 8.0028 / oracle 0.7933) are byte-identical across every commit. | EMPIRICAL_RESULT | docs/REPRODUCIBILITY_CONTRACT.md | `evidence/release_gate.md`; `PYTHONPATH=src python -m ctios.runner --mode full` | PAGE_HINKLEY_TEST | Any drift in the frozen numbers; runner fails closed. | ACTIVE |
| TRI-CLAIM-004 | v5 minimal causal-action is opt-in and scope-bounded; not a world model. | NON_CLAIM_BOUNDARY | docs/SPEC.md S2 | `python -m ctios.causal_runner --mode full`; `evidence/` v5 ledger | CUSUM_PAGE_1954, KALMAN_1960 | action_null gap > 0.02 or interventional ≈ logged. | ACTIVE |
| TRI-CLAIM-005 | Every RED / PARTIAL_RED lineage is preserved and reproducible; no threshold tuned to green. | GOVERNANCE_MECHANISM | docs/reports/LINEAGE_STATE.md | `evidence/NEGATIVE_*`; sha-pinned RED tags; `docs/reports/LINEAGE_STATE.md` | LAKATOS_RESEARCH_PROGRAMMES, KUHN_PARADIGMS | One RED with no sealed artifact or no reproduction path. | ACTIVE |
| TRI-CLAIM-006 | Pinned scientific thresholds are never edited after a result (spec sha256 covers them). | GOVERNANCE_MECHANISM | docs/FAILURE_TAXONOMY.md | `HypothesisSpec.sha()`; `tests/` spec-sha mutation test | POPPER_FALSIFIABILITY | A post-hoc threshold edit not detected by the spec sha. | ACTIVE |
| TRI-CLAIM-007 | The agent receives only the realised signal; a no-leakage introspection test enforces it. | ENGINEERING_MECHANISM | docs/SPEC.md S1 | `tests/` no-leakage test; `scripts/claims_lint.py` | PAGE_HINKLEY_TEST | An agent path observing a hidden variable. | ACTIVE |
| TRI-CLAIM-008 | Eight deterministic degenerate probes run fail-closed against the battery over a 7-family portfolio. | ENGINEERING_MECHANISM | docs/SYSTEM_CARD.md PR21 | `ctios.falsifier_stress`; `tests/test_adversarial_probes.py`; CI | POPPER_FALSIFIABILITY | A data-blind probe reaching a clean PASS. | ACTIVE |
| TRI-CLAIM-009 | The redacted hypothesis interface tests claim shape, never mechanism, data, or theorem content. | ENGINEERING_MECHANISM | docs/PRIVATE_RND_PROTOCOL.md | `src/ctios/redacted_io.py`; `examples/indi_redacted_temporal_hypothesis.yaml` | MODEL_CARDS_2019 | A hypothesis class expressible only by leaking a never-share field. | ACTIVE |
| TRI-CLAIM-010 | A sealed verdict, not a narrative, is the artifact of evaluation. | GOVERNANCE_MECHANISM | docs/SYSTEM_CARD.md | `ctios.falsify`; `FALSIFY_<hid>.json`; 12 engine contract tests | POPPER_FALSIFIABILITY | A verdict accepted from prose without a sealed artifact. | ACTIVE |
| TRI-CLAIM-011 | The evidence ledger is append-only; preserved negatives are not erased. | GOVERNANCE_MECHANISM | docs/REPRODUCIBILITY_CONTRACT.md | `evidence/` ledger; `tests/` ledger tests | LAKATOS_RESEARCH_PROGRAMMES | A preserved negative removed or overwritten. | ACTIVE |
| TRI-CLAIM-012 | The next experiment is human-gated; nothing auto-runs. | GOVERNANCE_MECHANISM | docs/SYSTEM_CARD.md | `ctios.human_gate`; `ctios.review_cli`; `NEXT_<hid>.yaml` | NIST_AI_RMF_2023 | The loop auto-running a proposed next experiment. | ACTIVE |
| TRI-CLAIM-013 | A machine-checked lexicon blocks interpretive / claim-boundary inflation in CI. | GOVERNANCE_MECHANISM | claims.yaml, README | `scripts/claims_lint.py`; `tests/test_claims_lexicon.py`; CI | POPPER_FALSIFIABILITY, NIST_AI_RMF_2023 | A forbidden assertive term passing CI outside a disclaimer. | ACTIVE |
| TRI-CLAIM-014 | The provenance manifest binds every source file to a sha256 + SPDX id; drift fails loud. | REPRODUCIBILITY_CONTRACT | docs/PROVENANCE.md | `scripts/provenance_attest.py`; `provenance_manifest.json`; CI | GITHUB_ARTIFACT_ATTESTATION | A source-file hash drift not failing the gate. | ACTIVE |
| TRI-CLAIM-015 | Supply-chain hardening is Build L2 / LEVEL_1: not hermetic, not SLSA L3, not complete supply-chain security. | SUPPLY_CHAIN_TRUST | docs/SLSA_LEVEL_DECLARATION.md, docs/SUPPLY_CHAIN_TRUST.md | `src/ctios/supply_chain_audit.py`; `sbom.spdx.json`; CI | SLSA_SPEC, SPDX_SPEC, GITHUB_ARTIFACT_ATTESTATION | An L3 / hermetic / "secure" wording without a verified mechanism. | ACTIVE |
| TRI-CLAIM-016 | Independent external reproduction is OPEN and caps readiness in code. | OPEN_GAP | docs/OPEN_STRUCTURAL_GAPS.md GAP_1 | `docs/OPEN_STRUCTURAL_GAPS.md`; `ctios.readiness_score` | NIST_AI_RMF_2023 | GAP_1 CLOSED without a valid external proof bundle. | ACTIVE |
| TRI-CLAIM-017 | Domain breadth beyond the synthetic families is OPEN. | OPEN_GAP | docs/OPEN_STRUCTURAL_GAPS.md GAP_2 | `docs/OPEN_STRUCTURAL_GAPS.md`; `docs/reports/LINEAGE_STATE.md` | LAKATOS_RESEARCH_PROGRAMMES | GAP_2 CLOSED without ≥2 sealed independent task-family verdicts. | ACTIVE |
| TRI-CLAIM-018 | No READY / PRODUCTIZABLE claim is admissible while a structural gap is OPEN. | NON_CLAIM_BOUNDARY | docs/OPEN_STRUCTURAL_GAPS.md, docs/VALUE_POSITIONING.md | `ctios.readiness_score`; `tests/test_structural_gaps.py` | NIST_AI_RMF_2023 | A READY/productizable wording while a gap is OPEN (`docs/OPEN_STRUCTURAL_GAPS.md`). | ACTIVE |
| TRI-CLAIM-019 | Prediction-error language is an operational inspiration only and does not imply biological fidelity. | INSPIRATION_ONLY | README, docs/SPEC.md, docs/SYSTEM_CARD.md | `src/ctios/agents.py` (scalar `m += gain·error`) | RAO_BALLARD_1999, FRISTON_FREE_ENERGY, KNILL_POUGET_BAYESIAN_BRAIN, WALSH_PREDICTIVE_PROCESSING_REVIEW_2023 | Any neural-equivalence / modelled-cortex wording. | ACTIVE |
| TRI-CLAIM-020 | The four neuroplasticity-like markers are measured operational quantities; this does not imply biological fidelity. | INSPIRATION_ONLY | README result section | `evidence/release_gate.md` (np markers); ablation-gated | RAO_BALLARD_1999, WALSH_PREDICTIVE_PROCESSING_REVIEW_2023 | A marker asserted as biological neuroplasticity. | ACTIVE |
| TRI-CLAIM-021 | No intelligence / cognition / consciousness / AGI claim is made anywhere. | NON_CLAIM_BOUNDARY | docs/SPEC.md S5, README | `claims.yaml`; `scripts/claims_lint.py`; `tests/test_claims_lexicon.py` | MODEL_CARDS_2019 | Any such assertive term outside a disclaimer block. | ACTIVE |
| TRI-CLAIM-022 | The reproducibility contract is a clean-clone, exact-command, byte-identical-output discipline. | REPRODUCIBILITY_CONTRACT | docs/REPRODUCIBILITY_CONTRACT.md | `bash scripts/conference_smoke.sh`; frozen v4/v5 lines | DATASHEETS_2018 | A documented command not behaving as written on a clean clone. | ACTIVE |
| TRI-CLAIM-023 | A generalized falsification engine runs the full loop on any pinned hypothesis without the private IP. | ENGINEERING_MECHANISM | docs/SPEC.md S7 | `ctios.falsify`; `tri-falsify` demo GREEN; 12 contract tests | POPPER_FALSIFIABILITY | Battery passing a non-deterministic probe / decorative threshold / pseudo-GREEN control. | ACTIVE |

<!-- claims:end -->

## Reading rule

`EMPIRICAL_RESULT` requires an evidence path. `ENGINEERING_MECHANISM`
and `GOVERNANCE_MECHANISM` require a test/script/CI path.
`REPRODUCIBILITY_CONTRACT` requires a runnable command.
`INSPIRATION_ONLY` carries "does not imply biological fidelity".
`SUPPLY_CHAIN_TRUST` carries the not-hermetic / not-SLSA-L3 boundary.
`OPEN_GAP` links `docs/OPEN_STRUCTURAL_GAPS.md`. An unsupported claim
is downgraded or deleted and logged in
`evidence/CLAIM_DOWNGRADE_LEDGER.jsonl`.
