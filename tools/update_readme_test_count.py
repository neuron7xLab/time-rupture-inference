# SPDX-License-Identifier: MIT
"""Update README test-count badge and structure line from pytest collection.

This preserves the existing fail-closed README drift gate while giving the
operator one controlled updater instead of a manual badge/prose hunt.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def collected_count() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--co", "-q", "-o", "addopts="],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    match = re.search(r"(\d+) tests collected", result.stdout)
    if not match:
        raise RuntimeError(f"could not parse pytest collection count:\n{result.stdout[-800:]}")
    return int(match.group(1))


def render(readme: str, count: int) -> str:
    readme, badge_changes = re.subn(
        r"tests-\d+_PASSING",
        f"tests-{count}_PASSING",
        readme,
        count=1,
    )
    readme, prose_changes = re.subn(
        r"tests/\s+\d+ tests incl\.",
        f"tests/       {count} tests incl.",
        readme,
        count=1,
    )
    if badge_changes != 1:
        raise RuntimeError("README test badge pattern not found")
    if prose_changes != 1:
        raise RuntimeError("README structure test-count pattern not found")
    return readme


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write README.md in place")
    args = parser.parse_args()

    count = collected_count()
    current = README.read_text()
    updated = render(current, count)
    if args.write:
        README.write_text(updated)
        print(f"README test count updated to {count}")
    elif current != updated:
        print(f"README test count drift: run {Path(__file__).as_posix()} --write")
        return 1
    else:
        print(f"README test count OK ({count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
