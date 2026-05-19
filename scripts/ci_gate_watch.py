# SPDX-License-Identifier: MIT
"""Fail-closed CI gate watcher. Stdlib + the `gh` CLI.

The failure this kills: concluding "all green" from the *absence* of
evidence. A flaky GitHub API reply (empty / non-JSON / network error)
is TRANSIENT, never terminal-success. Terminal-success requires
positive proof: every expected workflow present, every run
`completed`, every conclusion `success`, all on the target sha. Any
adverse conclusion fails immediately; a timeout fails; an unparseable
or empty reply is retried, never trusted. Exit 0 ONLY on proven
all-green; 1 on a failed/timed-out run; 2 on timeout-without-proof.

Same principle as the repo's evidence contract: evidence is an
artifact, not the lack of one.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time

_ADVERSE = {"failure", "cancelled", "timed_out", "startup_failure",
            "action_required", "stale"}
_DONE = "completed"


def _poll(branch: str, limit: int) -> list[dict[str, str]] | None:
    """One poll. None == TRANSIENT (no trustworthy answer)."""
    try:
        p = subprocess.run(
            ["gh", "run", "list", "--branch", branch, "--limit",
             str(limit), "--json", "name,status,conclusion,headSha"],
            capture_output=True, text=True, check=False, timeout=60,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if p.returncode != 0 or not p.stdout.strip():
        return None
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list) or not data:
        return None
    return [
        {
            "name": str(r.get("name", "")),
            "status": str(r.get("status", "")),
            "conclusion": str(r.get("conclusion", "")),
            "sha": str(r.get("headSha", "")),
        }
        for r in data
    ]


def evaluate(
    rows: list[dict[str, str]], expected: set[str], sha: str
) -> tuple[str, str]:
    """Pure decision. Returns (state, detail). state in
    {SUCCESS, FAIL, PENDING}. PENDING == not yet proven (keep
    waiting); never an OK."""
    scoped = [r for r in rows if not sha or r["sha"] == sha]
    if not scoped:
        return "PENDING", "no runs on target sha yet"
    by_name = {r["name"]: r for r in scoped}
    for r in scoped:
        if r["conclusion"] in _ADVERSE:
            return "FAIL", f"{r['name']}: {r['conclusion']}"
    missing = sorted(expected - set(by_name))
    if missing:
        return "PENDING", f"expected workflows absent: {missing}"
    for name in sorted(expected):
        r = by_name[name]
        if r["status"] != _DONE:
            return "PENDING", f"{name}: {r['status']}"
        if r["conclusion"] != "success":
            return "FAIL", f"{name}: conclusion={r['conclusion']!r}"
    return "SUCCESS", f"{len(expected)} workflows completed success"


def watch(
    branch: str, expected: set[str], sha: str,
    timeout_s: int, interval_s: int,
) -> int:
    deadline = time.monotonic() + timeout_s
    last = "no poll yet"
    while time.monotonic() < deadline:
        rows = _poll(branch, max(8, len(expected) + 3))
        if rows is None:
            last = "TRANSIENT (empty/error reply — NOT trusted)"
        else:
            state, detail = evaluate(rows, expected, sha)
            last = f"{state}: {detail}"
            if state == "SUCCESS":
                print(f"CI GATE — OK ({detail})")
                return 0
            if state == "FAIL":
                print(f"CI GATE — FAIL ({detail})")
                return 1
        print(f"  …waiting: {last}")
        time.sleep(interval_s)
    print(f"CI GATE — TIMEOUT (no all-green proof; last: {last})")
    return 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", required=True)
    ap.add_argument(
        "--expect", required=True,
        help="comma-separated workflow names that must all succeed",
    )
    ap.add_argument("--sha", default="")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--interval", type=int, default=30)
    a = ap.parse_args()
    expected = {s.strip() for s in a.expect.split(",") if s.strip()}
    if not expected:
        print("CI GATE — FAIL (no expected workflows given)")
        return 1
    return watch(a.branch, expected, a.sha, a.timeout, a.interval)


if __name__ == "__main__":
    raise SystemExit(main())
