# Code Quality Audit (WP6)

Honest inspection. Where nothing was wrong, that is stated plainly —
no defects were invented to look diligent.

## Inspected areas

- broad/bare exception swallowing (`except:`, `except Exception`)
- `except … : pass`
- mutable default arguments (`def f(x=[]/{})`)
- hidden global mutable state (`NAME = []/{}` at module scope)
- undocumented randomness (all RNG is `np.random.default_rng(seed)`)
- filesystem side effects in tests (writes go to `tmp_path` or are
  cleaned in `finally`)
- generated files excluded from provenance (NEXT_/FALSIFY_/map JSONs
  gitignored and filtered by `provenance_attest._ephemeral`)
- shell scripts use `set -euo pipefail`
- weak tests asserting only "runs"

## Findings

- **Exceptions:** none broad/bare in `src/ctios`; no `except: pass`.
- **Mutable defaults / global state:** none.
- **Randomness:** seed-deterministic throughout; replay hashes stable.
- **Test side effects:** transient files use `tmp_path` or `finally`
  unlink (`test_claims_lint_scope`, `test_surface_claim_hardening`).
- **Provenance:** ephemerals filtered (PR #24 hardening, verified on 6
  lineages); pinned preregs attested.
- **Shell scripts:** all carry `set -euo pipefail` **except**
  `scripts/reviewer_attack.sh`, which intentionally uses
  `set -uo pipefail` so it can run *every* gate, record each exit
  code, and then exit non-zero if any hard gate failed. A skipped or
  failed hard gate is still a FAIL in its JSON/MD output. This is a
  deliberate, documented exception, not an oversight.
- **Test strength:** suites include kill tests, adversarial fakes,
  byte-identity guards, claim-boundary planted-violation tests, and
  verdict-isolation — not happy-path only.

## Defects fixed

None required: the inspection found no quality defect to fix. The
audit's value here is the negative result, recorded.

## Remaining risks (not code defects)

The open items are the documented research/validation risks
(`release/tri-falsify-review-pack-v0.2.0/RESIDUAL_RISKS.md`), chiefly
the absent real external run. They are scope/validation facts, not
code-quality defects.

## Files intentionally not touched

Frozen v4/v5 runners and their metrics; preserved RED/PARTIAL
artifacts; pinned `prereg/*.yaml` specs; the `set -uo` choice in
`reviewer_attack.sh` (intentional).
