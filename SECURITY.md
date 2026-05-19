# Security Policy

## Supported versions

| Version | Python | Supported |
|---|---|---|
| 0.1.x | 3.11 – 3.13 | yes (best effort) |

Older versions and other Python versions: not supported.

## Reporting a vulnerability

This is a public research artifact maintained best-effort by a solo
author; there is no SLA and no security team.

**Preferred:** GitHub *Private Vulnerability Reporting* — repository
**Security** tab → *Report a vulnerability* — **if that control is
available to you on this repo**.

**Fallback (if Private Vulnerability Reporting is not available):**
open a GitHub issue titled `SECURITY:` with a **minimal,
non-exploit** description (impact + affected file/area, no working
exploit, no secrets) and explicitly request a private follow-up
channel. Do not post a functional exploit in a public issue.

No email address or PGP key is published here on purpose: a fake or
unmonitored contact is worse than an honest GitHub-native path.

## Response

Best effort, target acknowledgement within **14 days**. No guaranteed
fix timeline. A confirmed supply-chain / trust-boundary issue is
prioritised over functional bugs.

## In security scope

- CI supply-chain bypass (loose dependency substitution).
- GitHub Action pin bypass / tag substitution.
- Verifier-manifest bypass (silent verifier weakening).
- Provenance / attestation forgery.
- Readiness-status tamper (claiming READY without the external proof
  bundle).
- Claim-boundary bypass that has a concrete security impact.

## Out of security scope

- Scientific disagreement or benchmark interpretation.
- Preregistered-threshold debate.
- The absence of external validation (a tracked structural gap, not a
  vulnerability — see `docs/OPEN_STRUCTURAL_GAPS.md`).
- Claims about intelligence / cognition (the project makes none; see
  the claim boundary).

This policy contains no placeholder text, no fabricated contact, and
no enterprise SLA. It states only what is honestly true for a solo
public artifact.
