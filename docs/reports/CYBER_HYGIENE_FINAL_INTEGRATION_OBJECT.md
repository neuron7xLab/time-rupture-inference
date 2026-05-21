# Cyber Hygiene Final Integration Object

> **Status:** Ready-to-merge contract artifact  
> **Operating model:** Fail-closed by default, deterministic by design

---

## I. Integration Contract

This integration object is considered valid only when **all** conditions hold:

1. CI executes `cyber-hygiene-full` in staged-governance telemetry mode (`must_not_exist`, non-blocking report generation).
2. Governance check verifies report ↔ policy alignment.
3. Report structure is deterministic and contract-complete.
4. Merge criteria in docs are semantically identical to runtime gate behavior.

---

## II. Canonical Artifacts (Single Source of Truth)

| Domain | Artifact |
|---|---|
| Runtime gate | `tools/cyber_hygiene_audit.py` |
| Governance gate | `tools/check_cyber_hygiene_governance.py` |
| Shared contract constants | `tools/cyber_hygiene_contract.py` |
| Target class config | `configs/cyber_hygiene_targets.json` |
| Merge-readiness contract | `docs/reports/CYBER_HYGIENE_TOP7_PR_READY.md` |
| Evidence output | `evidence/cyber_hygiene_top7.json` |
| Test coverage | `tests/test_cyber_hygiene_audit.py`, `tests/test_cyber_hygiene_governance.py` |
| CI enforcement | `.github/workflows/ci.yml` |
| Local entrypoint | `Makefile` (`cyber-hygiene-full`) |

---

## III. Deterministic Execution (No Side Paths)

Run only:

```bash
make cyber-hygiene-full
```

No manual interpretation, no parallel policy path, no soft bypass.

---

## IV. Fail-Closed Semantics

The staged gate must return **FAIL** if any of the following is true:

- Telemetry report generation fails to produce evidence artifact.
- Governance document and report semantics diverge.
- Input contract is malformed.
- Invalid rows were dropped while strict mode is active.

Enforcement mode remains available via `make cyber-hygiene-enforce` and fails when disallowed classes are present.

---

## V. Rollback Protocol

1. Revert integration commits with `git revert <sha>`.
2. Preserve CI gate activation unless governance owner authorizes emergency override.
3. Record reason + timestamp in governance ledger before any temporary bypass.

---

## VI. Ownership & Accountability

- **Security Platform:** runtime implementation + CI wiring.
- **Governance Owner:** merge criteria integrity + drift prevention.

---

## VII. Final Readiness Criteria

Integration is green when:

- unit tests pass,
- governance contract check passes,
- CI gate remains fail-closed by default.
