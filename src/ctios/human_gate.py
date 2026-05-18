# SPDX-License-Identifier: MIT
"""ctios.human_gate — mandatory human-in-the-loop boundary.

A proposed next experiment never runs autonomously. Approval,
rejection, and sealing are append-only audit records. The next
experiment is runnable only after an explicit ``approve`` with a
non-empty reviewer and reason; ``seal`` finalizes the verdict.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

AUDIT_FILE = "human_gate_audit.jsonl"


class GateError(RuntimeError):
    pass


@dataclass(frozen=True)
class GateRecord:
    action: str  # approve | reject | seal
    reviewer: str
    reason: str
    ts_utc: str

    def as_json(self) -> str:
        return json.dumps(
            {
                "action": self.action,
                "reviewer": self.reviewer,
                "reason": self.reason,
                "ts_utc": self.ts_utc,
            }
        )


def _append(run_dir: Path, rec: GateRecord) -> GateRecord:
    if not rec.reviewer.strip():
        raise GateError("reviewer must be non-empty")
    if not rec.reason.strip():
        raise GateError("reason must be non-empty")
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / AUDIT_FILE).open("a", encoding="utf-8") as fh:
        fh.write(rec.as_json() + "\n")
    return rec


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def approve_next(run_dir: Path, reviewer: str, reason: str) -> GateRecord:
    return _append(run_dir, GateRecord("approve", reviewer, reason, _now()))


def reject_next(run_dir: Path, reviewer: str, reason: str) -> GateRecord:
    return _append(run_dir, GateRecord("reject", reviewer, reason, _now()))


def seal_verdict(run_dir: Path, reviewer: str, reason: str) -> GateRecord:
    return _append(run_dir, GateRecord("seal", reviewer, reason, _now()))


def audit_trail(run_dir: Path) -> list[GateRecord]:
    p = run_dir / AUDIT_FILE
    if not p.exists():
        return []
    out: list[GateRecord] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        out.append(
            GateRecord(d["action"], d["reviewer"], d["reason"], d["ts_utc"])
        )
    return out


def next_experiment_runnable(run_dir: Path) -> bool:
    """True only if the latest decision is an approval (never auto-true)."""
    trail = [r for r in audit_trail(run_dir) if r.action in ("approve", "reject")]
    return bool(trail) and trail[-1].action == "approve"
