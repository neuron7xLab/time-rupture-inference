# SPDX-License-Identifier: MIT
"""Phase 2 — verifier-capture red team. Every mutation that would
silently weaken a verifier is detected by the independent static root
(run hermetically against a tmp copy; real files untouched)."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "tools" / "check_verifier_manifest_static.py"
LOCK = ROOT / "verifier_manifest.lock"


def _mini_repo(tmp_path, mutate_rel=None, new_text=None,
               drop_change_report=True):
    """A minimal copy: the pinned files + lock + checker."""
    r = tmp_path / "repo"
    for line in LOCK.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        _, rel = line.split(None, 1)
        dst = r / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
    shutil.copy2(LOCK, r / "verifier_manifest.lock")
    if mutate_rel:
        (r / mutate_rel).write_text(new_text)
    return r


def _static(repo):
    return subprocess.run(
        [sys.executable, str(CHECK), "--repo", str(repo)],
        capture_output=True, text=True, check=False,
    )


def test_unmutated_copy_passes(tmp_path):
    assert _static(_mini_repo(tmp_path)).returncode == 0


def test_claims_lint_weakened_is_detected(tmp_path):
    r = _mini_repo(
        tmp_path, "scripts/claims_lint.py",
        "def main():\n    print('CLAIMS LINT — PASS')\n    return 0\n",
    )
    out = _static(r)
    assert out.returncode == 1
    assert "MISMATCH scripts/claims_lint.py" in out.stdout


def test_readiness_score_weakened_is_detected(tmp_path):
    r = _mini_repo(
        tmp_path, "src/ctios/readiness_score.py",
        "def compute_readiness(**k):\n    return 'READY'\n",
    )
    assert _static(r).returncode == 1


def test_artifact_assertions_weakened_is_detected(tmp_path):
    r = _mini_repo(
        tmp_path, "src/ctios/artifact_assertions.py",
        "def assert_artifact(*a, **k):\n    return {}\n",
    )
    assert _static(r).returncode == 1


def test_deep_audit_script_weakened_is_detected(tmp_path):
    r = _mini_repo(
        tmp_path, "scripts/deep_mechanism_audit.sh",
        "#!/usr/bin/env bash\nexit 0\n",
    )
    assert _static(r).returncode == 1


def test_static_checker_self_tamper_is_detected(tmp_path):
    # the checker pins itself; replacing it with an always-OK stub is
    # caught because its own hash no longer matches the lock.
    r = _mini_repo(
        tmp_path, "tools/check_verifier_manifest_static.py",
        "import sys\nprint('VERIFIER MANIFEST — OK')\nsys.exit(0)\n",
    )
    # run the ORIGINAL trusted checker against the tampered copy
    out = subprocess.run(
        [sys.executable, str(CHECK), "--repo", str(r)],
        capture_output=True, text=True, check=False,
    )
    assert out.returncode == 1
    assert "tools/check_verifier_manifest_static.py" in out.stdout


def test_lock_update_without_change_report_fails_generator_gate(
    tmp_path, monkeypatch
):
    # generator-gate: a changed verifier with an updated lock but no
    # VERIFIER_CHANGE_REPORT must FAIL.
    sys.path.insert(0, str(ROOT / "tools"))
    import importlib

    vm = importlib.import_module("verifier_manifest")
    monkeypatch.setattr(vm, "_ROOT", tmp_path)
    monkeypatch.setattr(vm, "_LOCK", tmp_path / "verifier_manifest.lock")
    monkeypatch.setattr(
        vm, "_CHANGE_REPORT", tmp_path / "docs/reports/VERIFIER_CHANGE_REPORT.md"
    )
    monkeypatch.setattr(vm, "CRITICAL", ["v.py"])
    (tmp_path / "v.py").write_text("# original\n")
    vm.write()  # lock pins original
    (tmp_path / "v.py").write_text("# WEAKENED\n")  # change, no report
    problems = vm.verify()
    assert any("not updated" in p or "without" in p for p in problems)
