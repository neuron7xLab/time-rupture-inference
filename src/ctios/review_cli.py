# SPDX-License-Identifier: MIT
"""`python -m ctios.review_cli {approve|reject|seal} <run_dir>
--reviewer R --reason "..."`.

Thin CLI over ctios.human_gate. The next experiment never runs
automatically; a human must approve it here with a reason.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ctios.human_gate import (
    approve_next,
    audit_trail,
    next_experiment_runnable,
    reject_next,
    seal_verdict,
)

_ACTIONS = {"approve": approve_next, "reject": reject_next, "seal": seal_verdict}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ctios.review_cli")
    ap.add_argument("action", choices=sorted([*_ACTIONS, "status"]))
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--reviewer", default="")
    ap.add_argument("--reason", default="")
    args = ap.parse_args(argv)

    if args.action == "status":
        for r in audit_trail(args.run_dir):
            print(f"{r.ts_utc}  {r.action:7s}  {r.reviewer}: {r.reason}")
        print(f"next_experiment_runnable={next_experiment_runnable(args.run_dir)}")
        return 0

    rec = _ACTIONS[args.action](args.run_dir, args.reviewer, args.reason)
    print(f"{rec.action} recorded by {rec.reviewer} @ {rec.ts_utc}")
    print(f"next_experiment_runnable={next_experiment_runnable(args.run_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
