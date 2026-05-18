# SPDX-License-Identifier: MIT
"""Provenance & SPDX attestation (audit P1 #3 — internal layer).

Scope discipline (admissibility != science): this closes the INTERNAL
integrity layer only — every source file carries an SPDX license id and
a sha256 in a signed manifest, drift fails loud. It does NOT and must
NOT be read as a no-plagiarism claim: external arXiv/GitHub similarity
comparison is OPEN and cannot be performed in this offline environment.
That status is recorded honestly in the manifest, not silently closed.

Usage:
  python scripts/provenance_attest.py --write    # regenerate manifest
  python scripts/provenance_attest.py            # verify (exit 1 on drift)
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "provenance_manifest.json"

EXTERNAL_SCAN_STATUS = (
    "OPEN — external arXiv/GitHub similarity scan NOT performed (offline "
    "environment). This manifest attests internal integrity + license "
    "only; it is explicitly NOT a no-plagiarism claim."
)

PY_GLOBS = ("src/ctios/*.py", "scripts/*.py", "scripts_prereg.py")
OTHER = (
    "configs/*.yaml",
    "prereg/*.yaml",
    "claims.yaml",
    "invariants.yaml",
    "requirements-lock.txt",
    "pyproject.toml",
    "LICENSE",
    "README.md",
)


# Engine-generated, gitignored, ephemeral artifacts. They are NOT
# committed, so they must never enter the signed manifest — otherwise a
# clean CI checkout fails with "references missing file".
EPHEMERAL = ("NEXT_*.yaml", "FALSIFY_*.json", "NEGATIVE_FALSIFY_*.md")


def _ephemeral(p: Path) -> bool:
    return any(fnmatch(p.name, pat) for pat in EPHEMERAL)


def _files() -> list[Path]:
    out: list[Path] = []
    for g in (*PY_GLOBS, *OTHER):
        out += list(ROOT.glob(g))
    return sorted(
        {p for p in out if p.is_file() and not _ephemeral(p)}
    )


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build() -> dict:
    entries = []
    for p in _files():
        rel = str(p.relative_to(ROOT))
        spdx = "SPDX-License-Identifier: MIT" in p.read_text(errors="ignore")
        entries.append(
            {
                "path": rel,
                "sha256": _sha(p),
                "license": "MIT",
                "spdx_header": spdx if p.suffix == ".py" else "n/a",
            }
        )
    return {
        "license": "MIT",
        "copyright": "2026 neuron7xLab",
        "external_similarity_scan": EXTERNAL_SCAN_STATUS,
        "files": entries,
    }


def verify() -> list[str]:
    if not MANIFEST.exists():
        return ["provenance_manifest.json missing — run --write"]
    rec = json.loads(MANIFEST.read_text())
    cur = build()
    problems: list[str] = []
    if rec.get("external_similarity_scan") != EXTERNAL_SCAN_STATUS:
        problems.append("external-scan status drifted (must stay honestly OPEN)")
    a = {e["path"]: e for e in rec["files"]}
    b = {e["path"]: e for e in cur["files"]}
    for path in sorted(set(a) | set(b)):
        if path not in a:
            problems.append(f"unattested file: {path}")
        elif path not in b:
            problems.append(f"manifest references missing file: {path}")
        elif a[path]["sha256"] != b[path]["sha256"]:
            problems.append(f"sha256 drift: {path}")
        if path.endswith(".py") and b.get(path, {}).get("spdx_header") is False:
            problems.append(f"missing SPDX header: {path}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if args.write:
        MANIFEST.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
        print(f"provenance_manifest.json written ({len(build()['files'])} files)")
        return 0
    problems = verify()
    if problems:
        print("PROVENANCE — FAIL\n" + "\n".join(problems))
        return 1
    print(f"PROVENANCE — PASS ({len(build()['files'])} files; external scan OPEN)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
