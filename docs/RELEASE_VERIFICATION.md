# Release Verification

Every release asset carries a GitHub build-provenance attestation
(SLSA Build L2 — see `docs/SLSA_LEVEL_DECLARATION.md`).

## Verify an asset

```
gh attestation verify <downloaded-asset> \
  --repo neuron7xLab/time-rupture-inference
```

Expect: attestation found, certificate identity = this repo's release
workflow, subject digest = the asset digest. Any mismatch ⇒ reject the
artifact.

## Verify the SBOM

`sbom.spdx.json` (SPDX-2.3) is attached to the release and is
deterministically generated from `requirements-ci.lock`:

```
python scripts/generate_sbom.py --verify-only
```

## What verification proves / does not prove

Proves: the asset was built by THIS repo's release workflow at a
recorded commit (origin authenticity + integrity). Does NOT prove the
code is vulnerability-free, the build is hermetic, or SLSA > L2.
