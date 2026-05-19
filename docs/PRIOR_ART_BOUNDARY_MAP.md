# Prior-Art Boundary Map

Purpose: prevent *both* underclaiming and overclaiming. For each row
the framing is fixed: **the prior art establishes X; this repository
reuses X; the repo-specific integration is Y; this does not justify
Z.** No "world first", no novelty of method, no heroic language.

<!-- claims:disclaimer -->

| claim_id | prior-art domain | established before this repo | reused by this repo | repo-specific integration | not claimed | falsifier / boundary |
|---|---|---|---|---|---|---|
| TRI-CLAIM-003 | Falsifiability (Popper) | Demarcation by refutability | Pre-pinned kill-test gates every admitted claim | Hash-pinned spec + CI lint make refutation mechanical | That any result is true; falsifiability ≠ correctness | A claim admitted without a pinned falsifier that ran |
| TRI-CLAIM-003 | Research programmes (Lakatos) | Progressive vs degenerate programmes | v1..v9 kept as one sealed lineage | Closure-before-restart enforced by tags + artifacts | That the programme is progressive | A RED with no sealed artifact or reproduction path |
| TRI-CLAIM-009 | Prediction error / predictive coding | Error-driven adaptation in perception | error→update loop as an operational analogy | A scalar estimator, ablation-gated, on a synthetic rupture | Biological fidelity, neural-equivalence, modelled cortex | Any neural-equivalence wording outside a disclaimer |
| TRI-CLAIM-002 | Sequential change detection | CUSUM / Page-Hinkley | The drift trigger is a Page-Hinkley-class statistic | Trigger fused into a fail-closed falsifier loop | Novelty in change detection itself | Detector beaten by a naive baseline on the frozen grid |
| TRI-CLAIM-012 | Online recursive estimation | Kalman filtering | v6 RED tested precision-weighting; it did not win | The negative is anchored to named prior art, not a strawman | Improvement over Kalman-class estimation | v6 reinterpreted as a positive |
| TRI-CLAIM-010 | Model / system documentation | Model Cards, Datasheets | System-card structure for an apparatus | Card fields bound to machine-checked gaps | That documentation implies validation | A READY claim while a gap is OPEN |
| TRI-CLAIM-007 | Reproducible CI / clean-clone | Reproducible builds, AI RMF | Clean-clone contract + frozen outputs | Drift fails closed; lint blocks inflation | That reproduction implies real-world validity | A frozen number changing silently and CI staying green |
| TRI-CLAIM-008 | SBOM / SPDX | SPDX 2.3 / ISO 5962 | SBOM emitted as SPDX-2.3 from the pinned lock | SBOM drift vs lock is a fail-closed gate | Dependency safety or hash-locking | An SBOM that diverges from the lock and CI staying green |
| TRI-CLAIM-008 | SLSA / provenance / attestation | SLSA L1–L4; GitHub attestations | Build L2 via artifact attestation | Gate-before-attest order machine-audited | SLSA L3, hermeticity, supply-chain security | An L3/hermetic wording without a verified mechanism |
| TRI-CLAIM-006 | Human-gated research workflows | Human-in-the-loop governance | Non-GREEN writes a proposal and stops | `human_review_required: true` mandatory in skeleton | Autonomous research capability | The loop auto-running a next experiment |
| TRI-CLAIM-004 | Redacted / private evaluation | Differential-privacy-style redaction patterns | Opaque-probe API; never-share field list | Forbidden-key fail-closed at load | That redaction proves the hidden claim | A hypothesis class expressible only by leaking a field |
| TRI-CLAIM-003 | Preserved negative-result governance | Registered reports, held-out controls | Every RED sealed; pseudo-GREEN control required to fail | Discrimination of the gate is itself tested | That negatives are truth-generating | A negative control that also passes |

<!-- claims:end -->

## How to attack this map

A reviewer should test the **not claimed** column directly: edit a
doc to assert one of those forbidden positions and confirm
`scripts/claims_lint.py` or `scripts/check_doc_trust.py` fails closed
(Track D in `docs/REVIEW_PATH.md`). The map is only as honest as the
gate that enforces it.
