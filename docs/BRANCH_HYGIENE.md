# Branch Hygiene Policy

## Purpose

Branch hygiene removes stale execution traces without deleting valid lineage.

A stale branch is not evidence. It is an old possible future that did not become the present. Leaving it alive creates operator noise, stale CI signals, and duplicate recovery paths.

## Rules

### Merged PR branch

After merge:

```text
delete remote branch unless it is a protected long-lived branch
```

### Closed unmerged duplicate

After closing:

```text
comment why it was superseded, then delete branch if no active dependent PR exists
```

### Stale branch with no open PR

Delete only after confirming:

- no open PR points to it
- branch is superseded by merged work
- no unique artifact must be preserved
- compare does not reveal required unmerged content

### Never resurrect silently

A stale branch may not be merged directly into `main`.

If useful work remains, extract it into a new branch with a new PR and a fresh boundary.

## Operator command

```bash
python tools/list_stale_branches.py --pattern 'pr-*' --max-age-days 7
```

This tool lists candidates only. It does not delete anything.

Deletion remains an explicit operator action:

```bash
git push origin --delete <branch>
```

## Current known action

Candidate stale branch:

```text
pr-50/external-reproduction-bundle-intake-clean
```

Recommended action after final confirmation:

```bash
git push origin --delete pr-50/external-reproduction-bundle-intake-clean
```

## Boundary

Branch deletion is repository hygiene, not scientific deletion.

RED tags, evidence artifacts, negative results, and release lineage must remain preserved.
