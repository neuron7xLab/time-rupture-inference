# SPDX-License-Identifier: MIT
"""WP4 — readiness scoring cannot deceive itself: the number never
overrides a blocking fact; external portability is capped without a
real external run; productizable needs >=2 external use cases."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.readiness_score import compute_readiness  # noqa: E402


def _status(tmp_path, real: bool) -> Path:
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"real_external_collaborator_run": real}))
    return p


def test_all_gates_pass_no_external_run_is_conditionally_ready(tmp_path):
    r = compute_readiness(
        gates_all_pass=True, status_path=_status(tmp_path, False)
    )
    assert r.status == "CONDITIONALLY_READY"
    assert r.subscores["external_portability"] == 5  # capped
    assert "capped" in r.score_cap_reason


def test_external_run_complete_plus_gates_is_ready(tmp_path):
    r = compute_readiness(
        gates_all_pass=True, status_path=_status(tmp_path, True)
    )
    assert r.status == "READY"
    assert r.subscores["external_portability"] == 10  # uncapped
    assert r.blocking_facts == []


def test_productizable_requested_without_use_cases_fails(tmp_path):
    r = compute_readiness(
        gates_all_pass=True,
        productizable_requested=True,
        external_use_cases=0,
        status_path=_status(tmp_path, True),
    )
    assert r.status != "PRODUCTIZABLE"
    assert any("productizable" in b for b in r.blocking_facts)


def test_productizable_with_two_use_cases_and_external_run(tmp_path):
    r = compute_readiness(
        gates_all_pass=True,
        productizable_requested=True,
        external_use_cases=2,
        status_path=_status(tmp_path, True),
    )
    assert r.status == "PRODUCTIZABLE"


def test_high_score_cannot_override_blocking_fact(tmp_path):
    r = compute_readiness(
        gates_all_pass=True, status_path=_status(tmp_path, False)
    )
    # technical subtotal is high, but a blocking fact pins the status.
    assert r.technical_score >= 80
    assert r.status == "CONDITIONALLY_READY"
    assert r.status not in ("READY", "PRODUCTIZABLE")


def test_failing_gates_is_not_ready(tmp_path):
    r = compute_readiness(
        gates_all_pass=False, status_path=_status(tmp_path, True)
    )
    assert r.status == "NOT_READY"
