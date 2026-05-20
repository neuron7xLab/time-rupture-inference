# SPDX-License-Identifier: MIT
"""List stale remote branches by naming pattern.

This is intentionally read-only. It prints deletion candidates for operator
review and never deletes branches itself. Humans apparently enjoy leaving dead
execution traces around, so the tool at least labels the ghosts.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class BranchInfo:
    name: str
    commit_date: datetime


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def list_remote_branches(pattern: str) -> list[BranchInfo]:
    fmt = "%(refname:short)|%(committerdate:iso-strict)"
    out = _git("for-each-ref", "refs/remotes/origin", f"--format={fmt}")
    regex = re.compile(pattern)
    branches: list[BranchInfo] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        raw_name, raw_date = line.split("|", 1)
        name = raw_name.removeprefix("origin/")
        if name == "HEAD" or not regex.fullmatch(name):
            continue
        commit_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        branches.append(BranchInfo(name=name, commit_date=commit_date))
    return sorted(branches, key=lambda item: item.commit_date)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", default=r"pr-.*")
    parser.add_argument("--max-age-days", type=int, default=7)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    branches = list_remote_branches(args.pattern)
    stale = [
        branch
        for branch in branches
        if (now - branch.commit_date).days >= args.max_age_days
    ]
    if not stale:
        print("STALE BRANCHES — none")
        return 0
    print("STALE BRANCH CANDIDATES — review manually before deletion")
    for branch in stale:
        age_days = (now - branch.commit_date).days
        print(f"{branch.name}\t{age_days}d\t{branch.commit_date.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
