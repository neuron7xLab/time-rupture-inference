# SPDX-License-Identifier: MIT
"""ctios.readiness_score — readiness without self-deception.

Three things are kept strictly separate: the technical sub-score, the
release decision, and the blocking facts. The number never overrides a
blocking fact. External portability cannot score full marks, and the
status cannot exceed CONDITIONALLY_READY, until a *real* external
collaborator run is recorded (a simulated/mock pack does not count).

A high number is not a reward. The blocking fact is the headline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
_STATUS = _ROOT / "evidence" / "external_validation_status.json"

# Engineering sub-scores (max). External portability is intentionally
# capped without a real external run — see _score().
_MAX = {
    "falsification": 20,
    "reproducibility": 15,
    "claim_discipline": 15,
    "reviewer_usability": 15,
    "adversarial_robustness": 15,
    "evidence_quality": 10,
    "external_portability": 10,
}
_PORTABILITY_CAP_NO_EXTERNAL = 5


@dataclass
class Readiness:
    blocking_facts: list[str]
    status: str
    technical_score: int
    score_cap_reason: str
    subscores: dict[str, int] = field(default_factory=dict)
    note: str = (
        "The number is not an achievement. Status is decided by blocking "
        "facts, not by the score."
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "blocking_facts": self.blocking_facts,
            "status": self.status,
            "technical_score": self.technical_score,
            "score_cap_reason": self.score_cap_reason,
            "subscores": self.subscores,
            "note": self.note,
        }


def _load_status(path: Path | None = None) -> dict[str, Any]:
    p = path or _STATUS
    if not p.exists():
        return {"real_external_collaborator_run": False}
    data: dict[str, Any] = json.loads(p.read_text())
    return data


def compute_readiness(
    *,
    gates_all_pass: bool,
    external_use_cases: int = 0,
    productizable_requested: bool = False,
    status_path: Path | None = None,
    bundle_path: Path | None = None,
) -> Readiness:
    from ctios.external_validation import real_external_run_attested

    # A real run is attested ONLY by a valid proof bundle, never by the
    # status flag alone (anti-tamper).
    _load_status(status_path)
    real_run = real_external_run_attested(
        status_path=status_path, bundle_path=bundle_path
    )

    blocking: list[str] = []
    if not real_run:
        blocking.append(
            "real_external_collaborator_run = false (simulated/mock pack "
            "does not count)"
        )
    if not gates_all_pass:
        blocking.append("one or more engineering gates fail")
    if productizable_requested and external_use_cases < 2:
        blocking.append(
            "productizable requested without >=2 external use cases"
        )

    sub = dict.fromkeys(_MAX, 0)
    if gates_all_pass:
        for k, v in _MAX.items():
            sub[k] = v
    cap_reason = "none"
    if not real_run and sub["external_portability"] > _PORTABILITY_CAP_NO_EXTERNAL:
        sub["external_portability"] = _PORTABILITY_CAP_NO_EXTERNAL
        cap_reason = (
            "external_portability capped at 5/10 — no real external run"
        )
    total = sum(sub.values())

    # Release decision: blocking facts dominate the number, always.
    if blocking:
        status = "CONDITIONALLY_READY" if gates_all_pass else "NOT_READY"
    elif real_run and gates_all_pass:
        status = (
            "PRODUCTIZABLE"
            if (productizable_requested and external_use_cases >= 2)
            else "READY"
        )
    else:
        status = "NOT_READY"

    # Hard ceiling: never READY/PRODUCTIZABLE while a blocking fact holds.
    if blocking and status in ("READY", "PRODUCTIZABLE"):
        status = "CONDITIONALLY_READY"

    return Readiness(blocking, status, total, cap_reason, sub)


def main() -> int:
    r = compute_readiness(gates_all_pass=True)
    print("FRONTIER READINESS — blocking facts first")
    for b in r.blocking_facts or ["(none)"]:
        print(f"  BLOCKING: {b}")
    print(f"STATUS: {r.status}")
    print(f"technical_score: {r.technical_score}/100  ({r.score_cap_reason})")
    print(f"note: {r.note}")
    return 0 if r.status in ("CONDITIONALLY_READY", "READY", "PRODUCTIZABLE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
