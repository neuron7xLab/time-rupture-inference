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


def _base_manifest(mod, status: str = "SCAFFOLD_ONLY", verdict: str = "INVALID_RUN"):
    return {
        "protocol": "MS-SN-v1.0.0",
        "pr": 74,
        "status": status,
        "claim_boundary": "research-only boundary",
        "config_sha256": mod.compute_config_sha256(),
        "runs": [{"seed": 1729, "verdict": verdict}],
    }


def test_scaffold_manifest_accepts_invalid_run(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    path = tmp_path / "m.json"
    path.write_text(json.dumps(_base_manifest(mod)), encoding="utf-8")
    mod.validate_scaffold_manifest(path)


def test_scaffold_manifest_rejects_wrong_pr(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod)
    m["pr"] = 72
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid pr"):
        mod.validate_scaffold_manifest(path)


def test_scaffold_manifest_rejects_missing_claim_boundary(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod)
    del m["claim_boundary"]
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="claim_boundary"):
        mod.validate_scaffold_manifest(path)


def test_scaffold_manifest_rejects_config_hash_mismatch(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod)
    m["config_sha256"] = "0" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="config_sha256 mismatch"):
        mod.validate_scaffold_manifest(path)


def test_runtime_manifest_rejects_invalid_run(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="INVALID_RUN")
    m["head_sha"] = "abc123"
    m["runs"][0]["hashes"] = {"manifest": "x"}
    m["runs"][0]["tests"] = {"suite": "ok"}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="INVALID_RUN"):
        mod.validate_runtime_manifest(path)


def test_runtime_manifest_rejects_missing_pr(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="GREEN")
    m["head_sha"] = "abc123"
    m["runs"][0]["hashes"] = {"manifest": "x"}
    m["runs"][0]["tests"] = {"suite": "ok"}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    del m["pr"]
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid pr"):
        mod.validate_runtime_manifest(path)


def test_runtime_manifest_rejects_wrong_pr(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="GREEN")
    m["pr"] = 73
    m["head_sha"] = "abc123"
    m["runs"][0]["hashes"] = {"manifest": "x"}
    m["runs"][0]["tests"] = {"suite": "ok"}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid pr"):
        mod.validate_runtime_manifest(path)


def test_runtime_manifest_rejects_missing_hashes(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="GREEN")
    m["head_sha"] = "abc123"
    m["runs"][0]["tests"] = {"suite": "ok"}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="missing hashes"):
        mod.validate_runtime_manifest(path)


def test_runtime_manifest_rejects_missing_tests(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="GREEN")
    m["head_sha"] = "abc123"
    m["runs"][0]["hashes"] = {"manifest": "x"}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="missing tests"):
        mod.validate_runtime_manifest(path)


def test_runtime_manifest_accepts_minimal_valid_runtime_manifest(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="GREEN")
    m["head_sha"] = "abc123"
    m["runs"][0]["hashes"] = {"manifest": "x"}
    m["runs"][0]["tests"] = {"suite": "ok"}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    mod.validate_runtime_manifest(path)


def test_runtime_manifest_rejects_empty_hashes(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="GREEN")
    m["head_sha"] = "abc123"
    m["runs"][0]["hashes"] = {}
    m["runs"][0]["tests"] = {"suite": "ok"}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="hashes must be non-empty"):
        mod.validate_runtime_manifest(path)


def test_runtime_manifest_rejects_empty_tests(tmp_path: Path) -> None:
    mod = _load_ms_sn_evidence_module()
    m = _base_manifest(mod, status="RUNTIME_VALIDATED", verdict="GREEN")
    m["head_sha"] = "abc123"
    m["runs"][0]["hashes"] = {"manifest": "x"}
    m["runs"][0]["tests"] = {}
    m["runs"][0]["artifact_sha256"] = "a" * 64
    path = tmp_path / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="tests must be non-empty"):
        mod.validate_runtime_manifest(path)
