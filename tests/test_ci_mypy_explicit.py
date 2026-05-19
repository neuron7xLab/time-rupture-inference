# SPDX-License-Identifier: MIT
"""Phase 6 core — CI strictness must be explicit, not config-dependent.
Fails if any workflow invokes bare `mypy` (so pyproject tampering
cannot silently weaken typing) and requires the explicit strict
target."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CI = ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_invokes_mypy_strict_explicitly():
    txt = CI.read_text()
    assert "mypy --strict src/ctios" in txt, "CI must call mypy explicitly"


def test_ci_has_no_bare_mypy_run_step():
    for ln in CI.read_text().splitlines():
        s = ln.strip()
        # a run step that is exactly `mypy` (optionally `run: mypy`)
        assert not re.fullmatch(r"(run:\s*)?mypy", s), (
            f"bare config-dependent mypy in CI: {ln!r}"
        )


def test_explicit_target_passes_locally():
    import subprocess

    r = subprocess.run(
        ["mypy", "--strict", "src/ctios"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
