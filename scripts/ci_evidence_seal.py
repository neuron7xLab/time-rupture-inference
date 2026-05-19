# SPDX-License-Identifier: MIT
"""Seal CI status into a reverifiable artifact — not a sentence.

"CI is green" must not rest on a report. This fetches the actual
workflow runs for an exact commit via the `gh` CLI, applies the same
fail-closed decision as scripts/ci_gate_watch.py (every expected
workflow present, completed, success, on that sha), and writes
evidence/CI_RUN_ATTESTATION.json — commit, per-workflow run id +
conclusion + url, fetch timestamp, and the exact command to
re-fetch. Anyone can re-run that command and diff.

Operator tool: it reaches the network (`gh`), so it is NOT wired into
CI or pytest (the repo forbids network there). Its decision core is
reused from ci_gate_watch and unit-tested without network.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_gate_watch as w  # noqa: E402

_ROOT = Path(__file__).resolve().parents[1]
_OUT = _ROOT / "evidence" / "CI_RUN_ATTESTATION.json"


def _fetch(branch: str, limit: int) -> list[dict[str, str]] | None:
    try:
        p = subprocess.run(
            ["gh", "run", "list", "--branch", branch, "--limit",
             str(limit), "--json",
             "databaseId,name,status,conclusion,headSha,url"],
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
            "run_id": str(r.get("databaseId", "")),
            "url": str(r.get("url", "")),
        }
        for r in data
    ]


def seal(
    branch: str, sha: str, expected: set[str],
    rows: list[dict[str, str]],
) -> tuple[int, dict[str, object]]:
    state, detail = w.evaluate(rows, expected, sha)
    scoped = sorted(
        (r for r in rows if r["sha"] == sha),
        key=lambda r: r["name"],
    )
    doc: dict[str, object] = {
        "commit": sha,
        "branch": branch,
        "expected_workflows": sorted(expected),
        "state": state,
        "detail": detail,
        "fetched_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        ),
        "runs": [
            {
                "name": r["name"],
                "status": r["status"],
                "conclusion": r["conclusion"],
                "run_id": r["run_id"],
                "url": r["url"],
            }
            for r in scoped
        ],
        "reverify": (
            f"gh run list --branch {branch} --limit 20 --json "
            f"databaseId,name,conclusion,headSha --jq "
            f"'.[]|select(.headSha==\"{sha}\")'"
        ),
        "note": (
            "Witnessed snapshot at fetched_utc. SUCCESS requires every "
            "expected workflow completed+success on this exact commit; "
            "absence of a run is NOT success (fail-closed)."
        ),
    }
    return (0 if state == "SUCCESS" else 1), doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--expect", required=True)
    a = ap.parse_args()
    expected = {s.strip() for s in a.expect.split(",") if s.strip()}
    rows = _fetch(a.branch, max(20, len(expected) + 5))
    if rows is None:
        print(
            "CI EVIDENCE SEAL — ABORT (no trustworthy gh reply; "
            "refusing to seal from absence of data)"
        )
        return 2
    rc, doc = seal(a.branch, a.sha, expected, rows)
    _OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    tag = "OK" if rc == 0 else "FAIL"
    print(
        f"CI EVIDENCE SEAL — {tag} ({doc['state']}: {doc['detail']}) "
        f"-> {_OUT.relative_to(_ROOT)}"
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
