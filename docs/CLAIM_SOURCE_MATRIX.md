# Claim → Source Matrix

Every important external-facing claim carries a stable ID. A reviewer
resolves each ID to in-repo evidence, a canonical source, an explicit
boundary, or a tracked open gap. Citations only *map* the apparatus to
prior art; they never expand a scientific claim. Machine-checked by
`scripts/check_doc_trust.py`; source IDs resolve against
`evidence/SOURCE_REGISTRY.yaml`.

Classes: `EMPIRICAL_RESULT` · `ENGINEERING_MECHANISM` ·
`GOVERNANCE_MECHANISM` · `REPRODUCIBILITY_CONTRACT` ·
`SUPPLY_CHAIN_TRUST` · `INSPIRATION_ONLY` · `NON_CLAIM_BOUNDARY` ·
`OPEN_GAP`.

<!-- claims:disclaimer -->

| claim_id | exact_claim_text | claim_class | location | evidence_path | source_id | falsifier / downgrade condition | status |
|---|---|---|---|---|---|---|---|
| TRI-CLAIM-001 | The hidden temporal-rupture benchmark is a constructed synthetic instrument, not a real-world task. | ENGINEERING_MECHANISM | docs/SPEC.md S4, README | `src/ctios/env.py`, `docs/SPEC.md` | DATASHEETS_2018 | Params not pinned before run, or claimed as real-world representative. | ACTIVE |
| TRI-CLAIM-002 | Under frozen pre-registered conditions the learned scalar estimator beats a hard-wired and the best naive baseline on post-rupture MAE. | EMPIRICAL_RESULT | docs/SPEC.md S1, evidence/release_gate.md | `evidence/release_gate.md`, frozen `learned 0.8830 < injected 8.0028`, `git tag cti-os-v4-GREEN` | PAGE_HINKLEY_TEST, CUSUM_PAGE_1954 | Loss to injected or best-naive on aggregate or any shift; single-seed-only; leakage; non-reproducible. | ACTIVE |
| TRI-CLAIM-003 | Every RED / negative lineage is preserved as a sealed artifact; no threshold tuned to green. | GOVERNANCE_MECHANISM | docs/reports/LINEAGE_STATE.md | `evidence/NEGATIVE_*`, sha-pinned RED tags, `docs/reports/LINEAGE_STATE.md` | POPPER_FALSIFIABILITY, LAKATOS_RESEARCH_PROGRAMMES, KUHN_PARADIGMS | One RED with no sealed artifact or no reproduction path. | ACTIVE |
| TRI-CLAIM-004 | The redacted hypothesis interface tests claim shape, never mechanism, data, or theorem content. | ENGINEERING_MECHANISM | docs/PRIVATE_RND_PROTOCOL.md | `src/ctios/redacted_io.py`, `examples/indi_redacted_temporal_hypothesis.yaml` | MODEL_CARDS_2019 | A real hypothesis class expressible only by leaking a never-share field. | ACTIVE |
| TRI-CLAIM-005 | A sealed verdict plus evidence ledger — not a narrative — is the artifact of evaluation. | GOVERNANCE_MECHANISM | docs/SYSTEM_CARD.md | `ctios.falsify`, `FALSIFY_<hid>.json`, 12 engine contract tests | POPPER_FALSIFIABILITY | A verdict accepted from prose without a sealed artifact. | ACTIVE |
| TRI-CLAIM-006 | The next experiment is human-gated; nothing auto-runs. | GOVERNANCE_MECHANISM | docs/SYSTEM_CARD.md | `ctios.human_gate`, `ctios.review_cli`, `NEXT_<hid>.yaml` | NIST_AI_RMF_2023 | The loop auto-runs a proposed next experiment. | ACTIVE |
| TRI-CLAIM-007 | A machine-checked lexicon blocks interpretive / claim-boundary inflation. | GOVERNANCE_MECHANISM | claims.yaml, README | `scripts/claims_lint.py`, `tests/test_claims_lexicon.py`, CI | NIST_AI_RMF_2023 | A forbidden assertive term passes CI outside a disclaimer block. | ACTIVE |
| TRI-CLAIM-008 | Supply-chain hardening improves the trust boundary at Build L2 / LEVEL_1; it is not hermetic and not SLSA L3 and does not imply complete supply-chain security. | SUPPLY_CHAIN_TRUST | docs/SLSA_LEVEL_DECLARATION.md, docs/SUPPLY_CHAIN_TRUST.md | `src/ctios/supply_chain_audit.py`, `sbom.spdx.json`, `.github/workflows/release.yml` | SLSA_SPEC, SPDX_SPEC, GITHUB_ARTIFACT_ATTESTATION | An L3 / hermetic / "supply-chain secure" wording without machine-verified mechanism. | ACTIVE |
| TRI-CLAIM-009 | Prediction-error language is an operational inspiration only and does not imply biological fidelity. | INSPIRATION_ONLY | README, docs/SPEC.md, docs/SYSTEM_CARD.md | `src/ctios/agents.py` (scalar `m += gain·error`) | RAO_BALLARD_1999, FRISTON_FREE_ENERGY, KNILL_POUGET_BAYESIAN_BRAIN | Any text asserting neural-equivalence, brain fidelity, or modelled cortex. | ACTIVE |
| TRI-CLAIM-010 | READY / PRODUCTIZABLE is not claimed while any structural gap is OPEN. | NON_CLAIM_BOUNDARY | docs/OPEN_STRUCTURAL_GAPS.md | `ctios.readiness_score`, `ctios.external_validation`, `tests/test_structural_gaps.py` | NIST_AI_RMF_2023 | A READY/productizable wording while a gap is OPEN. | ACTIVE |
| TRI-CLAIM-011 | The falsification engine runs the full loop on any pinned hypothesis without needing the private IP. | ENGINEERING_MECHANISM | docs/SPEC.md S7 | `ctios.falsify`, `tri-falsify` demo GREEN, 12 contract tests | POPPER_FALSIFIABILITY | Battery passes a non-deterministic probe, decorative threshold, or pseudo-GREEN control. | ACTIVE |
| TRI-CLAIM-012 | A scalar-inexpressible benchmark was validated (v8.4); a generic small learner does NOT recover its structure to floor (v9, preserved RED) — domain breadth beyond the synthetic families remains OPEN. | OPEN_GAP | docs/SPEC.md S4/S5, docs/OPEN_STRUCTURAL_GAPS.md GAP_2 | `docs/reports/LINEAGE_STATE.md` (v8.4 GREEN, v9 RED), `evidence/` sealed | LAKATOS_RESEARCH_PROGRAMMES, KALMAN_1960 | Closing GAP_2 without ≥2 sealed independent task-family verdicts. | ACTIVE |

<!-- claims:end -->

## Reading rule

`EMPIRICAL_RESULT` requires an evidence path. `ENGINEERING_MECHANISM`
and `GOVERNANCE_MECHANISM` require a test/script/CI path.
`INSPIRATION_ONLY` carries "does not imply biological fidelity".
`SUPPLY_CHAIN_TRUST` carries the not-hermetic / not-L3 boundary.
`OPEN_GAP` links `docs/OPEN_STRUCTURAL_GAPS.md`. An unsupported claim is
downgraded or deleted and logged in
`evidence/CLAIM_DOWNGRADE_LEDGER.jsonl`.
