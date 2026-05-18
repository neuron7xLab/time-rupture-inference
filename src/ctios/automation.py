# SPDX-License-Identifier: MIT
"""Operational automation gateway: run the full enforcement chain once and
emit a single UTC-stamped, command-provenanced JSON ledger.

This does NOT replace CI or the gates — it is a local one-command
reproduction that mirrors the CI contract and writes an auditable run
summary. The summary is written under ``runs/`` (gitignored): it is a
mutable artifact, never a committed RED/GREEN claim.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class AutomationContract:
    name: str
    command: tuple[str, ...]
    success_codes: tuple[int, ...] = (0,)


@dataclass(frozen=True)
class ChannelResult:
    name: str
    started_utc: str
    ended_utc: str
    returncode: int
    ok: bool
    command: list[str]
    stdout_tail: list[str]
    stderr_tail: list[str]


# Mirrors the CI contract (.github/workflows/ci.yml), in CI order.
DEFAULT_CHANNELS: tuple[AutomationContract, ...] = (
    AutomationContract("ruff", ("ruff", "check", "src", "tests", "scripts")),
    AutomationContract("mypy_strict", ("mypy",)),
    AutomationContract("claims_lint", ("python", "scripts/claims_lint.py")),
    AutomationContract("provenance", ("python", "scripts/provenance_attest.py")),
    AutomationContract("tests", ("python", "-m", "pytest", "tests", "-q")),
    AutomationContract("release_gate", ("python", "-m", "ctios.runner", "--mode", "full")),
)


def _run_contract(contract: AutomationContract) -> ChannelResult:
    started = datetime.now(UTC)
    proc = subprocess.run(
        contract.command, capture_output=True, text=True, check=False
    )
    ended = datetime.now(UTC)
    return ChannelResult(
        name=contract.name,
        started_utc=started.isoformat(),
        ended_utc=ended.isoformat(),
        returncode=proc.returncode,
        ok=proc.returncode in contract.success_codes,
        command=list(contract.command),
        stdout_tail=proc.stdout.splitlines()[-20:],
        stderr_tail=proc.stderr.splitlines()[-20:],
    )


def run_automation(channels: Sequence[AutomationContract], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)
    results = [_run_contract(ch) for ch in channels]
    status = "green" if all(r.ok for r in results) else "red"
    payload: dict[str, object] = {
        "schema": "tri.automation.v1",
        "started_utc": started.isoformat(),
        "finished_utc": datetime.now(UTC).isoformat(),
        "status": status,
        "results": [asdict(r) for r in results],
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if status == "green" else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-command reproduction; emits a UTC-stamped run ledger."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("runs/automation_status.json"),
        help="Path to the UTC-stamped structured run summary (gitignored).",
    )
    args = parser.parse_args()
    return run_automation(DEFAULT_CHANNELS, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
