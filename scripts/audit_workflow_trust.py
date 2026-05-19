# SPDX-License-Identifier: MIT
"""Workflow trust audit (PR K). Stdlib-only by design: it must not
bootstrap trust through an uninstalled dependency. Fails closed if any
GitHub Action is not pinned to a 40-hex commit SHA with a version
comment, any workflow lacks explicit permissions, write-all appears,
a non-release workflow has unjustified write, or the SHA-resolution
record is absent/incomplete.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_WF = _ROOT / ".github" / "workflows"
_RES = _ROOT / "evidence" / "ACTION_SHA_RESOLUTION.json"
_CONTRACT = _ROOT / "docs" / "WORKFLOW_TRUST_CONTRACT.md"

# capture the ref token AND the rest of the line (so the `# vX`
# version comment is validated together with the SHA pin)
_USES = re.compile(r"^\s*-?\s*uses:\s*(\S+)(.*)$")
_SHA_PIN = re.compile(r"^[\w.-]+/[\w.-]+@[0-9a-f]{40}$")
_VER_COMMENT = re.compile(r"#\s*\S+")
_PERMS = re.compile(r"(?m)^permissions:")


def _workflows() -> list[Path]:
    return sorted([*_WF.glob("*.yml"), *_WF.glob("*.yaml")])


def check_workflow(
    name: str, text: str, recorded: set[str], contract: str = ""
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
        m = _USES.match(ln)
        if not m:
            continue
        ref, rest = m.group(1), m.group(2)
        if "@" not in ref:
            problems.append(f"{name}: uses without ref: {ref}")
            continue
        act = ref.split("@", 1)[0]
        if not _SHA_PIN.match(ref):
            problems.append(
                f"{name}: action not pinned to a 40-hex commit SHA: {ref}"
            )
        elif not _VER_COMMENT.search(rest):
            problems.append(
                f"{name}: SHA-pinned action lacks a version comment: {ref}"
            )
        if act not in recorded:
            problems.append(
                f"{name}: {act} not recorded in ACTION_SHA_RESOLUTION.json"
            )
    return problems


def audit() -> list[str]:
    if not _RES.exists():
        return ["evidence/ACTION_SHA_RESOLUTION.json missing"]
    recorded = {
        a["action"]
        for a in json.loads(_RES.read_text()).get("actions", [])
    }
    contract = _CONTRACT.read_text() if _CONTRACT.exists() else ""
    problems: list[str] = []
    for wf in _workflows():
        problems += check_workflow(
            wf.name, wf.read_text(), recorded, contract
        )
    return problems


def main() -> int:
    problems = audit()
    out = _ROOT / "evidence" / "WORKFLOW_TRUST_AUDIT.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "clean": not problems,
                "n_problems": len(problems),
                "problems": problems,
                "workflows": [w.name for w in _workflows()],
            },
            indent=2,
        )
    )
    if problems:
        print("WORKFLOW TRUST AUDIT — FAIL")
        for p in problems:
            print("  " + p)
        return 1
    print(
        f"WORKFLOW TRUST AUDIT — OK ({len(_workflows())} workflows, "
        "all SHA-pinned, explicit permissions)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
