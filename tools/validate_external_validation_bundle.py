#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate an external reproduction proof bundle without upgrading claims.

This reviewer helper is intentionally outside scripts/ because scripts/
is part of the signed provenance root. The authoritative claim-upgrade
guard remains src/ctios/external_validation.py; this tool only checks
whether a candidate bundle is well-formed enough for human review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "evidence" / "EXTERNAL_VALIDATION_BUNDLE.schema.json"
DEFAULT_TEMPLATE = ROOT / "templates" / "EXTERNAL_VALIDATION_BUNDLE.example.json"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
AUTHOR_MARKERS = {"neuron7xlab", "neuron7x", "yaroslav", "vasylenko"}
EXPECTED_METRICS = {
    "learned_post_mae": 0.8830,
    "injected_post_mae": 8.0028,
    "oracle_post_mae": 0.7933,
    "causal_gain": 0.8680,
    "causal_null_gap": 0.0,
}
DEFAULT_TOLERANCE = 1e-3


def _load_json(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing bundle: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError("bundle root must be a JSON object")
    return obj


def _schema_required() -> list[str]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = schema.get("required", [])
    if not isinstance(required, list) or not required:
        raise ValueError("schema has no required fields")
    return [str(x) for x in required]


def _is_author_marker(value: str) -> bool:
    v = value.lower()
    return any(marker in v for marker in AUTHOR_MARKERS)


def validate_bundle(
    path: Path,
    *,
    allow_example: bool = False,
    require_metrics: bool = True,
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[str]:
    """Return validation errors. Empty list means candidate intake PASS."""

    errors: list[str] = []
    obj = _load_json(path)

    if obj.get("bundle_kind") == "EXAMPLE_NOT_EVIDENCE" and not allow_example:
        errors.append("example bundle is not evidence")

    for key in _schema_required():
        if key not in obj:
            errors.append(f"missing required field: {key}")

    reviewer_id = str(obj.get("reviewer_id", ""))
    if len(reviewer_id) < 3:
        errors.append("reviewer_id too short")
    if _is_author_marker(reviewer_id):
        errors.append("reviewer_id appears to be the repository author")

    for key in (
        "reviewer_pubkey_sha256",
        "spec_sha256",
        "verdict_sha256",
        "command_transcript_sha256",
    ):
        if not HEX64.match(str(obj.get(key, ""))):
            errors.append(f"{key} must be a lowercase 64-hex sha256")

    if not COMMIT.match(str(obj.get("repo_commit", ""))):
        errors.append("repo_commit must be a 7-40 char lowercase hex commit prefix/full sha")

    if str(obj.get("timestamp_utc", "")).endswith("Z") is False:
        errors.append("timestamp_utc must be UTC and end with Z")

    if obj.get("no_leakage_attestation") is not True:
        errors.append("no_leakage_attestation must be exactly true")

    env = obj.get("environment")
    if not isinstance(env, dict):
        errors.append("environment object is required")
    else:
        for key in ("os", "python"):
            if not str(env.get(key, "")).strip():
                errors.append(f"environment.{key} is required")

    commands = obj.get("commands_run")
    if not isinstance(commands, list) or not commands:
        errors.append("commands_run must be a non-empty list")

    if require_metrics:
        metrics = obj.get("observed_metrics")
        if not isinstance(metrics, dict):
            errors.append("observed_metrics object is required")
        else:
            for key, expected in EXPECTED_METRICS.items():
                if key not in metrics:
                    errors.append(f"observed_metrics.{key} missing")
                    continue
                try:
                    observed = float(metrics[key])
                except (TypeError, ValueError):
                    errors.append(f"observed_metrics.{key} must be numeric")
                    continue
                if abs(observed - expected) > tolerance:
                    errors.append(
                        f"observed_metrics.{key} drift: observed={observed} "
                        f"expected={expected} tolerance={tolerance}"
                    )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundle",
        nargs="?",
        default=str(DEFAULT_TEMPLATE),
        help="Path to candidate EXTERNAL_VALIDATION_BUNDLE.json",
    )
    parser.add_argument(
        "--allow-example",
        action="store_true",
        help="Allow the committed example template to pass as a template check, not evidence.",
    )
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Validate only schema/intake metadata; still does not close GAP_1.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=DEFAULT_TOLERANCE,
        help="Absolute tolerance for frozen metric comparison.",
    )
    args = parser.parse_args(argv)

    try:
        errors = validate_bundle(
            Path(args.bundle),
            allow_example=args.allow_example,
            require_metrics=not args.no_metrics,
            tolerance=args.tolerance,
        )
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    if errors:
        print("FAIL: external validation bundle rejected", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("PASS: candidate external validation bundle is intake-valid")
    print("NOTE: this does not close GAP_1 and does not set READY/productizable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
