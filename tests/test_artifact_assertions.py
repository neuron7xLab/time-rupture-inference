# SPDX-License-Identifier: MIT
"""WP3 — a gate's exit code is not evidence. These prove the artifact
guards actually reject missing/empty/malformed/stale artifacts."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.artifact_assertions import (  # noqa: E402
    ArtifactError,
    assert_artifact,
    assert_non_empty,
    load_json,
)


def test_missing_artifact_rejected(tmp_path):
    with pytest.raises(ArtifactError, match="missing"):
        assert_artifact(tmp_path / "nope.json")


def test_empty_artifact_rejected(tmp_path):
    p = tmp_path / "e.json"
    p.write_text("  \n")
    with pytest.raises(ArtifactError, match="empty"):
        assert_non_empty(p)


def test_malformed_json_rejected(tmp_path):
    p = tmp_path / "m.json"
    p.write_text("{not json")
    with pytest.raises(ArtifactError, match="unparseable"):
        load_json(p)


def test_missing_schema_key_rejected(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"a": 1}))
    with pytest.raises(ArtifactError, match="missing keys"):
        assert_artifact(p, required=["a", "b"])


def test_stale_commit_artifact_rejected(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"commit": "0" * 40, "ok": True}))
    with pytest.raises(ArtifactError, match="stale"):
        assert_artifact(p, required=["ok"], commit_key="commit")


def test_valid_artifact_accepted(tmp_path):
    p = tmp_path / "ok.json"
    p.write_text(json.dumps({"x": 1, "y": 2}))
    assert assert_artifact(p, required=["x", "y"]) == {"x": 1, "y": 2}


def test_repo_machine_artifacts_validate():
    # the committed status artifact must pass its own schema
    assert_artifact(
        ROOT / "evidence" / "external_validation_status.json",
        required=["status", "real_external_collaborator_run"],
    )
