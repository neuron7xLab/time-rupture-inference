# SPDX-License-Identifier: MIT
"""ctios.code_quality_audit — the audit is code, not prose.

Every check here is executable and tested. If this module says "no
defects", a test can prove the checker actually fires on a planted
defect. A markdown audit is never the source of truth.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src" / "ctios"

# Allowlisted broad excepts: file -> reason. Empty by design.
_BROAD_EXCEPT_ALLOW: dict[str, str] = {}
# Shell collectors that intentionally use `set -uo` (run-all-gates).
_SET_UO_ALLOW = {"reviewer_attack.sh", "deep_mechanism_audit.sh"}


@dataclass(frozen=True)
class Finding:
    check: str
    path: str
    detail: str


def _py_files() -> list[Path]:
    return sorted(_SRC.glob("*.py"))


def _scan_ast() -> list[Finding]:
    out: list[Finding] = []
    for f in _py_files():
        rel = str(f.relative_to(_ROOT))
        tree = ast.parse(f.read_text(), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    out.append(Finding("bare_except", rel, f"line {node.lineno}"))
                elif (
                    isinstance(node.type, ast.Name)
                    and node.type.id == "Exception"
                    and rel not in _BROAD_EXCEPT_ALLOW
                ):
                    out.append(
                        Finding("broad_except", rel, f"line {node.lineno}")
                    )
                if (
                    len(node.body) == 1
                    and isinstance(node.body[0], ast.Pass)
                ):
                    out.append(
                        Finding("except_pass", rel, f"line {node.lineno}")
                    )
            if isinstance(node, ast.FunctionDef):
                for d in node.args.defaults + node.args.kw_defaults:
                    if isinstance(d, ast.List | ast.Dict | ast.Set):
                        out.append(
                            Finding(
                                "mutable_default", rel,
                                f"{node.name} line {node.lineno}",
                            )
                        )
        # module-level mutable global container (empty list/dict/set
        # bound at module scope = shared mutable state smell).
        for stmt in tree.body:
            if not isinstance(stmt, ast.Assign):
                continue
            v = stmt.value
            empty = (
                (isinstance(v, ast.List) and not v.elts)
                or (isinstance(v, ast.Dict) and not v.keys)
                or (isinstance(v, ast.Set) and not v.elts)
            )
            if not empty:
                continue
            for tgt in stmt.targets:
                if isinstance(tgt, ast.Name):
                    out.append(
                        Finding(
                            "module_mutable_global", rel,
                            f"{tgt.id} line {stmt.lineno}",
                        )
                    )
    return out


def _scan_text() -> list[Finding]:
    out: list[Finding] = []
    # legacy global-RNG entry points (NOT default_rng / Generator type)
    rng_legacy = re.compile(
        r"\bnp\.random\.(seed|rand|randn|randint|random_sample|"
        r"random\(|normal|uniform|choice|permutation|shuffle|"
        r"standard_normal)\b"
    )
    for f in _py_files():
        rel = str(f.relative_to(_ROOT))
        if f.name == "code_quality_audit.py":
            continue  # self-exempt: this file holds the pattern strings
        txt = f.read_text()
        for m in rng_legacy.finditer(txt):
            out.append(Finding("np_random_global", rel, m.group(0)))
        for m in re.finditer(r"\b(TODO|FIXME|HACK)\b(?!.*#\d)", txt):
            out.append(Finding("unreferenced_todo", rel, m.group(1)))
    return out


def _scan_shell() -> list[Finding]:
    out: list[Finding] = []
    for s in sorted((_ROOT / "scripts").glob("*.sh")):
        head = s.read_text()[:600]
        if re.search(r"^set -euo pipefail", head, re.M):
            continue
        if s.name in _SET_UO_ALLOW and re.search(
            r"^set -uo pipefail", head, re.M
        ):
            continue
        out.append(
            Finding("shell_no_set_euo", f"scripts/{s.name}", "missing set -euo")
        )
    return out


def _scan_tracked_evidence() -> list[Finding]:
    """Generated evidence accidentally tracked by git."""
    import subprocess

    out: list[Finding] = []
    tracked = subprocess.run(
        ["git", "ls-files", "evidence/"],
        cwd=_ROOT, capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    gen = re.compile(
        r"(FALSIFY_|NEGATIVE_FALSIFY_|ADVERSARIAL_PORTABILITY_|"
        r"_MAP\.json|REVIEWER_ATTACK_RESULT|DEEP_MECHANISM_AUDIT_RESULT|"
        r"CHANGE_DETECTION_ARC\.json)"
    )
    for p in tracked:
        if gen.search(p):
            out.append(Finding("tracked_generated_evidence", p, "should be gitignored"))
    return out


def run_audit() -> list[Finding]:
    return (
        _scan_ast()
        + _scan_text()
        + _scan_shell()
        + _scan_tracked_evidence()
    )


def as_payload(findings: list[Finding]) -> dict[str, Any]:
    return {
        "clean": not findings,
        "n_findings": len(findings),
        "findings": [
            {"check": f.check, "path": f.path, "detail": f.detail}
            for f in findings
        ],
        "checks": [
            "bare_except", "broad_except", "except_pass",
            "mutable_default", "module_mutable_global",
            "np_random_global", "unreferenced_todo",
            "shell_no_set_euo", "tracked_generated_evidence",
        ],
    }


def main() -> int:
    findings = run_audit()
    payload = as_payload(findings)
    (_ROOT / "evidence").mkdir(exist_ok=True)
    (_ROOT / "evidence" / "CODE_QUALITY_AUDIT_RESULT.json").write_text(
        json.dumps(payload, indent=2)
    )
    rep = (_ROOT / "docs" / "reports" / "CODE_QUALITY_AUDIT_REPORT.md")
    rep.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Code Quality Audit Report (executable)",
        "",
        f"clean: **{payload['clean']}**  findings: {payload['n_findings']}",
        "",
        "Generated by `python -m ctios.code_quality_audit`. The markdown "
        "is the OUTPUT of the check, never its source of truth.",
        "",
        "| check | path | detail |",
        "|---|---|---|",
    ]
    lines += [
        f"| {f.check} | {f.path} | {f.detail} |" for f in findings
    ] or ["| (none) | | |"]
    rep.write_text("\n".join(lines) + "\n")
    print(f"code-quality audit :: clean={payload['clean']} "
          f"findings={payload['n_findings']}")
    return 0 if payload["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
