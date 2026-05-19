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

_H = "a" * 64


def _status(tmp_path, real: bool) -> Path:
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"real_external_collaborator_run": real}))
    return p


def _valid_bundle(tmp_path) -> Path:
    p = tmp_path / "bundle.json"
    p.write_text(
        json.dumps(
            {
                "reviewer_id": "ext-reviewer",
                "reviewer_pubkey_sha256": _H,
                "timestamp_utc": "2026-05-19T00:00:00Z",
                "repo_commit": "abcdef1",
                "spec_sha256": _H,
                "verdict_sha256": _H,
                "no_leakage_attestation": True,
                "command_transcript_sha256": _H,
            }
        )
    )
    return p


def test_all_gates_pass_no_external_run_is_conditionally_ready(tmp_path):
    r = compute_readiness(
        gates_all_pass=True, status_path=_status(tmp_path, False)
    )
    assert r.status == "CONDITIONALLY_READY"
    assert r.subscores["external_portability"] == 5  # capped
    assert "capped" in r.score_cap_reason


def test_flag_true_without_bundle_is_still_conditionally_ready(tmp_path):
    # Anti-tamper: flipping the status flag alone must NOT yield READY.
    r = compute_readiness(
        gates_all_pass=True, status_path=_status(tmp_path, True)
    )
    assert r.status == "CONDITIONALLY_READY"
    assert r.subscores["external_portability"] == 5  # still capped


def test_external_run_complete_with_valid_bundle_is_ready(tmp_path):
    r = compute_readiness(
        gates_all_pass=True,
        status_path=_status(tmp_path, True),
        bundle_path=_valid_bundle(tmp_path),
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
        bundle_path=_valid_bundle(tmp_path),
    )
    assert r.status != "PRODUCTIZABLE"
    assert any("productizable" in b for b in r.blocking_facts)


def test_productizable_with_two_use_cases_and_external_run(tmp_path):
    r = compute_readiness(
        gates_all_pass=True,
        productizable_requested=True,
        external_use_cases=2,
        status_path=_status(tmp_path, True),
        bundle_path=_valid_bundle(tmp_path),
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
