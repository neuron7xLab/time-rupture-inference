# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_VERDICTS = {"GREEN", "RED_EXPECTED", "RED_UNEXPECTED", "INVALID_RUN"}


def canonical_json(payload: dict[str, Any]) -> bytes:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return canonical.encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def validate_evidence_schema(payload: dict[str, Any]) -> None:
    required = ["protocol", "pr", "seed", "hashes", "tests", "claim_boundary", "verdict"]
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError(f"missing required keys: {missing}")
    if payload["protocol"] != "MS-SN-v1.0.0":
        raise ValueError("invalid protocol")
    if payload["verdict"] not in ALLOWED_VERDICTS:
        raise ValueError(f"invalid verdict: {payload['verdict']}")


def write_evidence(payload: dict[str, Any], path: Path) -> str:
    validate_evidence_schema(payload)
    sealed = sha256_bytes(canonical_json(payload))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(payload))
    return sealed


def bootstrap_manifest(path: Path, seed: int = 1729) -> None:
    payload = {
        "protocol": "MS-SN-v1.0.0",
        "runs": [
            {
                "seed": seed,
                "verdict": "INVALID_RUN",
                "note": "bootstrap placeholder until runtime module is implemented",
            }
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def validate_manifest(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("protocol") != "MS-SN-v1.0.0":
        raise ValueError("invalid manifest protocol")
    for run in payload.get("runs", []):
        if run.get("verdict") not in ALLOWED_VERDICTS:
            raise ValueError(f"invalid run verdict: {run}")
    print("manifest schema valid")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path)
    parser.add_argument("--emit-config-hash", action="store_true")
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--bootstrap-manifest", type=Path)
    args = parser.parse_args()
    if args.config and args.emit_config_hash:
        print(sha256_file(args.config))
        return
    if args.bootstrap_manifest:
        bootstrap_manifest(args.bootstrap_manifest)
        return
    if args.validate:
        validate_manifest(args.validate)
        return
    parser.error("no action selected")


if __name__ == "__main__":
    main()
