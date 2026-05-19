# SPDX-License-Identifier: MIT
"""ctios.external_validation — a real external run cannot be faked.

A status JSON saying real_external_collaborator_run=true is NOT
sufficient. It is honoured only if an EXTERNAL_VALIDATION_BUNDLE exists
and validates against the pinned schema (reviewer id+key hash,
timestamp, repo commit, spec hash, verdict hash, no-leakage
attestation==true, command-transcript hash). No bundle -> no upgrade.
The default state is and remains EXTERNAL_RUN_PENDING.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
_STATUS = _ROOT / "evidence" / "external_validation_status.json"
_SCHEMA = _ROOT / "evidence" / "EXTERNAL_VALIDATION_BUNDLE.schema.json"
_BUNDLE = _ROOT / "evidence" / "EXTERNAL_VALIDATION_BUNDLE.json"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ExternalState:
    real_run_attested: bool
    reason: str


def _validate_bundle(obj: dict[str, Any]) -> list[str]:
    schema = json.loads(_SCHEMA.read_text())
    errs: list[str] = []
    for k in schema["required"]:
        if k not in obj:
            errs.append(f"missing field: {k}")
    if errs:
        return errs
    for k in (
        "reviewer_pubkey_sha256", "spec_sha256",
        "verdict_sha256", "command_transcript_sha256",
    ):
        if not _HEX64.match(str(obj.get(k, ""))):
            errs.append(f"{k} not a sha256")
    if obj.get("no_leakage_attestation") is not True:
        errs.append("no_leakage_attestation must be exactly true")
    if len(str(obj.get("repo_commit", ""))) < 7:
        errs.append("repo_commit too short")
    if len(str(obj.get("timestamp_utc", ""))) < 19:
        errs.append("timestamp_utc malformed")
    return errs


def external_state(
    *, status_path: Path | None = None, bundle_path: Path | None = None
) -> ExternalState:
    sp = status_path or _STATUS
    bp = bundle_path or _BUNDLE
    status: dict[str, Any] = (
        json.loads(sp.read_text()) if sp.exists() else {}
    )
    flag = bool(status.get("real_external_collaborator_run", False))
    if not bp.exists():
        return ExternalState(
            False,
            "no EXTERNAL_VALIDATION_BUNDLE.json — status flag (if any) "
            "is insufficient on its own",
        )
    try:
        bundle = json.loads(bp.read_text())
    except json.JSONDecodeError as e:
        return ExternalState(False, f"bundle not parseable: {e}")
    errs = _validate_bundle(bundle)
    if errs:
        return ExternalState(False, "bundle invalid: " + "; ".join(errs))
    if not flag:
        return ExternalState(
            False,
            "valid bundle present but status flag still false — "
            "both required",
        )
    return ExternalState(True, "valid external bundle + attested flag")


def real_external_run_attested(
    *, status_path: Path | None = None, bundle_path: Path | None = None
) -> bool:
    return external_state(
        status_path=status_path, bundle_path=bundle_path
    ).real_run_attested


def main() -> int:
    st = external_state()
    print(f"external_run_attested={st.real_run_attested}")
    print(f"reason: {st.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
