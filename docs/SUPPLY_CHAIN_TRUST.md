# Supply-Chain Trust (PR O — consolidated)

## Honest level

**`SUPPLY_CHAIN_CONSISTENT_FAIL_CLOSED`.** The aggregate
(`python -m ctios.supply_chain_audit`) runs every independent
supply-chain trust root as a separate process and fails closed: any
one FAIL → aggregate FAIL, no PASS verdict written.

| Root | Gate | PR | Honest level |
|---|---|---|---|
| Verifier manifest (independent static root + gate) | `tools/check_verifier_manifest_static.py`, `tools/verifier_manifest.py` | G | sha256 pin, change-report required |
| Workflow trust | `scripts/audit_workflow_trust.py` | K / K.1 | every `uses:` bound to 40-hex SHA + exact tag in `ACTION_SHA_RESOLUTION.json` |
| Dependency trust | `scripts/verify_ci_deps.py` | L | `LEVEL_1_PINNED_NO_HASHES` (pinned, **not** hash-locked, **not** hermetic) |
| Release trust | `scripts/audit_release_trust.py` | N | SLSA **Build L2** (GitHub artifact attestation), **not** L3 |
| SBOM | `scripts/generate_sbom.py --verify-only` | N | SPDX-2.3 derived from the lock, drift = fail |
| Scorecard honesty | `scripts/verify_scorecard_prerequisites.py` | O | OpenSSF Scorecard recorded **NOT_RUN**, **not** PASS |

## OpenSSF Scorecard — why NOT_RUN, not PASS

Scorecard requires live GitHub-API network access. `CLAUDE.md`
imposes a hard **no-network-in-CI/tests** invariant, so the in-gate
supply-chain audit is offline-only and *cannot* execute Scorecard.
Running it in-gate would either break the offline invariant or
fabricate a number. `evidence/SCORECARD_STATUS.json` therefore
records `status: NOT_RUN`, `score: null`, with the reason.
`verify_scorecard_prerequisites.py` *enforces* that honesty: a
numeric score while `NOT_RUN`, or `RUN` without a real tool version
and committed scorecard artifact, is a hard FAIL. If Scorecard is
ever run out-of-band, the status file must be replaced with `RUN`
carrying a real `tool_version` + committed `scorecard_json`.

## What is NOT claimed

Not hermetic. Not hash-locked. Not SLSA L3. No OpenSSF Scorecard
score. The aggregate proves the trust roots are internally
**consistent and fail-closed** — it does not promote any of them to
a stronger level than each individually earns.

## Run it

```
bash scripts/supply_chain_trust_audit.sh
```

Wired into `gate` (`.github/workflows/ci.yml`, `proof-of-life`) as a
PR-blocking step. The four trust scripts above and
`src/ctios/supply_chain_audit.py` are pinned in
`verifier_manifest.lock` (closes debt item: trust scripts unpinned).
