# Provenance & Originality Attestation (audit P1 #3)

Honest two-layer split. The internal layer is **CLOSED and enforced**;
the external layer is **OPEN and explicitly not claimed** — silence here
would itself be the pseudo-validity the audit warns about.

## Layer 1 — internal integrity & license (CLOSED, gated)

- Every source file carries `SPDX-License-Identifier: MIT`.
- `provenance_manifest.json` pins a sha256 for every source/config/doc
  artifact under `scripts/provenance_attest.py`.
- `python scripts/provenance_attest.py` fails loud (exit 1) on hash
  drift, an unattested file, a missing referenced file, or a `.py`
  without an SPDX header.
- Enforced in pytest (`tests/test_provenance.py`) and CI.

Closes: license clarity, tamper-evidence, file-level provenance.

## Layer 2 — external similarity / plagiarism scan (OPEN, NOT claimed)

**Status: OPEN.** A true plagiarism determination requires comparison
against external corpora (arXiv, GitHub, the web). This was **not
performed** — the working environment is offline. No "no-plagiarism"
conclusion is asserted anywhere; the manifest records this status
verbatim and the test asserts it stays OPEN (it cannot be silently
flipped to closed).

Documented procedure for when an online environment is available:

1. Code: run a clone/similarity scanner (e.g. MOSS / `jscpd`) over
   `src/` against a public-corpus index; attach the report hash.
2. Text: run a similarity scan of `README.md` + `docs/*.md` against
   arXiv/web; attach top-k matches + scores.
3. Provenance: emit SPDX SBOM + sign the manifest; record scanner
   versions and corpus snapshot date in the evidence ledger.
4. Gate: similarity above a pre-registered threshold blocks release.

Until step 1–4 run, the originality claim scope is: **license-clean,
tamper-evident, internally original by construction of the lineage
history — external originality undetermined.**
