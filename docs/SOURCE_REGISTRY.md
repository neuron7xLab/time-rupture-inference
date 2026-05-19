<!-- GENERATED from evidence/SOURCE_REGISTRY.yaml by
     scripts/build_doc_trust_audit.py. Do not hand-edit; edit the YAML
     and regenerate (scripts/build_doc_trust_audit.py --verify-only
     fails closed on drift). -->
# Source Registry (claim-support, not a bibliography)

A source appears here only if it maps to >=1 `claim_id` or repo file.
No prestige padding, no citation laundering. Machine source of truth:
`evidence/SOURCE_REGISTRY.yaml`. Tiers: **CANONICAL** /
**SUPPORTING** / **CONTEXT_ONLY**. Claim numbers are the
`TRI-CLAIM-0NN` suffix in `docs/CLAIM_SOURCE_MATRIX.md`.

| id | tier | domain | supports | boundary |
|---|---|---|---|---|
| POPPER_FALSIFIABILITY | CANONICAL | philosophy_of_science | 006,008,010,013,023 | Workflow-structure justification only; never a correctness warrant. |
| LAKATOS_RESEARCH_PROGRAMMES | CANONICAL | philosophy_of_science | 005,011,017 | Lineage-governance context; not empirical evidence. |
| KUHN_PARADIGMS | CONTEXT_ONLY | philosophy_of_science | 005 | Contrast only; a CONTEXT_ONLY source never supports a positive claim. |
| RAO_BALLARD_1999 | SUPPORTING | predictive_coding | 019,020 | Inspiration only; does not imply biological fidelity. |
| FRISTON_FREE_ENERGY | CONTEXT_ONLY | predictive_coding | 019 | Context only; not operational proof. |
| KNILL_POUGET_BAYESIAN_BRAIN | CONTEXT_ONLY | predictive_coding | 019 | Analogy only. |
| WALSH_PREDICTIVE_PROCESSING_REVIEW_2023 | CONTEXT_ONLY | predictive_coding | 019,020 | Boundary-setting context only. |
| PAGE_HINKLEY_TEST | CANONICAL | change_detection | 001,003,007 | Prior-art acknowledgement; not detector superiority. |
| CUSUM_PAGE_1954 | CANONICAL | change_detection | 001,004 | Disclaims novelty; no empirical result here. |
| KALMAN_1960 | SUPPORTING | online_estimation | 004,005 | Prior-art baseline only. |
| MODEL_CARDS_2019 | CANONICAL | ai_documentation | 002,009,021 | Documentation-structure reference; not correctness. |
| DATASHEETS_2018 | SUPPORTING | ai_documentation | 022 | Reporting standard only; not external validity. |
| NIST_AI_RMF_2023 | SUPPORTING | ai_documentation | 012,013,016,018 | Governance context only; no safety/compliance claim. |
| SLSA_SPEC | CANONICAL | supply_chain | 015 | Exact-level reference; ceiling is Build L2. |
| SPDX_SPEC | CANONICAL | supply_chain | 015 | Artifact-format standard only; not dependency safety. |
| GITHUB_ARTIFACT_ATTESTATION | SUPPORTING | supply_chain | 014,015 | Build-trust mechanism only. |

Full citations, URLs, allowed/forbidden use are in
`evidence/SOURCE_REGISTRY.yaml`; the rendered human bibliography is
`docs/REFERENCES.md`. A source cannot be added unless it maps to at
least one `claim_id` or repo file.
