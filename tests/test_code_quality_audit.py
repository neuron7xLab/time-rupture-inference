# SPDX-License-Identifier: MIT
"""WP2 — the code-quality audit is executable and itself tested: it
must fire on a planted defect, not merely claim cleanliness."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.code_quality_audit import as_payload, run_audit  # noqa: E402


def test_repo_is_clean_under_executable_audit():
    assert run_audit() == []


def test_payload_lists_all_checks():
    p = as_payload([])
    assert p["clean"] is True
    assert {"bare_except", "broad_except", "mutable_default",
            "shell_no_set_euo", "tracked_generated_evidence"} <= set(
        p["checks"]
    )


def test_audit_fires_on_planted_defects(tmp_path, monkeypatch):
    import ctios.code_quality_audit as cqa

    bad = ROOT / "src" / "ctios" / "_tmp_defect.py"
    bad.write_text(
        "def f(x=[]):\n"
        "    try:\n"
        "        return x\n"
        "    except Exception:\n"
        "        pass\n"
    )
    try:
        codes = {f.check for f in cqa.run_audit() if "_tmp_defect" in f.path}
        assert "mutable_default" in codes
        assert "broad_except" in codes
        assert "except_pass" in codes
    finally:
        bad.unlink()
