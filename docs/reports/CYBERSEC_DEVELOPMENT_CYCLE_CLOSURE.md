# Cybersecurity Development Cycle Closure (14 Remaining Tasks)

## Objective
Close the remaining 14 integration tasks with deterministic acceptance criteria, explicit ownership, and fail-closed gates.

## Task register (T11–T24)
| ID | Task | Owner | Artifact | Gate (PASS condition) |
|---|---|---|---|---|
| T11 | Pin Bandit policy version contract | Security Platform | `configs/cyber_hygiene_targets.json` + lock note | CI fails on target drift |
| T12 | Add schema contract for `cyber_hygiene_top7.json` | Detection Eng | `evidence/EXTERNAL_VALIDATION_BUNDLE.schema.json` (section update) | schema validation step passes |
| T13 | Add deterministic seed/version stamp to report | Security Platform | `tools/cyber_hygiene_audit.py` metadata block | report contains tool version + UTC timestamp |
| T14 | Add negative fixture for malformed top-level JSON | Detection Eng | `tests/test_cyber_hygiene_audit.py` fixture extension | test fails pre-fix, passes post-fix |
| T15 | Add `must_exist` governance-path coverage | Detection Eng | `tests/test_cyber_hygiene_governance.py` | mode-branch coverage > 0 for both modes |
| T16 | Add CI artifact upload for hygiene report | Platform | `.github/workflows/ci.yml` | artifact always uploaded |
| T17 | Add Make target for local full cyber gate | Platform | `Makefile` (`cyber-hygiene-full`) | local command executes both gates |
| T18 | Add rollback runbook snippet | Infra Sec | `docs/reports/CYBER_HYGIENE_TOP7_PR_READY.md` | rollback command documented and verified |
| T19 | Add branch protection check matrix entry | Governance | `docs/governance/REQUIRED_CHECKS_MATRIX.md` | matrix lists both cyber gates as required |
| T20 | Add ownership mapping for hygiene gates | Governance | `docs/reports/CYBER_HYGIENE_TOP7_PR_READY.md` | owner + escalation contact present |
| T21 | Add adversarial fixture for absolute+relative path mix | Detection Eng | `tests/test_cyber_hygiene_audit.py` | hotspot counts stable deterministic |
| T22 | Add false-positive control check for synthetic paths | Detection Eng | `tools/check_cyber_hygiene_governance.py` | check fails if synthetic path inflation detected |
| T23 | Add evidence freshness check (UTC date) | Security Platform | `tools/check_cyber_hygiene_governance.py` | stale evidence fails gate |
| T24 | Add final release readiness summary | Governance | `docs/reports/CYBERSEC_DEVELOPMENT_CYCLE_CLOSURE.md` | all tasks marked complete with commit refs |

## Sequencing
1. Contracts first: T11–T15.
2. CI and execution plumbing: T16–T17.
3. Governance and rollback hardening: T18–T20.
4. Adversarial + falsification closure: T21–T23.
5. Release closure artifact: T24.

## Definition of done
- Both gates (`cyber-hygiene-audit`, `cyber-hygiene-governance`) enforced in CI.
- All T11–T24 have merged artifacts and tests.
- Final closure report includes commit references and gate screenshots/log excerpts.

## Current status
- Baseline gating is active.
- Remaining tasks are planned and bounded for deterministic closure.
