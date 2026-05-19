# SPDX-License-Identifier: MIT
"""Supply-chain trust aggregate (PR O). Stdlib-only, offline.

Single consolidated verdict over the independent supply-chain trust
roots shipped across PRs K/K.1/L/N/O. Each component is invoked as a
separate process (independent root, no shared in-process state), its
exit code captured, and the whole thing **fails closed**: any
component FAIL -> aggregate FAIL (exit 1) and no PASS verdict is
written.

Honest level (no overclaim): the aggregate proves that the workflow
SHA-pins, the pinned dependency lock, the release attestation/SBOM
contract, the verifier manifest, and the Scorecard *honesty record*
are all internally consistent and fail-closed. It does NOT prove
hermeticity, hash-locking, SLSA L3, or a real OpenSSF Scorecard
score (Scorecard is recorded NOT_RUN — see evidence/SCORECARD_
STATUS.json — because it requires network the project forbids in CI).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_EVIDENCE = _ROOT / "evidence" / "SUPPLY_CHAIN_TRUST_AUDIT.json"

# (component id, argv) — order is reporting order, not a dependency.
_COMPONENTS: list[tuple[str, list[str]]] = [
    ("verifier_manifest_static",
     ["tools/check_verifier_manifest_static.py", "--repo", "."]),
    ("verifier_manifest_gate", ["tools/verifier_manifest.py"]),
    ("workflow_trust", ["scripts/audit_workflow_trust.py"]),
    ("dependency_trust", ["scripts/verify_ci_deps.py"]),
    ("release_trust", ["scripts/audit_release_trust.py"]),
    ("sbom_no_drift", ["scripts/generate_sbom.py", "--verify-only"]),
    ("scorecard_honesty",
     ["scripts/verify_scorecard_prerequisites.py"]),
]

HONEST_LEVEL = (
    "SUPPLY_CHAIN_CONSISTENT_FAIL_CLOSED — workflow SHA-pinned, deps "
    "LEVEL_1 pinned (not hash-locked, not hermetic), release SLSA "
    "Build L2 (not L3), SBOM matches lock, verifier manifest intact, "
    "Scorecard honestly NOT_RUN (not PASS)."
)


def _run(argv: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, *argv],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tail = (proc.stdout or proc.stderr).strip().splitlines()
    return proc.returncode, tail[-1] if tail else ""


def audit() -> dict[str, object]:
    results: list[dict[str, object]] = []
    for cid, argv in _COMPONENTS:
        rc, last = _run(argv)
        results.append({
            "component": cid,
            "status": "PASS" if rc == 0 else "FAIL",
            "exit": rc,
            "last_line": last,
        })
    all_pass = all(r["status"] == "PASS" for r in results)
    return {
        "generated_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        ),
        "all_pass": all_pass,
        "honest_level": HONEST_LEVEL,
        "components": results,
        "not_claimed": [
            "hermetic build",
            "hash-locked dependencies",
            "SLSA Build L3",
            "OpenSSF Scorecard score (recorded NOT_RUN)",
        ],
    }


def main() -> int:
    report = audit()
    _EVIDENCE.parent.mkdir(exist_ok=True)
    _EVIDENCE.write_text(json.dumps(report, indent=2, sort_keys=True))
    components = report["components"]
    assert isinstance(components, list)
    if not report["all_pass"]:
        print("SUPPLY-CHAIN TRUST — FAIL (fail-closed aggregate)")
        for r in components:
            if r["status"] == "FAIL":
                print(f"  {r['component']}: exit {r['exit']} "
                      f":: {r['last_line']}")
        return 1
    print(f"SUPPLY-CHAIN TRUST — OK ({len(components)} independent "
          f"roots consistent; {HONEST_LEVEL})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
