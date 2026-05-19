# SPDX-License-Identifier: MIT
"""Workflow trust audit (PR K + K.1). Stdlib-only by design: it must
not bootstrap trust through an uninstalled dependency.

K.1 closes the residual gap: it is not enough that an action *name* is
recorded. Every workflow `uses:` ref must be BOUND to the evidence —
exact action, exact lowercase-40-hex SHA equal to the recorded
resolved_sha, and an exact `# <tag>` comment equal to the recorded
tag. The resolution evidence is itself schema-validated. Fails closed
on any mismatch, malformed record, missing/excess permissions,
write-all, or unjustified non-release write.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_WF = _ROOT / ".github" / "workflows"
_RES = _ROOT / "evidence" / "ACTION_SHA_RESOLUTION.json"
_CONTRACT = _ROOT / "docs" / "WORKFLOW_TRUST_CONTRACT.md"

_USES = re.compile(r"^\s*-?\s*uses:\s*(\S+)(.*)$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_PERMS = re.compile(r"(?m)^permissions:")


def _workflows() -> list[Path]:
    return sorted([*_WF.glob("*.yml"), *_WF.glob("*.yaml")])


def load_resolution(
    data: dict[str, Any] | None = None,
) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Parse + STRICTLY validate ACTION_SHA_RESOLUTION.json into
    {action: {tag, resolved_sha, source_ref, resolved_at_utc}}.
    Returns (record_map, schema_problems)."""
    problems: list[str] = []
    if data is None:
        if not _RES.exists():
            return {}, ["evidence/ACTION_SHA_RESOLUTION.json missing"]
        try:
            data = json.loads(_RES.read_text())
        except json.JSONDecodeError as e:
            return {}, [f"ACTION_SHA_RESOLUTION.json unparseable: {e}"]
    if not isinstance(data, dict) or "actions" not in data:
        return {}, ["ACTION_SHA_RESOLUTION.json: 'actions' missing"]
    top_ts = str(data.get("resolved_at_utc", "")).strip()
    record: dict[str, dict[str, str]] = {}
    for i, a in enumerate(data.get("actions", [])):
        if not isinstance(a, dict):
            problems.append(f"actions[{i}]: not an object")
            continue
        act = str(a.get("action", "")).strip()
        tag = str(a.get("tag", "")).strip()
        sha = str(a.get("resolved_sha", "")).strip()
        src = str(a.get("source_ref", "")).strip()
        ts = str(a.get("resolved_at_utc", "")).strip() or top_ts
        if not act:
            problems.append(f"actions[{i}]: action missing")
            continue
        if act in record:
            problems.append(f"{act}: duplicate action record")
        if not tag:
            problems.append(f"{act}: tag missing")
        if not _HEX40.match(sha):
            problems.append(
                f"{act}: resolved_sha not lowercase 40-hex: {sha!r}"
            )
        if not src:
            problems.append(f"{act}: source_ref missing")
        elif tag and not (src == f"refs/tags/{tag}" or src.endswith(f"/{tag}")):
            problems.append(
                f"{act}: source_ref {src!r} does not match tag {tag!r}"
            )
        if not ts:
            problems.append(f"{act}: resolved_at_utc missing (global+local)")
        record[act] = {
            "tag": tag, "resolved_sha": sha,
            "source_ref": src, "resolved_at_utc": ts,
        }
    if not record and not problems:
        problems.append("ACTION_SHA_RESOLUTION.json: no actions recorded")
    return record, problems


def check_workflow(
    name: str,
    text: str,
    record: dict[str, dict[str, str]],
    contract: str = "",
) -> list[str]:
    """Pure per-workflow audit (filesystem-free, unit-testable)."""
    problems: list[str] = []
    if not _PERMS.search(text):
        problems.append(f"{name}: no explicit top-level permissions")
    if re.search(r"(?m)permissions:\s*write-all", text):
        problems.append(f"{name}: permissions: write-all forbidden")
    is_release = "release" in name
    for m in re.finditer(r"(?m)^\s+(\w[\w-]*):\s*write\b", text):
        scope = m.group(1)
        if not is_release and f"{name}:{scope}:write" not in contract:
            problems.append(
                f"{name}: unjustified write permission '{scope}' "
                f"(justify as '{name}:{scope}:write' in "
                "docs/WORKFLOW_TRUST_CONTRACT.md)"
            )
    for ln in text.splitlines():
        mm = _USES.match(ln)
        if not mm:
            continue
        ref, rest = mm.group(1), mm.group(2).strip()
        if "@" not in ref:
            problems.append(f"{name}: uses without ref: {ref}")
            continue
        act, _, sha = ref.partition("@")
        if not _HEX40.match(sha):
            problems.append(
                f"{name}: {act} not pinned to a lowercase 40-hex SHA: "
                f"{sha!r}"
            )
            continue
        rec = record.get(act)
        if rec is None:
            problems.append(
                f"{name}: {act} not recorded in ACTION_SHA_RESOLUTION.json"
            )
            continue
        if sha != rec["resolved_sha"]:
            problems.append(
                f"{name}: {act} SHA {sha} != recorded resolved_sha "
                f"{rec['resolved_sha']}"
            )
        want = f"# {rec['tag']}"
        if rest != want:
            problems.append(
                f"{name}: {act} comment {rest!r} != exact {want!r}"
            )
    return problems


def audit() -> list[str]:
    record, schema_problems = load_resolution()
    if schema_problems:
        return schema_problems
    contract = _CONTRACT.read_text() if _CONTRACT.exists() else ""
    problems: list[str] = []
    for wf in _workflows():
        problems += check_workflow(wf.name, wf.read_text(), record, contract)
    return problems


def _evidence(problems: list[str], record: dict[str, dict[str, str]]
              ) -> dict[str, Any]:
    import subprocess

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=_ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    wfs = _workflows()
    use_n = sum(
        1 for w in wfs for ln in w.read_text().splitlines()
        if _USES.match(ln)
    )
    sha_mm = [p for p in problems if "!= recorded resolved_sha" in p]
    cmt_mm = [p for p in problems if "!= exact" in p]
    perm = [p for p in problems if "permission" in p or "write-all" in p]
    return {
        "status": "PASS" if not problems else "FAIL",
        "commit": head,
        "workflow_count": len(wfs),
        "action_use_count": use_n,
        "recorded_action_count": len(record),
        "sha_binding": {
            "status": "PASS" if not sha_mm else "FAIL",
            "mismatches": sha_mm,
        },
        "version_comment_binding": {
            "status": "PASS" if not cmt_mm else "FAIL",
            "mismatches": cmt_mm,
        },
        "permissions": {
            "status": "PASS" if not perm else "FAIL",
            "problems": perm,
        },
        "problems": problems,
    }


def main() -> int:
    record, schema_problems = load_resolution()
    problems = schema_problems or audit()
    out = _ROOT / "evidence" / "WORKFLOW_TRUST_AUDIT.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(_evidence(problems, record), indent=2))
    if problems:
        print("WORKFLOW TRUST AUDIT — FAIL")
        for p in problems:
            print("  " + p)
        return 1
    print(
        f"WORKFLOW TRUST AUDIT — OK ({len(_workflows())} workflows; "
        f"{len(record)} actions SHA+tag bound to evidence)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
