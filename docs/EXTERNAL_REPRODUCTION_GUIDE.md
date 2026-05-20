# External Reproduction Guide

This guide is the reviewer-facing intake path for `GAP_1: INDEPENDENT_REPRODUCTION`.
It reduces friction for a clean-clone external run. It does **not** close
`GAP_1` by itself, does **not** upgrade readiness, and does **not** expand
any scientific claim.

## Boundary

A valid external reproduction requires all of the following:

- reviewer is not the repository author,
- clean clone from the public repository,
- recorded commit hash,
- recorded OS and Python version,
- command transcript captured locally by the reviewer,
- output metrics compared against frozen expected values,
- sanitized proof bundle submitted for review,
- `evidence/external_validation_status.json` updated only after the bundle
  is accepted.

A template, mock, self-run, or edited status flag is not evidence.

## Clean-clone commands

```bash
git clone https://github.com/neuron7xLab/time-rupture-inference
cd time-rupture-inference
python --version
git rev-parse HEAD
pip install -e ".[dev]"
export PYTHONPATH=src
ruff check src tests scripts
python scripts/claims_lint.py
python scripts/check_doc_trust.py
python scripts/provenance_attest.py
pytest tests -q
bash scripts/conference_smoke.sh
PYTHONPATH=src python -m ctios.runner --mode full
PYTHONPATH=src python -m ctios.causal_runner --mode full
```

Expected frozen values for the public path:

- `learned_post_mae ~= 0.8830`
- `injected_post_mae ~= 8.0028`
- `oracle_post_mae ~= 0.7933`
- `causal_gain ~= 0.8680`
- `causal_null_gap ~= 0.0000`

If the clean clone fails, do not patch around it silently. Record the failure
as the external result. A negative reproduction is more valuable than a fake
pass.

## Bundle preparation

Start from:

```bash
cp templates/EXTERNAL_VALIDATION_BUNDLE.example.json /tmp/EXTERNAL_VALIDATION_BUNDLE.json
```

Then replace every placeholder with reviewer-owned values. The committed
example is marked `EXAMPLE_NOT_EVIDENCE`; it must never be copied into
`evidence/` as proof.

Required fields are pinned by `evidence/EXTERNAL_VALIDATION_BUNDLE.schema.json`.
The intake helper adds reviewer-facing checks for environment, commands, and
frozen metric drift:

```bash
python tools/validate_external_validation_bundle.py /tmp/EXTERNAL_VALIDATION_BUNDLE.json
```

For template maintenance only:

```bash
python tools/validate_external_validation_bundle.py \
  templates/EXTERNAL_VALIDATION_BUNDLE.example.json \
  --allow-example
```

## Acceptance rule

`GAP_1` can only be closed after a real external proof bundle is committed as
`evidence/EXTERNAL_VALIDATION_BUNDLE.json`, the status flag is intentionally
updated, and the existing anti-tamper checks still pass.

Until then, `GAP_1` remains OPEN and readiness remains capped.

## Admissible conclusion

The admissible conclusion after this PR is only:

> The repository now provides a structured intake path for independent external
> reproduction proof bundles.

Forbidden conclusion:

> The repository has already been independently reproduced or is now READY.
