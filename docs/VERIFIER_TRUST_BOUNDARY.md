# Verifier Trust Boundary — the law

## The law

> A verifier file may not change without the change being **proven**:
> the pinned hash in `verifier_manifest.lock` must be updated **and**
> `docs/reports/VERIFIER_CHANGE_REPORT.md` must record OLD_HASH,
> NEW_HASH, WHY_SAFE, and TEST_THAT_WOULD_FAIL_IF_WEAKENED. Otherwise
> the change does not exist as far as CI is concerned — the build
> fails.

Improvement is not asked for; it is proven against this law or rejected.

## Attack closed: verifier capture

Previously every audit was run by scripts inside the repo, so one PR
could weaken both a protected mechanism and the verifier that guards
it while CI stayed green. This is now blocked by three layers:

1. **`verifier_manifest.lock`** — sha256 of 13 critical verifier files
   (see `release/verifier-root/EXPECTED_VERIFIERS.md`).
2. **`tools/check_verifier_manifest_static.py`** — the independent
   root: stdlib-only, no `ctios` import, no repo install; it pins
   *itself*. CI runs it before installing anything.
3. **`tools/verifier_manifest.py`** (change-gate) — fails if a verifier
   changed without a lock update, or the lock changed without a
   rationale report naming the new hash.

The generator is not the only verifier of itself: the static checker
and `tests/test_verifier_capture_resistance.py` independently catch
mutation.

## Rejected / unverified premises (from the proposed CI plan)

These were **not** implemented because they rest on unverified
assumptions (verification-first, per the protocol's own rule):

- "force Node 24 deadline 2026-06-02" — no such annotation was
  measured; no fake `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` added.
- "replace loose pip with requirements-lock.txt" — no lock exists yet;
  inventing a filename ≠ determinism. Deferred to a dedicated,
  evidence-producing PR (hash-locked dependency contract).
- "move non-gate workflows to push-main" — not done without
  per-workflow PR-criticality classification (would risk dropping a
  reviewer gate).
- "reduce fetch-depth" — `fetch-depth: 0` kept; no experiment yet
  proves prereg/provenance survive shallow history.
- "0 Node warnings" / "deterministic deps" — not asserted without
  measured logs / a consumed lock artifact.

## Boundary

This closes verifier capture only. It does **not** make the build
hermetic, does **not** prove the verifiers correct, and does **not**
constitute external validation. Status remains
**CONDITIONALLY_READY_HARDENED_CI_PLUS** — READY still requires a real
external collaborator run with a valid proof bundle. The dependency
hermeticity model and offline/hash-locked install remain explicitly
unclaimed until their own evidence-producing PR.
