# SPDX-License-Identifier: MIT
"""Fail-closed CI watcher contract. The decision core never emits
SUCCESS without positive proof; a transient/empty reply is never
trusted; a timeout exits non-zero. tests/ is outside claims_lint
scope."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ci_gate_watch as w  # noqa: E402

EXP = {"gate", "platform-demo"}
SHA = "a" * 40


def _r(name, status, concl, sha=SHA):
    return {"name": name, "status": status, "conclusion": concl,
            "sha": sha}


def test_empty_rows_is_pending_not_success():
    assert w.evaluate([], EXP, SHA)[0] == "PENDING"


def test_wrong_sha_is_pending():
    rows = [_r("gate", "completed", "success", "b" * 40),
            _r("platform-demo", "completed", "success", "b" * 40)]
    assert w.evaluate(rows, EXP, SHA)[0] == "PENDING"


def test_missing_expected_workflow_is_pending():
    assert w.evaluate([_r("gate", "completed", "success")],
                       EXP, SHA)[0] == "PENDING"


def test_in_progress_is_pending():
    rows = [_r("gate", "completed", "success"),
            _r("platform-demo", "in_progress", "")]
    assert w.evaluate(rows, EXP, SHA)[0] == "PENDING"


def test_failure_conclusion_is_fail():
    rows = [_r("gate", "completed", "failure"),
            _r("platform-demo", "completed", "success")]
    st, d = w.evaluate(rows, EXP, SHA)
    assert st == "FAIL" and "gate" in d


def test_completed_non_success_is_fail():
    rows = [_r("gate", "completed", "neutral"),
            _r("platform-demo", "completed", "success")]
    assert w.evaluate(rows, EXP, SHA)[0] == "FAIL"


def test_all_success_on_sha_is_success():
    rows = [_r("gate", "completed", "success"),
            _r("platform-demo", "completed", "success")]
    assert w.evaluate(rows, EXP, SHA)[0] == "SUCCESS"


def test_extra_workflow_does_not_block_success():
    rows = [_r("gate", "completed", "success"),
            _r("platform-demo", "completed", "success"),
            _r("conference-smoke", "completed", "success")]
    assert w.evaluate(rows, EXP, SHA)[0] == "SUCCESS"


def test_transient_poll_never_yields_success(monkeypatch):
    # _poll always None (API down): watch must time out non-zero,
    # never exit 0 from absence of evidence.
    monkeypatch.setattr(w, "_poll", lambda *a, **k: None)
    monkeypatch.setattr(w.time, "sleep", lambda *_: None)
    rc = w.watch("br", EXP, SHA, timeout_s=0, interval_s=0)
    assert rc == 2


def test_failure_short_circuits_to_exit_1(monkeypatch):
    rows = [_r("gate", "completed", "failure"),
            _r("platform-demo", "completed", "success")]
    monkeypatch.setattr(w, "_poll", lambda *a, **k: rows)
    monkeypatch.setattr(w.time, "sleep", lambda *_: None)
    assert w.watch("br", EXP, SHA, timeout_s=5, interval_s=0) == 1


def test_success_path_exits_0(monkeypatch):
    rows = [_r("gate", "completed", "success"),
            _r("platform-demo", "completed", "success")]
    monkeypatch.setattr(w, "_poll", lambda *a, **k: rows)
    monkeypatch.setattr(w.time, "sleep", lambda *_: None)
    assert w.watch("br", EXP, SHA, timeout_s=5, interval_s=0) == 0
