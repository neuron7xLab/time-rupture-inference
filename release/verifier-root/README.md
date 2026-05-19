# Verifier Root (independent, exportable)

A reviewer copies **this directory** out of the repository and uses it
to check whether the repo's critical verifier files were silently
weakened. It does not trust the repo to verify itself.

## Why this exists

Every internal audit in the repo is run by scripts *inside* the repo.
A malicious change could edit both the target code and its verifier
and keep CI green (verifier capture). This root breaks that loop: the
expected verifier hashes are pinned here, and the checker is
stdlib-only and does not import the package it verifies.

## Use (outside the repo, stdlib Python 3 only)

```bash
cp -r release/verifier-root /somewhere/outside
cd /somewhere/outside/verifier-root
python check_verifier_manifest_static.py --repo /path/to/time-rupture-inference \
       --lock verifier_manifest.lock
```

Exit 0 + `VERIFIER MANIFEST — OK (N verifier files pinned)` means the
repo's verifier files match the hashes recorded here. Any
`MISMATCH`/`MISSING` means a verifier changed — demand the matching
`docs/reports/VERIFIER_CHANGE_REPORT.md` rationale before trusting any
"all green" claim.

## Files

- `check_verifier_manifest_static.py` — the checker (no deps, no ctios).
- `verifier_manifest.lock` — pinned sha256 of every critical verifier.
- `EXPECTED_VERIFIERS.md` — the named list and why each is critical.

## Boundary

This proves only that verifier *files* were not silently mutated. It
does NOT prove the verifiers are correct, does NOT make the build
hermetic, and does NOT constitute external validation. READY still
requires a real external collaborator run with a valid proof bundle.
