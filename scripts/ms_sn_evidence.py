#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ALLOWED_VERDICTS = {"GREEN", "RED_EXPECTED", "RED_UNEXPECTED", "INVALID_RUN"}
EXPECTED_PROTOCOL = "MS-SN-v1.0.0"
EXPECTED_PR = 74
DEFAULT_CONFIG = Path("configs/ms_sn_v1_0_0.yaml")


def canonical_json(payload: dict[str, Any]) -> bytes:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return canonical.encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compute_config_sha256(config_path: Path = DEFAULT_CONFIG) -> str:
    return sha256_file(config_path)


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"manifest not found: {path}")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid json in manifest: {path}") from exc
    if not isinstance(obj, dict):
        raise ValueError("manifest root must be a JSON object")
    return obj


def assert_config_hash(config_path: Path, expected_hash_path: Path) -> None:
    expected = expected_hash_path.read_text(encoding="utf-8").strip()
    actual = sha256_file(config_path)
    if actual != expected:
        raise ValueError(f"config hash mismatch: expected {expected} but computed {actual}")
    print(actual)


def _validate_common(payload: dict[str, Any]) -> None:
    if payload.get("protocol") != EXPECTED_PROTOCOL:
        raise ValueError("invalid protocol")
    if payload.get("pr") != EXPECTED_PR:
        raise ValueError("invalid pr; expected 74")
    claim_boundary = payload.get("claim_boundary")
    if not isinstance(claim_boundary, str) or not claim_boundary.strip():
        raise ValueError("missing or empty claim_boundary")
    config_sha = payload.get("config_sha256")
    if not is_sha256(config_sha):
        raise ValueError("config_sha256 must be lowercase sha256 hex")
    if config_sha != compute_config_sha256():
        raise ValueError("config_sha256 mismatch against configs/ms_sn_v1_0_0.yaml")
    runs = payload.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("runs must be a non-empty list")


def validate_scaffold_manifest(path: Path) -> None:
    payload = load_json_object(path)
    _validate_common(payload)
    if payload.get("status") != "SCAFFOLD_ONLY":
        raise ValueError("scaffold manifest status must be SCAFFOLD_ONLY")
    for i, run in enumerate(payload["runs"]):
        if not isinstance(run, dict):
            raise ValueError(f"run #{i} must be an object")
        if "seed" not in run:
            raise ValueError(f"run #{i} missing seed")
        verdict = run.get("verdict")
        if verdict not in ALLOWED_VERDICTS:
            raise ValueError(f"run #{i} invalid verdict")
    print("scaffold manifest valid")


def validate_runtime_manifest(path: Path) -> None:
    payload = load_json_object(path)
    _validate_common(payload)
    if payload.get("status") != "RUNTIME_VALIDATED":
        raise ValueError("runtime manifest status must be RUNTIME_VALIDATED")
    if not isinstance(payload.get("head_sha"), str) or not payload["head_sha"].strip():
        raise ValueError("missing head_sha")
    for i, run in enumerate(payload["runs"]):
        if not isinstance(run, dict):
            raise ValueError(f"run #{i} must be an object")
        for key in ("seed", "verdict", "hashes", "tests"):
            if key not in run:
                raise ValueError(f"run #{i} missing {key}")
        if not run["hashes"]:
            raise ValueError(f"run #{i} hashes must be non-empty")
        if not run["tests"]:
            raise ValueError(f"run #{i} tests must be non-empty")
        if run["verdict"] == "INVALID_RUN":
            raise ValueError(f"run #{i} verdict INVALID_RUN is not allowed for runtime validation")
        if run["verdict"] not in ALLOWED_VERDICTS:
            raise ValueError(f"run #{i} invalid verdict")
        artifact = run.get("artifact_sha256") or run.get("runtime_artifact_sha256")
        if artifact is None:
            raise ValueError(f"run #{i} missing artifact_sha256 or runtime_artifact_sha256")
        if not is_sha256(artifact):
            raise ValueError(f"run #{i} runtime artifact must be lowercase sha256 hex")
    print("runtime manifest valid")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path)
    parser.add_argument("--emit-config-hash", action="store_true")
    parser.add_argument("--expected-config-hash", type=Path)
    parser.add_argument("--validate-scaffold", type=Path)
    parser.add_argument("--validate-runtime", type=Path)
    parser.add_argument("--validate", type=Path, help="alias for --validate-scaffold")
    args = parser.parse_args()
    if args.config and args.emit_config_hash:
        print(sha256_file(args.config))
        return
    if args.config and args.expected_config_hash:
        assert_config_hash(args.config, args.expected_config_hash)
        return
    if args.validate_scaffold:
        validate_scaffold_manifest(args.validate_scaffold)
        return
    if args.validate_runtime:
        validate_runtime_manifest(args.validate_runtime)
        return
    if args.validate:
        validate_scaffold_manifest(args.validate)
        return
    parser.error("no action selected")


if __name__ == "__main__":
    main()
