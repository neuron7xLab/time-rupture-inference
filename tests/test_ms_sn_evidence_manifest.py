# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_ms_sn_evidence_module():
    module_path = Path("scripts/ms_sn_evidence.py")
    spec = importlib.util.spec_from_file_location("ms_sn_evidence", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load ms_sn_evidence module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validate_manifest_accepts_allowed_verdicts(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    manifest = {
        "protocol": "MS-SN-v1.0.0",
        "runs": [{"seed": 1729, "verdict": "GREEN"}, {"seed": 1730, "verdict": "INVALID_RUN"}],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    mod.validate_manifest(path)


def test_validate_manifest_rejects_missing_file(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    with pytest.raises(FileNotFoundError, match="manifest not found"):
        mod.validate_manifest(tmp_path / "missing.json")


def test_bootstrap_manifest_writes_canonical_placeholder(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    path = tmp_path / "manifest.json"
    mod.bootstrap_manifest(path, seed=1733)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["protocol"] == "MS-SN-v1.0.0"
    assert payload["runs"][0]["seed"] == 1733
    assert payload["runs"][0]["verdict"] == "INVALID_RUN"


def test_assert_config_hash_matches_and_mismatch(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    config_path = tmp_path / "cfg.yaml"
    config_path.write_text("a: 1\n", encoding="utf-8")
    digest_path = tmp_path / "cfg.sha256"
    digest_path.write_text(mod.sha256_file(config_path) + "\n", encoding="utf-8")
    mod.assert_config_hash(config_path, digest_path)

    digest_path.write_text("0" * 64 + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="config hash mismatch"):
        mod.assert_config_hash(config_path, digest_path)
