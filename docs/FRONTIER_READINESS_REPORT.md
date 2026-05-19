# FRONTIER READINESS REPORT

Generated discipline, not self-congratulation. The number is last and
capped; the blocking fact is first.

## Verdict

- **Status: CONDITIONALLY_READY** (stable).
- **Blocking fact (single, non-technical):** no real external
  collaborator has run the private redacted layer
  (`evidence/external_validation_status.json:
  real_external_collaborator_run = false`). A simulated/mock pack does
  not count.
- **Score:** subordinate to the blocking fact by construction
  (`ctios.readiness_score`): external portability is capped at 5/10
  without a real external run, and no number can produce READY while a
  blocking fact holds. The agent is structurally forbidden from
  awarding itself a "READY" or a flattering total as a reward.

## Gates (engineering)

| gate | state |
|---|---|
| Reproducibility | PASS — clean-clone contract, CI green, frozen v4/v5 byte-identical |
| Falsification | PASS — 6 pinned lineages, executable falsifiers, preserved negatives |
| Operational boundary | PASS — quantitative per lineage (prereg/*.yaml) |
| Adversarial null | PASS — 8 degenerate probes × 7 families, none escapes |
| Claim boundary | PASS — claims-lint full surface incl. release/** + surface-hardening test |
| Evidence ledger | PASS — verdict + provenance + preserved RED/PARTIAL/GREEN |
| Human gate | PASS — non-GREEN proposes, never auto-runs |
| External portability | PARTIAL — path works without core edits (mock only); real run absent |

## Why not READY

READY requires an independent person to run
`docs/EXTERNAL_VALIDATION_PROTOCOL.md` and attest no never-share field
leaked. That has not happened. Every engineering gate passing does not
substitute for it. This is the honest ceiling: the artifact is handed
to other hands now, not polished further by the author.

## Next allowed / forbidden

- **Allowed:** ship `release/tri-falsify-review-pack-v0.2.0/` to an
  external reviewer; pin a new decision-gated lineage.
- **Forbidden:** asserting READY / PRODUCTIZABLE / "validated";
  upgrading the claim on a simulated pack; loosening a failed
  threshold; auto-running a next experiment.
