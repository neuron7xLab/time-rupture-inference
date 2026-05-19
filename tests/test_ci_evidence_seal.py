# SPDX-License-Identifier: MIT
"""CI evidence seal contract — no network in tests. SUCCESS only on
proven all-green for the exact sha; absence of a run is never success;
an untrustworthy fetch refuses to seal."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ci_evidence_seal as s  # noqa: E402

EXP = {"gate", "platform-demo"}
SHA = "c" * 40


def _r(name, concl, sha=SHA):
    return {"name": name, "status": "completed", "conclusion": concl,
            "sha": sha, "run_id": "1", "url": "u"}


def test_all_success_seals_rc0():
    rows = [_r("gate", "success"), _r("platform-demo", "success")]
    rc, doc = s.seal("main", SHA, EXP, rows)
    assert rc == 0 and doc["state"] == "SUCCESS"
    assert {r["name"] for r in doc["runs"]} == EXP
    assert doc["commit"] == SHA and "reverify" in doc


def test_missing_workflow_is_not_success():
    rc, doc = s.seal("main", SHA, EXP, [_r("gate", "success")])
    assert rc == 1 and doc["state"] != "SUCCESS"


def test_failure_conclusion_seals_fail():
    rows = [_r("gate", "failure"), _r("platform-demo", "success")]
    rc, doc = s.seal("main", SHA, EXP, rows)
    assert rc == 1 and doc["state"] == "FAIL"


def test_wrong_sha_runs_not_counted():
    rows = [_r("gate", "success", "d" * 40),
            _r("platform-demo", "success", "d" * 40)]
    rc, doc = s.seal("main", SHA, EXP, rows)
    assert rc == 1 and doc["runs"] == []


def test_untrustworthy_fetch_refuses_to_seal(monkeypatch, capsys):
    monkeypatch.setattr(s, "_fetch", lambda *a, **k: None)
    monkeypatch.setattr(
        sys, "argv",
        ["x", "--branch", "main", "--sha", SHA, "--expect", "gate"],
    )
    rc = s.main()
    assert rc == 2
    assert "refusing to seal from absence" in capsys.readouterr().out
