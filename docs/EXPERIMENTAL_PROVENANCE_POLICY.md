# Experimental Provenance Policy

## Purpose

This policy makes the provenance boundary explicit for nested experimental modules.

The current provenance script signs top-level `src/ctios/*.py`, `scripts/*.py`, `scripts_prereg.py`, selected config files, prereg files, and root governance files. It does not recursively include nested `src/ctios/**` modules unless the script policy is changed.

That behavior is acceptable only as an explicit boundary.

## Policy

Experimental modules under:

```text
src/ctios/experimental/**
```

are not canonical provenance-root files until promoted.

They must still:

- carry SPDX headers
- be isolated from canonical runners
- have contract checks before promotion
- avoid public claim expansion
- avoid protected branch writes

## Rationale

Experimental modules are candidate substrates. They may change quickly and may fail. Signing them as canonical too early turns exploration into release-governed surface area and creates avoidable manifest churn.

Canonical provenance should attest accepted internal integrity, not every quarantined candidate.

## Promotion rule

When an experimental module is promoted, one of two actions is required:

### Option A: move to canonical top-level module

Example:

```text
src/ctios/experimental/foo.py -> src/ctios/foo.py
```

The existing provenance glob includes it automatically.

### Option B: expand provenance root intentionally

Change `scripts/provenance_attest.py` from top-level-only to an explicit recursive include policy, then regenerate `provenance_manifest.json`.

Required wording in the PR body:

```text
This PR changes provenance-root policy to include promoted nested modules.
```

## Forbidden state

Forbidden:

```text
experimental module used by canonical path but absent from provenance root
```

If canonical code imports an experimental module, either promote it or fail the PR.

## Check command

```bash
python tools/check_experimental_contract.py
PYTHONPATH=src python scripts/provenance_attest.py
```

## Claim boundary

This policy is an internal integrity boundary. It is not an external originality, novelty, or no-plagiarism claim.
