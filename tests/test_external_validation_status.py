# SPDX-License-Identifier: MIT
"""WP3 — the external-validation status file is the single source of
truth for whether a real external run happened. Claiming READY while
real_external_collaborator_run=false must be impossible."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.readiness_score import compute_readiness  # noqa: E402

STATUS = ROOT / "evidence" / "external_validation_status.json"


def test_status_file_exists_and_well_formed():
    d = json.loads(STATUS.read_text())
    for k in (
        "status",
        "simulated_external_pack_passed",
        "real_external_collaborator_run",
        "claim_upgrade_allowed",
    ):
        assert k in d


def test_default_state_is_pending_and_not_upgraded():
    d = json.loads(STATUS.read_text())
    assert d["real_external_collaborator_run"] is False
    assert d["claim_upgrade_allowed"] is False
    assert d["status"] == "EXTERNAL_RUN_PENDING"


def test_ready_is_impossible_without_real_external_run(tmp_path):
    fake = tmp_path / "s.json"
    fake.write_text(json.dumps({"real_external_collaborator_run": False}))
    r = compute_readiness(gates_all_pass=True, status_path=fake)
    assert r.status == "CONDITIONALLY_READY"
    assert any("real_external" in b for b in r.blocking_facts)
    assert r.status != "READY"


def test_simulated_pack_passing_does_not_upgrade(tmp_path):
    fake = tmp_path / "s.json"
    fake.write_text(
        json.dumps(
            {
                "real_external_collaborator_run": False,
                "simulated_external_pack_passed": True,
            }
        )
    )
    r = compute_readiness(gates_all_pass=True, status_path=fake)
    assert r.status == "CONDITIONALLY_READY"


def test_repo_status_yields_conditionally_ready_today():
    r = compute_readiness(gates_all_pass=True, status_path=STATUS)
    assert r.status == "CONDITIONALLY_READY"
