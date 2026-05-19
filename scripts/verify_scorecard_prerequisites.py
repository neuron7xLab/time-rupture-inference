# SPDX-License-Identifier: MIT
"""OpenSSF Scorecard honesty gate (PR O). Stdlib-only.

Scorecard cannot run inside the gate (it needs live GitHub-API
network access; the project contract forbids network in CI/tests).
This script does NOT run Scorecard. It enforces that the recorded
status in `evidence/SCORECARD_STATUS.json` is HONEST and never
overclaims:

  * status must be exactly NOT_RUN or RUN;
  * NOT_RUN  -> score MUST be null and a non-empty reason MUST exist;
  * RUN      -> a real tool_version AND a committed scorecard_json
                path that exists AND a numeric score in [0, 10];
  * a numeric score with status NOT_RUN is a fabrication -> fail.

Fails closed on a missing/unparseable file or any overclaim.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_STATUS = _ROOT / "evidence" / "SCORECARD_STATUS.json"


def audit() -> list[str]:
    problems: list[str] = []
    if not _STATUS.exists():
        return ["evidence/SCORECARD_STATUS.json missing"]
    try:
        d = json.loads(_STATUS.read_text())
    except json.JSONDecodeError as e:
        return [f"SCORECARD_STATUS.json unparseable: {e}"]

    status = d.get("status")
    if status not in ("NOT_RUN", "RUN"):
        problems.append(f"status must be NOT_RUN or RUN, got {status!r}")
        return problems

    score = d.get("score")
    if status == "NOT_RUN":
        if score is not None:
            problems.append(
                "status NOT_RUN but a score is present "
                f"({score!r}) — fabricated Scorecard number"
            )
        if not str(d.get("reason", "")).strip():
            problems.append("status NOT_RUN without a recorded reason")
    else:  # RUN
        if not str(d.get("tool_version", "")).strip():
            problems.append("status RUN without a real tool_version")
        sj = d.get("scorecard_json")
        if not sj or not (_ROOT / str(sj)).exists():
            problems.append(
                "status RUN without an existing committed "
                "scorecard_json artifact"
            )
        if not isinstance(score, (int, float)) or not (0 <= score <= 10):
            problems.append(
                "status RUN without a numeric score in [0, 10]"
            )
    return problems


def main() -> int:
    problems = audit()
    if problems:
        print("SCORECARD HONESTY — FAIL")
        for p in problems:
            print("  " + p)
        return 1
    d = json.loads(_STATUS.read_text())
    print(f"SCORECARD HONESTY — OK (status={d['status']}, "
          f"score={d.get('score')}, no overclaim)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
