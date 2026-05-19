# EXTERNAL REVIEW FORM

Fill and return. Decide PASS/FAIL yourself against `EXPECTED_OUTPUTS.md`
and `CHECKSUMS.sha256`. Do not ask the author to interpret results.

```
Reviewer:
Date:
Clone commit (git rev-parse HEAD):
Machine / OS / Python:

## 10-minute path
[ ] pip install -e ".[dev]" succeeded without manual fixes
[ ] bash scripts/indi_demo.sh -> ALL HARD GATES PASSED
[ ] frozen line byte-identical (0.8830 / 8.0028 / 0.7933): PASS / FAIL
[ ] I understood what is claimed and forbidden without asking: YES / NO

## 30-minute path
[ ] bash scripts/reviewer_attack.sh completed
[ ] evidence/REVIEWER_ATTACK_RESULT.json present, all hard gates PASS
[ ] adversarial probes: none reached clean PASS: PASS / FAIL
[ ] changed one threshold -> spec_sha256 changed: PASS / FAIL
[ ] read one preserved negative; reproduction command worked: PASS / FAIL

## 2-hour path (the real validation)
[ ] supplied my own redacted skeleton (no private mechanism)
[ ] kept my opaque probe local; repo received only sanitized verdict
[ ] confirmed NO never-share field leaked into any artifact
[ ] obtained a sealed verdict + a human-gated next proposal
[ ] external opaque probe required NO edit to ctios core: YES / NO

## Verdict
Engineering gates:           PASS / FAIL
Claim boundary respected:    PASS / FAIL
Adversarial robustness:      PASS / FAIL
Private layer (real run):    COMPLETE / NOT ATTEMPTED
Author needed at any step:   YES / NO   (YES => not READY)

Overall reviewer call:       CONDITIONALLY_READY / NOT_READY / READY
Free-text objections:
```

If "Private layer (real run) = COMPLETE" and no author was needed,
attach the sanitized verdict artifacts so
`evidence/external_validation_status.json` can be updated.
