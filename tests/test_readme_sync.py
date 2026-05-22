# SPDX-License-Identifier: MIT
"""Kills the recurring README test-count drift class: the badge and the
structure line must equal the real collected count, enforced — not
babysat. CI fails on any drift."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _collected_count() -> int:
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--co", "-q", "-o", "addopts="],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    m = re.search(r"(\d+) tests collected", out)
    assert m, f"could not parse collected count from:\n{out[-400:]}"
    return int(m.group(1))


def test_readme_counts_match_reality():
    n = _collected_count()
    readme = (ROOT / "README.md").read_text()
    badge = re.search(r"tests-(\d+)_passing", readme, flags=re.IGNORECASE)
    if badge:
        prose = re.search(r"(\d+) tests incl", readme)
        assert int(badge.group(1)) == n, f"README badge != {n}"
        assert prose and int(prose.group(1)) == n, f"README structure count != {n}"
    else:
        assert "tests-CI_VERIFIED" in readme
