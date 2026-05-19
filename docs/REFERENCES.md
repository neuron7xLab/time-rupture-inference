# References

Not decoration. Every entry maps to a `TRI-CLAIM-0NN` in
`docs/CLAIM_SOURCE_MATRIX.md` and to a record in
`evidence/SOURCE_REGISTRY.yaml` (the machine source of truth;
`scripts/check_doc_trust.py` fails closed if a registry source is
missing here, or vice-versa). A source that supports nothing is
removed, not kept for prestige. Schema per entry: **Canonical
citation · Scope · Why it matters here · What it does NOT justify ·
Repo files linked · Claim boundary · Status**.

## A. Philosophy of science / falsification

### POPPER_FALSIFIABILITY
- Canonical citation: Popper, K. R. (1959/2002). *The Logic of Scientific Discovery*. Routledge.
- Scope: Falsifiability as demarcation.
- Why it matters here: Grounds the claim→falsifier→evidence→boundary admission grammar.
- What it does NOT justify: That any result is true; falsifiability ≠ correctness.
- Repo files linked: `docs/SPEC.md`, `claims.yaml`, `prereg/`.
- Claim boundary: Workflow-structure justification only.
- Status: CANONICAL

### LAKATOS_RESEARCH_PROGRAMMES
- Canonical citation: Lakatos, I. (1970). *Falsification and the Methodology of Scientific Research Programmes*. Cambridge University Press.
- Scope: Progressive/degenerate research-programme lineage.
- Why it matters here: Frames the preserved v1..v9 lineage as one programme.
- What it does NOT justify: That the programme is progressive.
- Repo files linked: `docs/reports/LINEAGE_STATE.md`, `evidence/`.
- Claim boundary: Lineage-governance context.
- Status: CANONICAL

### KUHN_PARADIGMS
- Canonical citation: Kuhn, T. S. (1962/1970). *The Structure of Scientific Revolutions*. University of Chicago Press.
- Scope: Paradigm shift; contrast only.
- Why it matters here: Marks what the apparatus refuses — anomalies preserved, not absorbed.
- What it does NOT justify: Anything; a CONTEXT_ONLY source never supports a positive claim.
- Repo files linked: `docs/reports/LINEAGE_STATE.md`.
- Claim boundary: Contrast only.
- Status: CONTEXT_ONLY

## B. Prediction-error / neuroscience inspiration

### RAO_BALLARD_1999
- Canonical citation: Rao, R. P. N. & Ballard, D. H. (1999). Predictive coding in the visual cortex. *Nature Neuroscience*, 2(1), 79-87.
- Scope: Predictive-coding / prediction-error framing.
- Why it matters here: The error→update analogy is borrowed from this lineage.
- What it does NOT justify: Biological fidelity, neural-equivalence, modelled cortex.
- Repo files linked: `README.md`, `docs/SPEC.md`, `src/ctios/agents.py`.
- Claim boundary: Inspiration only; does not imply biological fidelity.
- Status: SUPPORTING

### FRISTON_FREE_ENERGY
<!-- claims:disclaimer -->
- Canonical citation: Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127-138.
<!-- claims:end -->
- Scope: Broad predictive-processing / free-energy context.
- Why it matters here: Situates prediction-error language in a known theoretical family.
- What it does NOT justify: Any repo result.
- Repo files linked: `docs/MANUAL_REVIEW_NOTES.md`.
- Claim boundary: Context only, never direct support.
- Status: CONTEXT_ONLY

### KNILL_POUGET_BAYESIAN_BRAIN
<!-- claims:disclaimer -->
- Canonical citation: Knill, D. C. & Pouget, A. (2004). The Bayesian brain: the role of uncertainty in neural coding and computation. *Trends in Neurosciences*, 27(12), 712-719.
<!-- claims:end -->
- Scope: Uncertainty as the inference driver.
- Why it matters here: Context for treating error/uncertainty as the adaptation signal.
- What it does NOT justify: A Bayesian-brain claim.
- Repo files linked: `docs/PRIOR_ART_BOUNDARY_MAP.md`.
- Claim boundary: Analogy only.
- Status: CONTEXT_ONLY

### WALSH_PREDICTIVE_PROCESSING_REVIEW_2023
- Canonical citation: Walsh, K. S., McGovern, D. P., Clark, A. & O'Connell, R. G. (2023). Evaluating the neurophysiological evidence for predictive processing as a model of perception. *Annals of the New York Academy of Sciences*, 1524(1), 6-33.
- Scope: Modern review bounding how far predictive-processing evidence reaches.
- Why it matters here: Anchors the cautious "inspiration, not evidence" wording to a current review.
- What it does NOT justify: That predictive coding — or this estimator — is a validated model of perception.
- Repo files linked: `docs/MANUAL_REVIEW_NOTES.md`, `docs/REFERENCES.md`.
- Claim boundary: Boundary-setting context only.
- Status: CONTEXT_ONLY

## C. Online change detection / adaptation

### PAGE_HINKLEY_TEST
- Canonical citation: Hinkley, D. V. (1971). Inference about the change-point from cumulative sum tests. *Biometrika*, 58(3), 509-523.
- Scope: Sequential change-point inference.
- Why it matters here: The drift trigger is a Page-Hinkley-class statistic (prior art, reused).
- What it does NOT justify: Detector superiority or generalization beyond the synthetic families.
- Repo files linked: `src/ctios/drift.py`, `src/ctios/change_detection.py`.
- Claim boundary: Prior-art acknowledgement.
- Status: CANONICAL

### CUSUM_PAGE_1954
- Canonical citation: Page, E. S. (1954). Continuous Inspection Schemes. *Biometrika*, 41(1/2), 100-115.
- Scope: Foundational CUSUM / sequential analysis.
- Why it matters here: Establishes that sequential detection long predates this repo.
- What it does NOT justify: Any empirical result here.
- Repo files linked: `src/ctios/change_detection.py`.
- Claim boundary: Disclaims novelty.
- Status: CANONICAL

### KALMAN_1960
- Canonical citation: Kalman, R. E. (1960). A New Approach to Linear Filtering and Prediction Problems. *Journal of Basic Engineering*, 82(1), 35-45.
- Scope: Online recursive estimation.
- Why it matters here: Anchors the v6 precision-weighting RED to named prior art.
- What it does NOT justify: Any estimator-superiority claim; v6 RED shows the opposite.
- Repo files linked: `docs/reports/LINEAGE_STATE.md`.
- Claim boundary: Prior-art baseline only.
- Status: SUPPORTING

## D. AI documentation / evaluation

### MODEL_CARDS_2019
- Canonical citation: Mitchell, M. et al. (2019). Model Cards for Model Reporting. *Proc. FAT* '19*, 220-229. arXiv:1810.03993.
- Scope: Structured reporting of intended use and limits.
- Why it matters here: `docs/SYSTEM_CARD.md` adopts this structure.
- What it does NOT justify: That a card implies correctness, safety, or readiness.
- Repo files linked: `docs/SYSTEM_CARD.md`.
- Claim boundary: Documentation-structure reference.
- Status: CANONICAL

### DATASHEETS_2018
- Canonical citation: Gebru, T. et al. (2018/2021). Datasheets for Datasets. *Communications of the ACM*, 64(12), 86-92. arXiv:1803.09010.
- Scope: Documenting a constructed instrument's provenance and scope.
- Why it matters here: The synthetic rupture family is a constructed instrument documented in datasheet spirit.
- What it does NOT justify: External validity of the synthetic family.
- Repo files linked: `docs/SPEC.md`, `docs/REPRODUCIBILITY_CONTRACT.md`.
- Claim boundary: Reporting standard only.
- Status: SUPPORTING

### NIST_AI_RMF_2023
- Canonical citation: NIST (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1.
- Scope: Risk map/measure/manage vocabulary.
- Why it matters here: Aligns the failure taxonomy and open-gap governance to an external risk vocabulary.
- What it does NOT justify: Any safety, assurance, compliance, or deployment claim.
- Repo files linked: `docs/FAILURE_TAXONOMY.md`, `docs/OPEN_STRUCTURAL_GAPS.md`.
- Claim boundary: Governance context only.
- Status: SUPPORTING

## E. Software supply chain / reproducibility / trust

### SLSA_SPEC
- Canonical citation: OpenSSF (2023). *Supply-chain Levels for Software Artifacts (SLSA)*, specification v1.0.
- Scope: Build-integrity levels and provenance.
- Why it matters here: Defines the achieved Build L2 (GitHub artifact attestation).
- What it does NOT justify: SLSA L3, hermeticity, or end-to-end supply-chain trust.
- Repo files linked: `docs/SLSA_LEVEL_DECLARATION.md`, `.github/workflows/release.yml`.
- Claim boundary: Exact-level reference; ceiling is Build L2.
- Status: CANONICAL

### SPDX_SPEC
- Canonical citation: Linux Foundation (2021). *SPDX Specification v2.3*; ISO/IEC 5962:2021.
- Scope: SBOM metadata standard.
- Why it matters here: The SBOM is emitted as SPDX-2.3 derived from the pinned lock.
- What it does NOT justify: Dependency safety, hash-locking, or hermeticity.
- Repo files linked: `scripts/generate_sbom.py`, `sbom.spdx.json`.
- Claim boundary: Artifact-format standard only.
- Status: CANONICAL

### GITHUB_ARTIFACT_ATTESTATION
- Canonical citation: GitHub (2024). *Using artifact attestations to establish provenance for builds*. GitHub Docs.
- Scope: CI artifact provenance attestation.
- Why it matters here: The concrete mechanism behind the Build L2 step.
- What it does NOT justify: That the build is free of compromise.
- Repo files linked: `.github/workflows/release.yml`, `docs/RELEASE_VERIFICATION.md`.
- Claim boundary: Build-trust mechanism only.
- Status: SUPPORTING

---

Scientific claims are not expanded by citation. Every line above
either bounds a claim or disclaims novelty; none grants correctness.
