# Noise Hygiene Audit

## Purpose
Deterministic lexical scan for maintenance-risk markers.
No scientific claims. This is an engineering gate.

## Execution
- CI/default output: `evidence/noise_hygiene/latest.json`
- Optional snapshot: `evidence/noise_hygiene/snapshot_YYYY-MM-DD.json`
- Policy file: `.auditignore.json`

Run:
```bash
make noise-audit
```

## Enforcement contract
`--enforce` returns RED (`exit 1`) when policy evaluation reports violations.
Current hard checks target `src/` for unauthorized:
- `todo_markers`
- `ai_disclaimer`

Unauthorized means: finding exists in `src/` and no valid policy exception
for `(path, rule)` exists in `.auditignore.json`.

## Policy requirements
Each exception entry must contain:
- `path`
- `rule`
- `reason` (min length)
- `owner` (email)
- `expires_utc` (`YYYY-MM-DD`)

Expired or malformed entries invalidate policy and force RED in enforce mode.

## Governance boundary
This audit does not close structural gaps and does not upgrade repository status.
