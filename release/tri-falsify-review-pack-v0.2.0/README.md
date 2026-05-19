# TRI-Falsify — External Review Pack v0.2.0

You can review this artifact without reading the repository and without
the author present. Start here; everything you need is in this folder.

## What this is

A falsification-first temporal-inference apparatus with a reproducible
falsification path. A pinned hypothesis runs through an adversarial
battery into a sealed verdict; non-GREEN auto-proposes a human-gated
next experiment. Synthetic benchmarks only.

## What this is NOT

Not a product, not market-validated, not a proof of any private
theorem, not a cognition / AGI / brain / time-theory claim, not a
real-world-validity claim. Scope is stated in `CLAIM_BOUNDARY.md`.

## Review in three depths

| time | do this |
|---|---|
| 10 min | read this + `COMMANDS.md`; run `bash scripts/indi_demo.sh`; compare to `EXPECTED_OUTPUTS.md` |
| 30 min | run `bash scripts/reviewer_attack.sh`; inspect `evidence/REVIEWER_ATTACK_RESULT.json`; read `RESIDUAL_RISKS.md` |
| 2 h | follow `../../docs/EXTERNAL_VALIDATION_PROTOCOL.md`: supply a redacted skeleton, keep your probe local, confirm no private field leaks |

## Reporting

Fill `EXTERNAL_REVIEW_FORM.md` and return it. PASS/FAIL is decided by
you against `EXPECTED_OUTPUTS.md` and `CHECKSUMS.sha256` — not by trust
in the author.

## Honest status

`CONDITIONALLY_READY`. Every engineering gate passes; the one open item
is **not technical** — no external collaborator has yet run the private
redacted layer. The status cannot become `READY` until that happens
(`../../evidence/external_validation_status.json`,
`../../docs/FRONTIER_READINESS_REPORT.md`).
