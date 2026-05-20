# Contributing

## Purpose

This repository is a falsification-first research artifact. Contributions must preserve claim discipline, reproducibility, provenance, and fail-closed behavior.

## Contribution rules

### 1. No claim without evidence

Any new or expanded claim must include at least one witness:

- test
- evidence artifact
- benchmark result
- source reference
- reproducible command
- mechanical check

Unsupported claims must be removed or quarantined.

### 2. No benchmark without baseline

Benchmark or capability claims require:

- baseline
- metric
- seed policy
- failure condition
- evidence path

### 3. No experimental promotion without protocol

Changes under `src/ctios/experimental/**` are candidate-only until they satisfy `docs/EXPERIMENTAL_PROMOTION_PROTOCOL.md`.

Experimental code may not replace canonical code by import side effect, README wording, or release-gate implication.

### 4. No dependency update without lockfile discipline

Dependency changes must update the relevant lockfile and explain why the update is needed.

Raw environment freezes from uncontrolled local environments are not accepted.

### 5. No workflow weakening

Changes to `.github/workflows/**`, provenance scripts, dependency checks, or repository governance docs must explain:

- invariant preserved or added
- risk reduced
- checks affected
- rollback path

### 6. No README count drift

If tests are added or removed, update README counts with:

```bash
python tools/update_readme_test_count.py --write
PYTHONPATH=src python scripts/provenance_attest.py --write
```

Then verify:

```bash
PYTHONPATH=src pytest tests/test_readme_sync.py tests/test_provenance.py -q
```

### 7. No provenance drift

If a signed file changes, regenerate the manifest through the authorized script:

```bash
PYTHONPATH=src python scripts/provenance_attest.py --write
```

Manual hash editing is not accepted.

## Required local checks

Recommended before opening a PR:

```bash
ruff check src tests scripts
mypy --strict src/ctios
python scripts/claims_lint.py
python scripts/build_doc_trust_audit.py --verify-only
python scripts/check_doc_claim_sources.py
python scripts/check_doc_trust.py
PYTHONPATH=src python scripts/provenance_attest.py
PYTHONPATH=src pytest tests -q
```

For public or reviewer path changes, also run:

```bash
bash scripts/external_adversarial_demo.sh
bash scripts/conference_smoke.sh
bash scripts/indi_demo.sh
```

## Pull request expectations

Every PR must include:

- purpose
- boundary
- verification commands
- claim impact
- provenance impact
- rollback plan

Use `.github/pull_request_template.md`.

## Review stance

A contribution may be rejected even if it works locally when it:

- inflates claims
- weakens provenance
- bypasses required checks
- adds unbounded complexity
- changes canonical behavior without preregistration
- removes negative-result memory
- introduces dependency or workflow drift

## License

By contributing, you agree that your contribution is licensed under the repository MIT license.
