# SPDX-License-Identifier: MIT
"""PR L — dependency trust contract: CI consumes the pinned lock, no
loose installs, mypy/types declared, no hash-lock overclaim. Negative
cases fail closed; live repo passes."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import re  # noqa: E402

import verify_ci_deps as vcd  # noqa: E402


def test_live_repo_passes():
    assert vcd.audit() == []


def test_lock_exists_and_no_hashes_so_level1():
    lock = ROOT / "requirements-ci.lock"
    assert lock.exists()
    # LEVEL_1: no REAL pip hash lines (the header prose mentions the
    # word '--hash'; ignore comments — same rule as the guard).
    real = [
        ln for ln in lock.read_text().splitlines()
        if not ln.strip().startswith("#")
        and re.search(r"--hash=sha256:[0-9a-f]{64}", ln)
    ]
    assert real == [] and not vcd._lock_has_hashes()


def test_all_workflows_consume_lock_no_loose_install():
    for wf in (ROOT / ".github" / "workflows").glob("*.yml"):
        for ln in wf.read_text().splitlines():
            m = re.search(r"pip install\b(.*)$", ln)
            if not m:
                continue
            a = m.group(1)
            ok = (
                "requirements-ci.lock" in a
                or "--upgrade pip" in a
                or "-e . --no-deps" in a
            )
            # release.yml may pin the build tool (name==ver), mirroring
            # verify_ci_deps' narrow documented exception.
            if not ok and "release" in wf.name:
                toks = [
                    t.strip('"').strip("'")
                    for t in a.split()
                    if not t.startswith("-")
                    and t not in ("pip", "python")
                ]
                ok = bool(toks) and all(
                    re.fullmatch(r"[\w.\-]+==[\w.\-]+", t) for t in toks
                )
            assert ok, f"{wf.name}: loose install: {ln.strip()}"


def test_mypy_and_types_declared():
    pp = (ROOT / "pyproject.toml").read_text()
    dev = re.search(r"(?ms)^dev\s*=\s*\[(.*?)\]", pp).group(1)
    assert "mypy" in dev and "types-PyYAML" in dev


def test_loose_install_is_rejected(tmp_path, monkeypatch):
    bad = tmp_path / "wf"
    bad.mkdir()
    (bad / "x.yml").write_text(
        "jobs:\n  j:\n    steps:\n"
        "      - run: pip install -q numpy pytest\n"
    )
    monkeypatch.setattr(vcd, "_WF", bad)
    assert any("loose pip install" in p for p in vcd.audit())


def test_missing_lock_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(vcd, "_LOCK", tmp_path / "absent.txt")
    assert any("requirements-ci.lock missing" in p for p in vcd.audit())


def test_undeclared_mypy_is_rejected(tmp_path, monkeypatch):
    fake = tmp_path / "pp.toml"
    fake.write_text('dev = ["pytest>=8", "ruff>=0.6"]\n')
    monkeypatch.setattr(vcd, "_PYPROJECT", fake)
    probs = vcd.audit()
    assert any("mypy not declared" in p for p in probs)


def test_fake_hash_lock_claim_is_rejected(tmp_path, monkeypatch):
    doc = tmp_path / "c.md"
    doc.write_text("This build is hash-locked via --require-hashes.\n")
    monkeypatch.setattr(vcd, "_CONTRACT", doc)
    assert any("hash-locking" in p for p in vcd.audit())


def test_release_pinned_build_tool_allowed(tmp_path, monkeypatch):
    bad = tmp_path / "wf"
    bad.mkdir()
    (bad / "release.yml").write_text(
        "permissions:\n  contents: write\n"
        "  - run: pip install -q -r requirements-ci.lock\n"
        '  - run: python -m pip install -q "build==1.5.0"\n'
    )
    monkeypatch.setattr(vcd, "_WF", bad)
    probs = [p for p in vcd.audit() if "loose pip install" in p]
    assert probs == [], probs


def test_release_unpinned_build_tool_rejected(tmp_path, monkeypatch):
    bad = tmp_path / "wf"
    bad.mkdir()
    (bad / "release.yml").write_text(
        "permissions:\n  contents: write\n"
        "  - run: pip install -q -r requirements-ci.lock\n"
        "  - run: python -m pip install -q build\n"
    )
    monkeypatch.setattr(vcd, "_WF", bad)
    assert any("loose pip install" in p for p in vcd.audit())


def test_non_release_pinned_install_still_rejected(tmp_path, monkeypatch):
    bad = tmp_path / "wf"
    bad.mkdir()
    (bad / "ci.yml").write_text(
        "  - run: pip install -q numpy==2.4.3\n"
    )
    monkeypatch.setattr(vcd, "_WF", bad)
    assert any("loose pip install" in p for p in vcd.audit())
