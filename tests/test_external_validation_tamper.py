# SPDX-License-Identifier: MIT
"""WP4 — a real external run cannot be faked by editing JSON. Only a
schema-valid proof bundle + the attested flag together count."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.external_validation import (  # noqa: E402
    external_state,
    real_external_run_attested,
)
from ctios.readiness_score import compute_readiness  # noqa: E402

_H = "b" * 64


def _flag(tmp_path, v):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"real_external_collaborator_run": v}))
    return p


def _bundle(tmp_path, **over):
    base = {
        "reviewer_id": "ext",
        "reviewer_pubkey_sha256": _H,
        "timestamp_utc": "2026-05-19T00:00:00Z",
        "repo_commit": "deadbee",
        "spec_sha256": _H,
        "verdict_sha256": _H,
        "no_leakage_attestation": True,
        "command_transcript_sha256": _H,
    }
    base.update(over)
    p = tmp_path / "bundle.json"
    p.write_text(json.dumps(base))
    return p


def test_manual_flag_true_without_bundle_is_insufficient(tmp_path):
    assert real_external_run_attested(
        status_path=_flag(tmp_path, True), bundle_path=tmp_path / "absent.json"
    ) is False
    r = compute_readiness(
        gates_all_pass=True,
        status_path=_flag(tmp_path, True),
        bundle_path=tmp_path / "absent.json",
    )
    assert r.status == "CONDITIONALLY_READY"


def test_bundle_without_flag_is_insufficient(tmp_path):
    st = external_state(
        status_path=_flag(tmp_path, False),
        bundle_path=_bundle(tmp_path),
    )
    assert st.real_run_attested is False
    assert "both required" in st.reason


def test_missing_required_field_rejected(tmp_path):
    b = _bundle(tmp_path)
    d = json.loads(b.read_text())
    del d["no_leakage_attestation"]
    b.write_text(json.dumps(d))
    st = external_state(status_path=_flag(tmp_path, True), bundle_path=b)
    assert st.real_run_attested is False
    assert "missing field" in st.reason


def test_no_leakage_must_be_exactly_true(tmp_path):
    st = external_state(
        status_path=_flag(tmp_path, True),
        bundle_path=_bundle(tmp_path, no_leakage_attestation="yes"),
    )
    assert st.real_run_attested is False


def test_non_sha_hashes_rejected(tmp_path):
    st = external_state(
        status_path=_flag(tmp_path, True),
        bundle_path=_bundle(tmp_path, verdict_sha256="not-a-hash"),
    )
    assert st.real_run_attested is False


def test_valid_bundle_plus_flag_attests(tmp_path):
    st = external_state(
        status_path=_flag(tmp_path, True), bundle_path=_bundle(tmp_path)
    )
    assert st.real_run_attested is True


def test_repo_default_state_is_pending_no_bundle_present():
    # The committed repo must NOT ship a bundle; status stays pending.
    assert not (ROOT / "evidence" / "EXTERNAL_VALIDATION_BUNDLE.json").exists()
    assert real_external_run_attested() is False
    d = json.loads(
        (ROOT / "evidence" / "external_validation_status.json").read_text()
    )
    assert d["status"] == "EXTERNAL_RUN_PENDING"
