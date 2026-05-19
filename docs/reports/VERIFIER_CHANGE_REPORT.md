# VERIFIER CHANGE REPORT

The verifier law (`docs/VERIFIER_TRUST_BOUNDARY.md`) requires this for
any change to a pinned verifier file. Latest entry on top.

## Entry — PR K (workflow SHA pinning + least-privilege)

### VERIFIER_CHANGED

`.github/workflows/ci.yml`

### OLD_HASH

`b72e41d9e948ced15b23b191150eb14a9da74c5ea13036c059c7df802571d30b`
(the NEW_HASH from the PR #35 entry below)

### NEW_HASH

`15e0ef3a03f0d31115ddb88c0493d81a5e58fc54e88d00e543fb006497a19bff`

### WHY_SAFE

Strengthening only. `ci.yml` changes: (1) all actions repinned from
mutable tags (`@v4`/`@v5`) to 40-hex commit SHAs with `# vX` comments;
(2) explicit top-level `permissions: contents: read`; (3) a new
PR-blocking step `python scripts/audit_workflow_trust.py` BEFORE
dependency install. No gate removed, no trigger changed, no install
loosened; the PR #34/#35 verifier + mypy-strict steps untouched;
`fetch-depth: 0` preserved. Strictly more constraint.

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_workflow_trust.py`: `test_tag_only_action_fails`,
`test_sha_without_version_comment_fails`,
`test_missing_permissions_fails`, `test_write_all_fails`,
`test_non_release_write_unjustified_fails`,
`test_live_repo_passes_real_audit`. Plus `tools/verifier_manifest.py`
gate + `tools/check_verifier_manifest_static.py` fail if `ci.yml`
changes without this entry's matching NEW_HASH.

---

## Entry — PR #35 (CI mypy --strict explicit)

### VERIFIER_CHANGED

`.github/workflows/ci.yml`

### OLD_HASH

`0e48ffecb41851154c789b2c64c11b56edb9aaa09dd333d84e53881fbe9a882b`

### NEW_HASH

`b72e41d9e948ced15b23b191150eb14a9da74c5ea13036c059c7df802571d30b`

### WHY_SAFE

`run: mypy` → `run: mypy --strict src/ctios` (no longer
config-dependent). Strictly more constraint, never less.

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_ci_mypy_explicit.py` (no bare mypy / explicit target
required) + the verifier manifest gate.
