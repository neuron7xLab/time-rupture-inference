# VERIFIER CHANGE REPORT

The verifier law (`docs/VERIFIER_TRUST_BOUNDARY.md`) requires this for
any change to a pinned verifier file. Latest entry on top.

## Entry — PR L (CI consumes pinned lock + dep-trust gate)

### VERIFIER_CHANGED

`.github/workflows/ci.yml`

### OLD_HASH

`0f01d7b40c90ee9681730e387678e8dbdb030387a5ba6eb1347a69361c9f752a`
(the NEW_HASH from the PR #38 entry below)

### NEW_HASH

`e6d42bf2884a54b16ec1353268ea1f6e2b468c103b487e6c880f5c5065d2014c`

### WHY_SAFE

Strengthening. ci.yml changes: (1) every loose `pip install <names>`
replaced with `pip install -r requirements-ci.lock` (pinned set);
(2) a new stdlib-only PR-blocking step `python scripts/verify_ci_deps.py`
added before install. Determinism increases (no silent version
substitution); no gate removed, no trigger/permission/SHA-pin change,
verifier + workflow-trust + mypy-strict steps untouched. Honest level
LEVEL_1_PINNED_NO_HASHES — not hash-locked, not hermetic (stated in
docs/DEPENDENCY_TRUST_CONTRACT.md).

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_ci_deps_contract.py` (loose install / missing lock /
undeclared mypy / fake hash-lock all rejected; live repo passes) +
`scripts/verify_ci_deps.py` as a CI gate + the verifier manifest gate
(this NEW_HASH must match).

## Entry — PR #38 (CI installs declared types-PyYAML)

### VERIFIER_CHANGED

`.github/workflows/ci.yml`

### OLD_HASH

`15e0ef3a03f0d31115ddb88c0493d81a5e58fc54e88d00e543fb006497a19bff`
(the NEW_HASH from the PR K entry below)

### NEW_HASH

`0f01d7b40c90ee9681730e387678e8dbdb030387a5ba6eb1347a69361c9f752a`

### WHY_SAFE

Strengthening / consistency only. With `ignore_missing_imports=false`
(this PR), `mypy --strict src/ctios` requires the `types-PyYAML`
stubs. `types-PyYAML` is a declared dev dependency, but the loose
`pip install` lines in the `gate` and external-adversarial jobs did
not install it, so CI mypy broke. The change appends `types-PyYAML`
to those loose installs (and v7-readiness.yml, unpinned) so CI
actually installs the dependency the project declares. No gate
removed, no trigger changed, no permission widened, SHA pins / verifier
step / mypy-strict step untouched. CI now installs *more* of the
declared toolchain, never less.

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_ci_mypy_explicit.py` (explicit `mypy --strict src/ctios`,
no bare mypy) + the `gate` job's own `mypy --strict src/ctios` step
(red without types-PyYAML, as observed on PR #38 run 1) + the verifier
manifest gate (this entry's NEW_HASH must match).

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
