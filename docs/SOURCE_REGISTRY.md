# Source Registry (claim-support, not a bibliography)

This is not decoration. A source appears here only if it supports a
specific `claim_id` or repo file. No prestige padding, no citation
laundering. The machine-readable source of truth is
`evidence/SOURCE_REGISTRY.yaml`; this page is the human mirror and
`scripts/check_doc_trust.py` fails closed if the two diverge in IDs.

Tiers: **CANONICAL** (load-bearing prior art the apparatus reuses) ·
**SUPPORTING** (maps one mechanism) · **CONTEXT_ONLY** (framing or
contrast, never proof).

| id | tier | domain | supports | bound use | does NOT justify |
|---|---|---|---|---|---|
| POPPER_FALSIFIABILITY | CANONICAL | philosophy of science | 003, 005, 007 | claim→falsifier→evidence→boundary grammar | correctness of any result |
| LAKATOS_RESEARCH_PROGRAMMES | CANONICAL | philosophy of science | 003, 012 | preserved-negative lineage as a programme | that the programme is progressive |
| KUHN_PARADIGMS | CONTEXT_ONLY | philosophy of science | 003 | contrast: anomalies preserved, not absorbed | anything (context only) |
| RAO_BALLARD_1999 | SUPPORTING | predictive coding | 009 | error→update operational analogy | biological fidelity |
| FRISTON_FREE_ENERGY | CONTEXT_ONLY | predictive coding | 009 | broad predictive-processing framing | any repo result |
| KNILL_POUGET_BAYESIAN_BRAIN | CONTEXT_ONLY | predictive coding | 009 | uncertainty-as-driver analogy | a Bayesian-brain claim |
| PAGE_HINKLEY_TEST | CANONICAL | change detection | 002, 012 | the sequential drift trigger (prior art) | detector superiority |
| CUSUM_PAGE_1954 | CANONICAL | change detection | 002 | foundational sequential analysis | any empirical result here |
| KALMAN_1960 | SUPPORTING | online estimation | 012 | anchors the v6 precision-weighting RED | estimator superiority |
| MODEL_CARDS_2019 | CANONICAL | AI documentation | 010 | the system-card reporting structure | safety / correctness |
| DATASHEETS_2018 | SUPPORTING | AI documentation | 001 | documenting a constructed instrument | external validity |
| NIST_AI_RMF_2023 | SUPPORTING | AI documentation | 007, 010 | risk vocabulary for the taxonomy | any safety claim |
| SLSA_SPEC | CANONICAL | supply chain | 008 | the achieved Build L2 definition | L3 / hermeticity |
| SPDX_SPEC | CANONICAL | supply chain | 008 | SBOM as SPDX-2.3 transparency | dependency safety |
| GITHUB_ARTIFACT_ATTESTATION | SUPPORTING | supply chain | 008 | the attestation mechanism | absence of compromise |

Full canonical citations, URLs, allowed/forbidden use, and the
"why this matters" / "what this does not justify" fields are in
`evidence/SOURCE_REGISTRY.yaml`. Each `claim_id` is defined in
`docs/CLAIM_SOURCE_MATRIX.md`.

## Hard rule

A source cannot be added unless it maps to at least one `claim_id` or
repo file. "Because famous" is not a reason. Prediction-error sources
are bound as inspiration with an explicit no-biological-fidelity
boundary; supply-chain sources are bound to an exact trust level with
mandatory not-hermetic / not-L3 wording.
