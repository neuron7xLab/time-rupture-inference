# No-Author-Required Review (WP7)

Strict pass condition: a reviewer completes the 10-minute, 30-minute,
and 2-hour paths **without asking the author anything**. If any step
needs author explanation, status stays CONDITIONALLY_READY.

## Self-contained entry

Everything starts from
`release/tri-falsify-review-pack-v0.2.0/README.md`. The reviewer never
needs the repository tour.

## Checklist

- [ ] clean clone (`git clone … && cd …`)
- [ ] install (`pip install -e ".[dev]"`) — no manual fixes
- [ ] run `bash scripts/reviewer_attack.sh` — one command, all gates
- [ ] inspect `evidence/REVIEWER_ATTACK_RESULT.json` — every hard gate
      `pass: true`
- [ ] compare frozen line to
      `release/.../EXPECTED_OUTPUTS.md` — byte-identical
- [ ] read `release/.../RESIDUAL_RISKS.md` — risks are stated, not
      hidden
- [ ] read `release/.../CLAIM_BOUNDARY.md` — forbidden claims explicit
- [ ] attempt one redacted skeleton from
      `examples/external_reviewer_packet_template.yaml` via
      `bash scripts/prepare_external_reviewer_packet.sh`
- [ ] confirm no never-share field is requested or emitted
- [ ] check `ctios.readiness_score` prints CONDITIONALLY_READY with the
      blocking fact first

## Pass / fail

- **PASS:** all boxes tickable solo; the artifact tells the reviewer
  what it is, what it forbids, what is open, and what to do next.
- **FAIL:** the reviewer has to ask "where do I start?" or "what does
  this number mean?" — then the entry docs failed, not the reviewer.

## Honest limit

This document asserts the *design intent* of author-independence and
provides the checklist to test it. It does **not** assert that an
external person has actually completed it — that is precisely the open
blocking fact tracked in
`evidence/external_validation_status.json`. Author-independence is
claimed as a property to be verified by the reviewer, not as a
completed result.
