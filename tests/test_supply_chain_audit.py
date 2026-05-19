# SPDX-License-Identifier: MIT
"""PR O — supply-chain aggregate + Scorecard-honesty contract.

Every negative case fails closed; the live repo passes. The aggregate
must (a) surface any single component failure, (b) never emit PASS
while any root is FAIL, (c) reject a fabricated Scorecard score, (d)
reject status RUN without a real artifact, (e) reject a missing
status file.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import verify_scorecard_prerequisites as vsp  # noqa: E402

from ctios import supply_chain_audit as sca  # noqa: E402


# ---- live repo ----
def test_live_scorecard_record_is_honest():
    assert vsp.audit() == []


def test_live_aggregate_all_pass():
    rep = sca.audit()
    assert rep["all_pass"] is True, [
        c for c in rep["components"] if c["status"] == "FAIL"
    ]
    # honest level must NOT overclaim
    low = str(rep["honest_level"]).lower()
    assert "not hash-locked" in low and "not l3" in low
    assert "OpenSSF Scorecard score (recorded NOT_RUN)" in rep[
        "not_claimed"
    ]


# ---- Scorecard honesty: the 4 required failing cases ----
def _write(tmp_path, monkeypatch, obj):
    p = tmp_path / "SCORECARD_STATUS.json"
    p.write_text(json.dumps(obj))
    monkeypatch.setattr(vsp, "_STATUS", p)
    return p


def test_fabricated_score_while_not_run_is_rejected(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch,
           {"status": "NOT_RUN", "score": 9.1, "reason": "x"})
    assert any("fabricated" in p for p in vsp.audit())


def test_not_run_without_reason_is_rejected(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch,
           {"status": "NOT_RUN", "score": None, "reason": ""})
    assert any("without a recorded reason" in p for p in vsp.audit())


def test_run_without_artifact_is_rejected(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, {
        "status": "RUN", "score": 7.0,
        "tool_version": "v5.0.0", "scorecard_json": "nope/missing.json",
    })
    assert any("scorecard_json" in p for p in vsp.audit())


def test_run_without_numeric_score_is_rejected(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, {
        "status": "RUN", "score": "great",
        "tool_version": "v5.0.0", "scorecard_json": None,
    })
    assert any("numeric score" in p for p in vsp.audit())


def test_unknown_status_is_rejected(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, {"status": "MAYBE"})
    assert any("must be NOT_RUN or RUN" in p for p in vsp.audit())


def test_missing_status_file_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(vsp, "_STATUS", tmp_path / "absent.json")
    assert any("missing" in p for p in vsp.audit())


# ---- aggregate fail-closed on a single broken root ----
def test_aggregate_fails_closed_if_one_component_fails(monkeypatch):
    orig = sca._run

    def fake(argv):
        if "verify_ci_deps.py" in argv[0]:
            return 1, "DEPENDENCY TRUST — FAIL (injected)"
        return orig(argv)

    monkeypatch.setattr(sca, "_run", fake)
    rep = sca.audit()
    assert rep["all_pass"] is False
    dep = [c for c in rep["components"]
           if c["component"] == "dependency_trust"][0]
    assert dep["status"] == "FAIL" and dep["exit"] == 1
