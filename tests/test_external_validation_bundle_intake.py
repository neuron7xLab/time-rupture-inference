# SPDX-License-Identifier: MIT
"""External validation bundle intake helper must fail closed.

The authoritative readiness/claim-upgrade guard remains
ctios.external_validation. This test covers only the reviewer helper in
``tools/`` so the signed provenance root stays unchanged.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_external_validation_bundle.py"
H = "a" * 64


def _bundle(tmp_path: Path, **overrides) -> Path:
    obj = {
        "reviewer_id": "external-team",
        "reviewer_pubkey_sha256": H,
        "timestamp_utc": "2026-05-20T00:00:00Z",
        "repo_commit": "0a91f5e",
        "spec_sha256": H,
        "verdict_sha256": H,
        "no_leakage_attestation": True,
        "command_transcript_sha256": H,
        "environment": {"os": "Ubuntu 24.04", "python": "3.12.3"},
        "commands_run": ["pytest tests -q"],
        "observed_metrics": {
            "learned_post_mae": 0.8830,
            "injected_post_mae": 8.0028,
            "oracle_post_mae": 0.7933,
            "causal_gain": 0.8680,
            "causal_null_gap": 0.0,
        },
    }
    obj.update(overrides)
    p = tmp_path / "bundle.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def _run(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_valid_candidate_bundle_passes(tmp_path):
    r = _run(_bundle(tmp_path))
    assert r.returncode == 0
    assert "intake-valid" in r.stdout
    assert "does not close GAP_1" in r.stdout


def test_example_bundle_rejected_as_evidence_by_default():
    r = _run(ROOT / "templates" / "EXTERNAL_VALIDATION_BUNDLE.example.json")
    assert r.returncode == 1
    assert "example bundle is not evidence" in r.stderr


def test_example_bundle_can_be_checked_only_as_template():
    r = _run(
        ROOT / "templates" / "EXTERNAL_VALIDATION_BUNDLE.example.json",
        "--allow-example",
    )
    assert r.returncode == 0


def test_author_self_run_rejected(tmp_path):
    r = _run(_bundle(tmp_path, reviewer_id="neuron7xLab"))
    assert r.returncode == 1
    assert "repository author" in r.stderr


def test_missing_environment_rejected(tmp_path):
    r = _run(_bundle(tmp_path, environment={"os": "Ubuntu"}))
    assert r.returncode == 1
    assert "environment.python" in r.stderr


def test_missing_commands_rejected(tmp_path):
    r = _run(_bundle(tmp_path, commands_run=[]))
    assert r.returncode == 1
    assert "commands_run" in r.stderr


def test_metric_drift_rejected(tmp_path):
    r = _run(
        _bundle(
            tmp_path,
            observed_metrics={
                "learned_post_mae": 99.0,
                "injected_post_mae": 8.0028,
                "oracle_post_mae": 0.7933,
                "causal_gain": 0.8680,
                "causal_null_gap": 0.0,
            },
        )
    )
    assert r.returncode == 1
    assert "learned_post_mae drift" in r.stderr


def test_bad_commit_rejected(tmp_path):
    r = _run(_bundle(tmp_path, repo_commit="not-a-sha"))
    assert r.returncode == 1
    assert "repo_commit" in r.stderr


def test_no_leakage_must_be_exact_true(tmp_path):
    r = _run(_bundle(tmp_path, no_leakage_attestation="true"))
    assert r.returncode == 1
    assert "no_leakage_attestation" in r.stderr
