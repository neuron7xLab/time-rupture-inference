# Workflow Trust Contract (PR K)

## Threat model

GitHub Action **tag substitution** (a mutable tag like `@v4`
re-pointed to malicious code) and **permission creep** (a workflow
token with more scope than the job needs). This contract does NOT
claim protection against a compromised pinned commit, runner
compromise, or GitHub itself.

## Law

Every `uses:` reference must be pinned to a **40-hex commit SHA** with
a trailing `# vX` version comment, recorded in
`evidence/ACTION_SHA_RESOLUTION.json` (action, tag, resolved SHA,
method). Every workflow must declare **explicit top-level
permissions**. `write-all` is forbidden anywhere. A **non-release**
workflow may hold a `write` scope only if justified here as a literal
token `<file>:<scope>:write`.

Enforced by `scripts/audit_workflow_trust.py` (stdlib-only, so it does
not bootstrap trust through an uninstalled dependency), wired into
`ci.yml` before dependency install, with negative tests in
`tests/test_workflow_trust.py`.

## Current state (PR K)

All five workflows (`ci`, `conference-smoke`, `indi-demo-gate`,
`platform-demo`, `v7-readiness`) are SHA-pinned and carry
`permissions:\n  contents: read`. No release workflow exists yet (PR N).
No write permission is in use, so the justified-write allowlist below
is intentionally empty.

## Justified non-release write permissions

(none — add as `<file>:<scope>:write` with rationale when first needed)

## K.1 — evidence binding (residual gap closed)

PR K pinned SHAs and recorded action *names*; it did not prove each
workflow ref equals the recorded SHA. K.1 closes this: for every
`uses:` line the audit now requires the action recorded, the workflow
SHA byte-equal to `resolved_sha`, and the comment exactly `# <tag>`
equal to the recorded `tag`; the resolution evidence is itself
schema-validated (lowercase-40-hex SHA, no duplicates, source_ref↔tag,
timestamps). `evidence/WORKFLOW_TRUST_AUDIT.json` reports
`sha_binding` and `version_comment_binding` status explicitly.

## What this does not prove

SHA pinning prevents mutable tag substitution only when workflow refs
are bound to recorded `resolved_sha` values by
`audit_workflow_trust.py`. It does not prove the pinned action code is
safe. SHA resolution was done once via the GitHub API and recorded; it
is not re-resolved each run (that would re-introduce a network trust
point). Re-pinning to newer SHAs is a deliberate, reviewed change.
