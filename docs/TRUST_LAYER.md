# Trust Layer

TRI-Falsify does not ask a reviewer to believe a narrative. It asks
the reviewer to inspect a claim boundary, run a reproduction path,
inspect sealed evidence, and verify that unsupported claims are either
blocked, downgraded, or explicitly marked as open.

This document describes the repository as a trust architecture, not a
project description. Each surface below names what is mechanically
enforced and what remains trust-based — stated, not hidden.

## 1. Trust surface

What a reviewer must trust vs. what is checked. Checked: claim
lexicon, frozen numbers, spec hashes, provenance hashes, workflow SHA
pins, dependency lock, SBOM/lock parity, verifier manifest. Still
trust-based: that the synthetic benchmark is a meaningful instrument,
that the author redacted the private hypothesis faithfully, and that
exempt internal docs are classified honestly.

## 2. Evidence surface

Evidence is an artifact, not a sentence: sealed `FALSIFY_<hid>.json`,
preserved `NEGATIVE_*` with a reproduction command, the byte-identical
frozen runner outputs, and `provenance_manifest.json`. Entry points:
[`evidence/release_gate.md`](../evidence/release_gate.md),
[`docs/reports/LINEAGE_STATE.md`](reports/LINEAGE_STATE.md).

## 3. Claim surface

Every major external-facing claim has a stable ID with a class,
evidence path, source, and falsifier:
[`docs/CLAIM_SOURCE_MATRIX.md`](CLAIM_SOURCE_MATRIX.md). Interpretive
inflation is blocked by [`claims.yaml`](../claims.yaml) +
[`scripts/claims_lint.py`](../scripts/claims_lint.py) in CI and pytest.

## 4. Source surface

Citations map the apparatus to prior art and clarify boundaries; they
do not expand a scientific claim. Source-of-truth:
[`evidence/SOURCE_REGISTRY.yaml`](../evidence/SOURCE_REGISTRY.yaml),
mirror [`docs/SOURCE_REGISTRY.md`](SOURCE_REGISTRY.md), boundaries
[`docs/PRIOR_ART_BOUNDARY_MAP.md`](PRIOR_ART_BOUNDARY_MAP.md).

## 5. Reproducibility surface

Clean clone → exact commands → byte-identical frozen numbers; drift
fails closed. Contract:
[`docs/REPRODUCIBILITY_CONTRACT.md`](REPRODUCIBILITY_CONTRACT.md).

## 6. Supply-chain surface

Workflow SHA pins, pinned dependency lock (LEVEL_1, not hash-locked),
release Build L2 attestation (not SLSA L3), SPDX-2.3 SBOM, fail-closed
aggregate. Honest level and explicit non-claims:
[`docs/SUPPLY_CHAIN_TRUST.md`](SUPPLY_CHAIN_TRUST.md).

## 7. Open-gap surface

Independent reproduction and domain breadth are OPEN; a
READY/PRODUCTIZABLE claim is not admissible while either gap is open
([`docs/OPEN_STRUCTURAL_GAPS.md`](OPEN_STRUCTURAL_GAPS.md)). A gap may
not become CLOSED without a committed evidence file.

## 8. Human-review surface

Nothing auto-runs. A non-GREEN outcome writes a proposed next
experiment and stops; `human_review_required: true` is mandatory in a
redacted skeleton or it is rejected.

## 9. What fails closed

Forbidden assertive vocabulary outside a disclaimer block; a frozen
number drifting; an edited threshold (spec sha changes); an unattested
file; a loose CI install; an unpinned workflow ref; SBOM/lock
divergence; a missing source mapping; a CLOSED gap without evidence; a
READY claim while a gap is OPEN; an `INSPIRATION_ONLY` claim without
its biological-fidelity boundary. Each is a specific test or gate,
listed in [`docs/FAILURE_TAXONOMY.md`](FAILURE_TAXONOMY.md) and
enforced by [`scripts/check_doc_trust.py`](../scripts/check_doc_trust.py).

## 10. What remains trust-based

The synthetic benchmark's external meaning; the faithfulness of a
private redaction; the honesty of the exempt-doc classification; and
external originality of the underlying ideas (OPEN, never asserted).
These are the residual trust assumptions — a reviewer should attack
exactly here.

Audit summary: [`evidence/DOC_TRUST_AUDIT.json`](../evidence/DOC_TRUST_AUDIT.json).
