# SPDX-License-Identifier: MIT
"""Generate an SPDX 2.3 SBOM from the pinned CI lock (NOT hand-written:
deterministically derived from requirements-ci.lock + pyproject). No
third-party SBOM tool is installed; this emits standard SPDX JSON from
real dependency state. `--verify-only` checks the committed SBOM still
matches the lock (drift = fail). Stdlib-only.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_LOCK = _ROOT / "requirements-ci.lock"
_PYPROJECT = _ROOT / "pyproject.toml"
_SBOM = _ROOT / "sbom.spdx.json"


def _commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=_ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.strip() or "UNKNOWN"


def _lock_pkgs() -> list[tuple[str, str]]:
    pkgs: list[tuple[str, str]] = []
    for ln in _LOCK.read_text().splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_.\-]+)==([A-Za-z0-9_.\-+]+)$", s)
        if m:
            pkgs.append((m.group(1), m.group(2)))
    return sorted(pkgs)


def _project_version() -> str:
    m = re.search(
        r'(?m)^version\s*=\s*"([^"]+)"', _PYPROJECT.read_text()
    )
    return m.group(1) if m else "0.0.0"


def build() -> dict[str, object]:
    pkgs = _lock_pkgs()
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    root_id = "SPDXRef-Package-time-rupture-inference"
    packages = [{
        "name": "time-rupture-inference",
        "SPDXID": root_id,
        "versionInfo": _project_version(),
        "downloadLocation": "NOASSERTION",
        "licenseConcluded": "NOASSERTION",
        "filesAnalyzed": False,
        "supplier": "Organization: neuron7xLab",
    }]
    rels = []
    for name, ver in pkgs:
        pid = f"SPDXRef-Package-{re.sub(r'[^A-Za-z0-9.-]', '-', name)}"
        packages.append({
            "name": name,
            "SPDXID": pid,
            "versionInfo": ver,
            "downloadLocation": "NOASSERTION",
            "licenseConcluded": "NOASSERTION",
            "filesAnalyzed": False,
        })
        rels.append({
            "spdxElementId": root_id,
            "relationshipType": "DEPENDS_ON",
            "relatedSpdxElement": pid,
        })
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "time-rupture-inference-SBOM",
        "documentNamespace": (
            f"https://github.com/neuron7xLab/time-rupture-inference/"
            f"sbom/{_commit()}"
        ),
        "creationInfo": {
            "created": ts,
            "creators": [
                "Tool: ctios-generate_sbom",
                "Organization: neuron7xLab",
            ],
        },
        "comment": (
            "Generated from requirements-ci.lock (pinned, LEVEL_1, "
            "no hashes). Source commit recorded in documentNamespace."
        ),
        "documentDescribes": [root_id],
        "packages": packages,
        "relationships": rels,
    }


def _pkg_set(doc: dict[str, object]) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for p in doc.get("packages", []):  # type: ignore[union-attr]
        if p["SPDXID"] != "SPDXRef-Package-time-rupture-inference":
            out.add((p["name"], p["versionInfo"]))
    return out


def verify() -> list[str]:
    problems: list[str] = []
    if not _SBOM.exists():
        return ["sbom.spdx.json missing — run generate_sbom.py"]
    try:
        doc = json.loads(_SBOM.read_text())
    except json.JSONDecodeError as e:
        return [f"sbom.spdx.json unparseable: {e}"]
    if doc.get("spdxVersion") != "SPDX-2.3":
        problems.append("spdxVersion != SPDX-2.3")
    if "creationInfo" not in doc or "created" not in doc["creationInfo"]:
        problems.append("creationInfo.created missing")
    lock = set(_lock_pkgs())
    sbom = _pkg_set(doc)
    extra = sbom - lock
    missing = lock - sbom
    if extra:
        problems.append(f"SBOM has packages absent from lock: {sorted(extra)}")
    if missing:
        problems.append(f"lock packages missing from SBOM: {sorted(missing)}")
    for req in ("numpy", "pyyaml", "pytest", "ruff", "mypy"):
        if not any(n.lower() == req for n, _ in sbom):
            problems.append(f"required dependency '{req}' absent from SBOM")
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--verify-only" in argv:
        problems = verify()
        if problems:
            print("SBOM — FAIL")
            for p in problems:
                print("  " + p)
            return 1
        print("SBOM — OK (SPDX-2.3, matches requirements-ci.lock)")
        return 0
    _SBOM.write_text(json.dumps(build(), indent=2, sort_keys=True))
    print(f"SBOM written: {_SBOM.relative_to(_ROOT)} "
          f"({len(_lock_pkgs())} pinned deps, SPDX-2.3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
