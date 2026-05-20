# Main Protection Ruleset

## Purpose

This runbook defines the required GitHub repository ruleset for protecting `main`.

The repository already has strong CI. The ruleset makes those checks enforceable before merge instead of relying on operator discipline.

## Target

```text
Branch: main
Enforcement: active
Bypass: disabled by default
```

## Required branch rules

Enable these rules for `main`:

- require pull request before merge
- require approvals before merge
- require CODEOWNER review
- require conversation resolution before merge
- require status checks to pass before merge
- require branch to be up to date before merge
- block force pushes
- block branch deletion
- restrict direct pushes to `main`
- require signed commits if the local signing workflow is ready
- require linear history if squash-only merge is selected

## Required status checks

The following checks must be required before merge:

```text
gate / proof-of-life (3.11)
gate / proof-of-life (3.12)
gate / external-adversarial
v7-readiness / v7-readiness
platform-demo / platform-demo
conference-smoke / conference-smoke
indi-demo-gate / indi-demo
```

If GitHub displays push/pull_request variants, select the check names produced on pull requests.

## Merge policy

Preferred:

```text
squash merge only
```

Allowed if repository history policy requires it:

```text
rebase merge
```

Avoid:

```text
merge commits for routine work
```

## Admin bypass policy

Default:

```text
no bypass
```

Emergency bypass may be used only for:

- failed GitHub Actions infrastructure unrelated to repository code
- urgent rollback of a harmful merge
- repository access recovery

Every bypass must be followed by a governance issue recording:

- reason
- affected commit
- skipped checks
- rollback or follow-up plan

## Protected surfaces

Any change touching these paths must be reviewed as a control-plane change:

```text
.github/**
scripts/**
tools/**
claims.yaml
invariants.yaml
provenance_manifest.json
requirements*.txt
pyproject.toml
README.md
SECURITY.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
docs/governance/**
```

## Verification after enabling

Open a test PR that changes documentation only and verify:

- required checks appear
- merge button is blocked while checks are pending
- unresolved conversation blocks merge
- CODEOWNERS are requested
- direct push to `main` is blocked

## Boundary

This runbook documents required repository settings. It does not modify GitHub settings by itself.
