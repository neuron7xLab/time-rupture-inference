# VERIFIER CHANGE REPORT

The verifier law (`docs/VERIFIER_TRUST_BOUNDARY.md`) requires this for
any change to a pinned verifier file. Latest entry on top.

## Entry — generated source mirror + complementary claim-source gate

### VERIFIER_CHANGED

`.github/workflows/ci.yml`, `scripts/build_doc_trust_audit.py`

### OLD_HASH

- ci.yml `38eed815f7d53f1b0273034c39f8457a584f25dff5bcd43ddb16e9ed93493eb8`
- build_doc_trust_audit.py `f7578555d61a097c30d380901cb3b1f5ec35f8de5b3dd72bc660275eff963585`

### NEW_HASH

- ci.yml `46f9d3771d67b2f405a6f1c57de548b91f78774951a1bdbb103f5272c3dba552`
- build_doc_trust_audit.py `70a230c8322b564de3b8cbe51124e05d4533c1c7a3ec121d086316cfe8dcafc7`

### WHY_SAFE

Strengthening only. `build_doc_trust_audit.py` now also renders
`docs/SOURCE_REGISTRY.md` deterministically from
`evidence/SOURCE_REGISTRY.yaml` and `--verify-only` fails closed on
mirror drift (the human mirror can no longer diverge from the machine
source of truth — a previously logged debt, now closed). `ci.yml`
adds one stdlib step `python scripts/check_doc_claim_sources.py`
inside the existing documentation trust gate: a flagged prior-art /
standards term in a positioning doc must be accounted for in
`docs/REFERENCES.md`, plus a forbidden-phrase-outside-disclaimer
scan — strictly more fail-closed coverage, none removed. No
trigger/permission/SHA-pin/install change, no gate removed. The new
`scripts/check_doc_claim_sources.py` is pinned in
`verifier_manifest.lock` and claims-lint-exempt (holds the lexicon as
data). No scientific claim expanded; no frozen metric/threshold/
lineage touched.

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_doc_claim_sources.py` (missing required doc / unmapped
term / forbidden-phrase-outside-disclaimer rejected, disclaimer-wrapped
allowed, live repo passes) + `build_doc_trust_audit.py --verify-only`
mirror-drift check + the documentation trust gate + the verifier
manifest gate (these NEW_HASHes must match).

## Entry — trust-layer hardening (real parser + ≥20 claims)

### VERIFIER_CHANGED

`.github/workflows/ci.yml`, `scripts/check_doc_trust.py`,
`scripts/build_doc_trust_audit.py`

### OLD_HASH

- ci.yml `a797983a042941fc0bac5cf626b8ebb65197b7091c05aee2004d23a4a99a0e8c`
- check_doc_trust.py `280263c87c73484adc70348ebebe25c386e59b899572cca953b44ce960b73104`
- build_doc_trust_audit.py `0e1f36c5c37e4d3d0416c215ec0047c6b82cbc9d1f33ab7a1b789feae706e494`

### NEW_HASH

- ci.yml `38eed815f7d53f1b0273034c39f8457a584f25dff5bcd43ddb16e9ed93493eb8`
- check_doc_trust.py `49f46fff592159c7d152a83cd9fcd7b669ef535e2636f32d08de6e58df803254`
- build_doc_trust_audit.py `f7578555d61a097c30d380901cb3b1f5ec35f8de5b3dd72bc660275eff963585`

### WHY_SAFE

Strengthening only. `check_doc_trust.py` is rewritten from a
presence-checker into a real row-by-row matrix parser with
class-aware contracts (EMPIRICAL/REPRODUCIBILITY → runnable/artifact
path; ENGINEERING → script/test/CI; GOVERNANCE → gate/linter/check;
INSPIRATION → biological-fidelity boundary; SUPPLY_CHAIN →
not-hermetic/not-SLSA-L3; OPEN_GAP → OPEN_STRUCTURAL_GAPS link),
plus registry-schema completeness, registry↔matrix↔REFERENCES
consistency, ≥20-claim floor, and a duplicate-manual-note guard —
strictly more fail-closed conditions, none removed.
`build_doc_trust_audit.py` now also emits the generated
`docs/reports/DOC_VALUE_AUDIT.md` from the JSON (no hand-authored
audit prose). `ci.yml` change is a step rename only
(`doc trust gate` → `documentation trust gate`); no
trigger/permission/SHA-pin/install change, no gate removed. No
scientific claim expanded; no frozen metric/threshold/lineage
touched. Both scripts remain claims-lint-exempt (they hold the
forbidden lexicon as data).

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_doc_trust.py` (unknown source / missing-evidence /
empirical-without-runnable / inspiration-without-bio-boundary /
supply-chain-without-ceiling / unlinked-open-gap / thin-matrix /
forbidden-phrase / README-bibliography / review-note-overlength /
duplicate-manual-note all rejected, live repo passes) + the
documentation trust gate as a CI step + the verifier manifest gate
(these NEW_HASHes must match).

## Entry — docs trust layer (claim/source/boundary gate)

### VERIFIER_CHANGED

`.github/workflows/ci.yml`

### OLD_HASH

`b6ccd5b14bd63304c7dba3437c490f02e70562f49fe2c6a7a943bd39e8d9ff91`
(the NEW_HASH from the PR O entry below)

### NEW_HASH

`a797983a042941fc0bac5cf626b8ebb65197b7091c05aee2004d23a4a99a0e8c`

### WHY_SAFE

Strengthening only. ci.yml change: one new stdlib+yaml PR-blocking
step in `proof-of-life` after the claim-lexicon lint —
`build_doc_trust_audit.py --verify-only` then `check_doc_trust.py`
(fails closed on a missing trust-layer file, an unknown source_id, an
unsupported claim, an inspiration claim without its biological-fidelity
boundary, a supply-chain claim without its not-hermetic/not-L3 ceiling,
an unlinked open gap, a forbidden external phrase asserted outside a
disclaimer, README bibliography bloat, or an over-long author note).
No gate removed, no trigger/permission/SHA-pin change, no install
loosened. The two new enforcement scripts
(`scripts/check_doc_trust.py`, `scripts/build_doc_trust_audit.py`) are
added to `verifier_manifest.lock` (more files protected, none
unpinned) and are claims-lint-exempt by the same rationale as
`scripts/claims_lint.py` (they hold the forbidden lexicon as data). No
scientific claim expanded; no frozen metric/threshold/lineage touched.

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_doc_trust.py` (missing file / unknown source / unsupported
claim / inspiration-without-boundary / supply-chain-without-ceiling /
unlinked open-gap / forbidden-phrase / README-bibliography-bloat /
author-note-overlength all rejected, live repo passes) + the doc-trust
step as a CI gate + the verifier manifest gate (this NEW_HASH must
match, and the two new pinned scripts' hashes must match the lock).

## Entry — PR O (supply-chain aggregate + Scorecard honesty)

### VERIFIER_CHANGED

`.github/workflows/ci.yml`

### OLD_HASH

`e6d42bf2884a54b16ec1353268ea1f6e2b468c103b487e6c880f5c5065d2014c`
(the NEW_HASH from the PR L entry below)

### NEW_HASH

`b6ccd5b14bd63304c7dba3437c490f02e70562f49fe2c6a7a943bd39e8d9ff91`

### WHY_SAFE

Strengthening only. ci.yml change: one new stdlib-only PR-blocking
step in `proof-of-life` after the existing trust audits —
`verify_scorecard_prerequisites.py` then
`python -m ctios.supply_chain_audit` (fail-closed aggregate over the
verifier/workflow/dependency/release/SBOM/Scorecard-honesty roots).
No gate removed, no trigger/permission/SHA-pin change, no install
loosened (still `-r requirements-ci.lock`). Additionally this PR
**closes a logged debt**: the trust scripts (`audit_workflow_trust`,
`verify_ci_deps`, `audit_release_trust`, `generate_sbom`,
`verify_scorecard_prerequisites`) and `src/ctios/supply_chain_audit.py`
are now pinned in `verifier_manifest.lock` — strictly more files
protected, none unpinned. Honest level unchanged and not inflated
(`SUPPLY_CHAIN_CONSISTENT_FAIL_CLOSED`; not hermetic, not
hash-locked, not SLSA L3, Scorecard NOT_RUN).

### TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_supply_chain_audit.py` (fabricated Scorecard score /
RUN-without-artifact / missing status / single-root failure all
rejected, live repo passes) + the aggregate as a CI gate + the
verifier manifest gate (this NEW_HASH must match, and the newly
pinned trust scripts' hashes must match their lock entries).

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
