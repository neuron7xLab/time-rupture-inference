# Dependency Trust Contract (PR L)

## Honest level

**LEVEL_1_PINNED_NO_HASHES.** `requirements-ci.lock` is a deliberate
pinned version set (`pkg==ver`). Every CI gate workflow installs from
it (`pip install -r requirements-ci.lock`, package via
`-e . --no-deps`). It has **no per-package hashes**, so
`pip --require-hashes` is impossible.

## Threat model closed

Loose `pip install <names>` in CI (silent version substitution / a
newly published malicious minor) and undeclared CI tools (`mypy`,
`types-PyYAML` previously installed loosely, not declared).

Enforced by `scripts/verify_ci_deps.py` (stdlib-only) wired into
`ci.yml`: it fails if any workflow installs loosely instead of from
the lock, if `mypy`/`types-PyYAML` are not declared in pyproject
`[dev]`, if no workflow consumes the lock, if hash-locking is claimed
without hashes, or if this document overclaims hermeticity. Negative
tests: `tests/test_ci_deps_contract.py`.

## What is NOT claimed

This build is **not hermetic** (it reaches PyPI over the network at
install time). It is **not hash-locked** (no `--hash` lines, no
`--require-hashes`). It is **not supply-chain-sealed**. A pinned
version can still be a compromised pinned version. Reaching
`LEVEL_2_HASH_LOCKED` requires `pip-compile --generate-hashes` from a
clean venv (a separate deliberate step; blocked state recorded in
`evidence/DEPENDENCY_HASH_LOCK_BLOCKED.json`).

## What IS proven

CI cannot silently change a dependency version without a visible diff
to `requirements-ci.lock`; `mypy`/`types-PyYAML` are declared, not
smuggled; no gate workflow uses an unpinned package list.
