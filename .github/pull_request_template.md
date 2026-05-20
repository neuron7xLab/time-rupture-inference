## Purpose

<!-- What does this PR change, and why is it needed? -->

## Boundary

This PR does **not** claim or change:

- [ ] scientific claim boundary
- [ ] canonical model path
- [ ] release gate semantics
- [ ] public README claims
- [ ] provenance root policy
- [ ] dependency trust policy

If any box above is intentionally changed, explain the evidence and rollback path.

## Change class

- [ ] documentation / governance
- [ ] tests only
- [ ] implementation
- [ ] experimental candidate
- [ ] canonical promotion
- [ ] CI / workflow / security control plane
- [ ] dependency / supply-chain
- [ ] release / evidence artifact

## Verification

Commands run locally:

```bash
# paste exact commands and outcomes
```

Required when relevant:

- [ ] `ruff check src tests scripts`
- [ ] `mypy --strict src/ctios`
- [ ] `PYTHONPATH=src pytest tests -q`
- [ ] `PYTHONPATH=src python scripts/provenance_attest.py`
- [ ] `python scripts/claims_lint.py`
- [ ] documentation trust gates
- [ ] full runner or targeted smoke
- [ ] external adversarial / reviewer smoke if public-facing

## Claim discipline

- [ ] no new claim
- [ ] claim has evidence reference
- [ ] claim is inside disclaimer / boundary block
- [ ] unsupported claim is quarantined or removed

Evidence references:

```text
<!-- paths, logs, test names, PR refs, or evidence artifacts -->
```

## Provenance and README impact

- [ ] no provenance impact
- [ ] provenance manifest regenerated through authorized script
- [ ] README test count unchanged
- [ ] README test count updated with `tools/update_readme_test_count.py --write`

## Experimental / canonical status

- [ ] does not touch `ctios.experimental.*`
- [ ] experimental-only change
- [ ] promotion candidate with preregistration and baseline comparison
- [ ] canonical change with rollback path

## Rollback

Rollback plan:

```text
<!-- exact revert, command, or artifact restoration path -->
```

## Reviewer checklist

- [ ] scope is bounded
- [ ] CI-required checks are expected to run
- [ ] no unpinned GitHub Actions were added
- [ ] no new dependency without lock/update rationale
- [ ] no branch-protection or trust-boundary weakening
- [ ] failure mode is documented
