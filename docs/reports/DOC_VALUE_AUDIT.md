# Documentation Value Audit (generated)

Generated from `evidence/DOC_TRUST_AUDIT.json` by `scripts/build_doc_trust_audit.py`. Do not hand-edit; edit the trust layer and regenerate.

- claims parsed: **23**
- sources mapped: **16**
- boundary/inspiration claims: **6**
- open gaps referenced: **2**
- downgraded (logged): **3**

## Findings

- Every external-facing claim carries a stable TRI-CLAIM-0NN ID parsed and class-checked by scripts/check_doc_trust.py; no scientific claim is expanded.
- Source registry uses the full schema (id/tier/citation/url/domain/supports_claim_ids/supports_repo_files/allowed_use/forbidden_use/boundary/status) and stays in sync with docs/REFERENCES.md (gate-enforced).
- Prediction-error language is bound INSPIRATION_ONLY with an explicit no-biological-fidelity boundary; supply-chain claims carry the not-hermetic / not-SLSA-L3 ceiling.
- Two structural gaps (independent reproduction, domain breadth) remain OPEN and block READY/PRODUCTIZABLE in code.

## Must not claim

- cognition
- consciousness
- AGI / general intelligence
- biological fidelity / brain equivalence
- real-world validity
- production readiness / productizable
- learned-model superiority
- hermetic or SLSA L3 supply chain
- novelty of falsification, change detection, or online estimation
