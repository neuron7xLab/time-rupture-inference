# SPDX-License-Identifier: MIT
"""Phase 1 — the verifier manifest pins critical verifiers and the
independent stdlib-only root works without importing ctios."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import verifier_manifest as vm  # noqa: E402


def test_lock_exists_and_matches_head():
    assert (ROOT / "verifier_manifest.lock").exists()
    assert vm.verify() == []  # generator-gate clean at HEAD


def test_all_critical_files_pinned_and_present():
    locked = vm.locked_hashes()
    for rel in vm.CRITICAL:
        assert rel in locked, f"{rel} not pinned"
        assert (ROOT / rel).exists()
    assert len(vm.CRITICAL) >= 12


def test_static_checker_is_stdlib_only_no_ctios():
    src = (ROOT / "tools" / "check_verifier_manifest_static.py").read_text()
    assert "import ctios" not in src and "from ctios" not in src
    assert "yaml" not in src  # no repo-specific deps


def test_static_checker_runs_and_passes_at_head():
    r = subprocess.run(
        [sys.executable, "tools/check_verifier_manifest_static.py",
         "--repo", "."],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK" in r.stdout


def test_external_root_copy_is_consistent():
    a = (ROOT / "verifier_manifest.lock").read_text()
    b = (ROOT / "release" / "verifier-root"
         / "verifier_manifest.lock").read_text()
    assert a == b  # exported root must match the live lock
