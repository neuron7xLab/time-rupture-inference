# VERIFIER CHANGE REPORT

The verifier law (`docs/VERIFIER_TRUST_BOUNDARY.md`) requires this for
any change to a pinned verifier file. This is its first real exercise
— on the agent's own change.

## VERIFIER_CHANGED

`.github/workflows/ci.yml`

## OLD_HASH

`0e48ffecb41851154c789b2c64c11b56edb9aaa09dd333d84e53881fbe9a882b`

## NEW_HASH

`b72e41d9e948ced15b23b191150eb14a9da74c5ea13036c059c7df802571d30b`

## WHY_SAFE

The only change to `ci.yml` is **strengthening**, not weakening: the
typing step changed from config-dependent `run: mypy` to the explicit
`run: mypy --strict src/ctios`. This removes a silent-weakening path
(editing `[tool.mypy]` in `pyproject.toml` could previously relax CI
typing without touching the workflow). No gate was removed, no trigger
changed, no install loosened, the verifier-root step from PR #34 is
untouched, `fetch-depth: 0` preserved. Strictly more constraint, never
less.

## TEST_THAT_WOULD_FAIL_IF_WEAKENED

`tests/test_ci_mypy_explicit.py`:
- `test_ci_has_no_bare_mypy_run_step` fails if `ci.yml` reverts to a
  bare `mypy` step.
- `test_ci_invokes_mypy_strict_explicitly` fails if the explicit
  `mypy --strict src/ctios` invocation is removed.
- `test_explicit_target_passes_locally` fails if strict typing breaks.

Additionally `tools/verifier_manifest.py` (gate) + the independent
`tools/check_verifier_manifest_static.py` fail if `ci.yml` changes
without this report carrying the matching NEW_HASH.
