# Open Structural Gaps

Machine-guarded (`tests/test_structural_gaps.py`). A gap's status may
not become `CLOSED` without a corresponding committed evidence file,
and `READY` may not be claimed while any gap is `OPEN`. These are not
vulnerabilities; they are honest scope limits.

## GAP_1: INDEPENDENT_REPRODUCTION

status: OPEN

requirement:
At least one external person or team reproduces the main results from
the public repository, without author shell access.

acceptance_criteria:
- external person/team (not the author),
- clean clone,
- run `bash scripts/conference_smoke.sh` or the full gate,
- record commit hash,
- record environment (OS, Python),
- record output metrics,
- compare against the expected frozen outputs,
- submit a signed / sanitized external proof bundle
  (`evidence/EXTERNAL_VALIDATION_BUNDLE.json`, schema-validated).

score_ceiling:
caps readiness below READY and below 95 until satisfied.

evidence_to_close: evidence/EXTERNAL_VALIDATION_BUNDLE.json (valid per
EXTERNAL_VALIDATION_BUNDLE.schema.json) AND
evidence/external_validation_status.json real_external_collaborator_run
== true.

## GAP_2: DOMAIN_BREADTH

status: OPEN

requirement:
The apparatus demonstrates value on at least two additional,
structurally distinct independent task families (beyond the synthetic
temporal-rupture family).

acceptance_criteria:
- ≥ 2 structurally distinct task families,
- preregistered falsifiers (pinned before run),
- negative controls,
- evidence ledger,
- baseline comparison,
- claim-boundary enforcement.

score_ceiling:
no productizable / generalized-platform claim is admissible while
this gap is open.

evidence_to_close: a committed evidence/DOMAIN_BREADTH_BUNDLE.json
referencing ≥2 sealed independent task-family verdicts.

## Status invariant

`READY` / `PRODUCTIZABLE` are impossible while either gap is `OPEN`.
This is enforced in code by `ctios.readiness_score` +
`ctios.external_validation` and asserted by
`tests/test_structural_gaps.py`.
