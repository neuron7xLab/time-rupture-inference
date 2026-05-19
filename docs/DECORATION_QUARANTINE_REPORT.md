# Decoration / Quarantine Report (WP7)

Outcome for every component the deep audit flagged. Generated audits
back each decision (`evidence/MECHANISM_INVENTORY.json`,
`TEST_VALUE_AUDIT.json`, `CODE_QUALITY_AUDIT_RESULT.json`).

## CONVERT_TO_EXECUTABLE_CHECK

- `docs/CODE_QUALITY_AUDIT.md` (markdown-only) → now an *output* of
  `ctios.code_quality_audit`; the executable check + planted-defect
  test are the source of truth.
- Mechanism inventory → `ctios.mechanism_inventory` (generated +
  meta-tested), not hand-written prose.
- Test-value audit → `ctios.test_value_audit` (generated +
  meta-tested).
- External-validation status → gated by `ctios.external_validation`
  (schema-validated proof bundle), no longer a hand-edited boolean.
- Shell gates → artifact-asserted via `ctios.artifact_assertions`
  (exit code alone is no longer accepted as evidence).

## KEEP_AS_MECHANISM

- `drift`, `gates`, `ledger`, `utils`, `v6_precision`: real
  mechanisms; the audit found them without *direct* tests, so contract/
  kill tests were added (`tests/test_core_contract_audit.py`). v6 is a
  preserved-RED lineage — tested for deterministic replay, not GREEN.

## QUARANTINE_AS_REPORT_ONLY

- `agent_cli`, `review_cli`, `spec_cli`, `falsify_cli`, `platform_demo`:
  reclassified REVIEWER_SURFACE — thin argparse/orchestration wrappers
  over tested cores, exercised under artifact-asserted demos. They are
  not counted as correctness evidence on their own.
- Narrative reports (`docs/reports/*`, release pack prose) remain
  REPORT_ONLY and are claims-lint / surface-hardening fenced; never a
  gated claim.

## DELETE_AS_DECORATION

- None. No component was found that is purely decorative *and* in the
  reviewer path. The honest result is recorded rather than inventing a
  deletion to look thorough.

## Untouched (by rule)

Preserved RED/PARTIAL artifacts; frozen v4/v5 metrics; pinned
`prereg/*.yaml`; lineage history. The `set -uo` collectors
(`reviewer_attack.sh`, `deep_mechanism_audit.sh`) are an allowlisted,
documented exception, enforced by the executable code-quality audit.
