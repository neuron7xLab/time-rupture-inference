# SPDX-License-Identifier: MIT
"""Internal adversarial multi-role red-team — the maximal HONEST use
of self-computation. Recursion / role-decomposition raises INTERNAL
rigor; it can never close epistemic independence. This artifact
self-declares ``independent_validation: false`` as a hard invariant —
it cannot upgrade itself, and GAP_1 stays OPEN by construction.

Each role is a concrete executable probe that re-uses the repo's own
fail-closed instruments (dogfood — no new unproven judging logic):

  ATTACKER   — the lexicon / scope gates demonstrably reject planted
               violations (the negative tests must hold).
  SKEPTIC    — every gate is discriminative: the mutation-rejection
               tests (artifact freshness, doc-trust, CI watcher, CI
               seal) must hold.
  ILYA       — no self-evaluation-as-evidence leak: live claims-lint
               clean AND the SPEC/SYSTEM_CARD non-claim blocks present.
  DARIO      — claim-boundary intact: both structural gaps still OPEN,
               no READY/PRODUCTIZABLE leak (structural-gaps test).
  REPRODUCER — runs what is locally runnable; anything absent is
               recorded UNVERIFIED, never PASS; ALWAYS non-independent.

Any role breach -> exit 1, sealed FAIL. Holds claim vocabulary as
data -> claims.yaml-exempt, same rationale as claims_lint.py.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_OUT = _ROOT / "evidence" / "INTERNAL_ADVERSARIAL_REDTEAM.json"


def _pytest(paths: list[str]) -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *paths, "-q",
         "-o", "addopts="],
        cwd=_ROOT, capture_output=True, text=True, check=False,
        env={"PYTHONPATH": "src", "PATH": _path()},
    )
    tail = (r.stdout or r.stderr).strip().splitlines()
    return r.returncode == 0, (tail[-1] if tail else "")


def _path() -> str:
    import os
    return os.environ.get("PATH", "")


def _run(argv: list[str]) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, *argv], cwd=_ROOT,
        capture_output=True, text=True, check=False,
        env={"PYTHONPATH": "src", "PATH": _path()},
    )
    tail = (r.stdout or r.stderr).strip().splitlines()
    return r.returncode, (tail[-1] if tail else "")


def role_attacker() -> dict[str, object]:
    ok, d = _pytest(["tests/test_claims_lexicon.py",
                     "tests/test_claims_lint_scope.py"])
    return {"role": "ATTACKER", "breach": not ok,
            "probe": "planted-violation lexicon/scope tests", "detail": d}


def role_skeptic() -> dict[str, object]:
    ok, d = _pytest([
        "tests/test_artifact_assertions.py", "tests/test_doc_trust.py",
        "tests/test_ci_gate_watch.py", "tests/test_ci_evidence_seal.py",
        "tests/test_doc_claim_sources.py",
    ])
    return {"role": "SKEPTIC", "breach": not ok,
            "probe": "gate-mutation-rejection tests", "detail": d}


def role_ilya() -> dict[str, object]:
    rc, d = _run(["scripts/claims_lint.py"])
    spec = (_ROOT / "docs" / "SPEC.md").read_text()
    card = (_ROOT / "docs" / "SYSTEM_CARD.md").read_text()
    has_nonclaim = ("Non-claims" in spec or "claims:disclaimer" in spec) \
        and "claims:disclaimer" in card
    breach = rc != 0 or not has_nonclaim
    return {"role": "ILYA", "breach": breach,
            "probe": "no self-eval-as-evidence: claims-lint + "
            "non-claim blocks present",
            "detail": f"claims_lint={d!r} nonclaim_blocks={has_nonclaim}"}


def role_dario() -> dict[str, object]:
    gaps = (_ROOT / "docs" / "OPEN_STRUCTURAL_GAPS.md").read_text()
    both_open = gaps.count("status: OPEN") >= 2
    ok, d = _pytest(["tests/test_structural_gaps.py"])
    breach = (not both_open) or (not ok)
    return {"role": "DARIO", "breach": breach,
            "probe": "claim-boundary: GAP_1+GAP_2 OPEN, no READY leak",
            "detail": f"both_open={both_open} structural_gaps_test={d!r}"}


def role_reproducer() -> dict[str, object]:
    steps: dict[str, str] = {}
    if shutil.which("ruff"):
        rc = subprocess.run(["ruff", "check", "src", "tests", "scripts"],
                             cwd=_ROOT, capture_output=True,
                             check=False).returncode
        steps["ruff"] = "PASS" if rc == 0 else "FAIL"
    else:
        steps["ruff"] = "UNVERIFIED (ruff absent)"
    ok, d = _pytest(["tests"])
    steps["pytest"] = "PASS" if ok else f"FAIL ({d})"
    breach = any(v.startswith("FAIL") for v in steps.values())
    return {"role": "REPRODUCER-SIMULANT", "breach": breach,
            "probe": "locally-runnable repro (NON-INDEPENDENT)",
            "detail": steps, "independent": False}


_ROLES = [role_attacker, role_skeptic, role_ilya, role_dario,
          role_reproducer]


def run() -> dict[str, object]:
    results = [r() for r in _ROLES]
    breached = [r["role"] for r in results if r["breach"]]
    return {
        "tier": "INTERNAL_ADVERSARIAL",
        "independent_validation": False,  # hard invariant, never True
        "gap_1_status": "OPEN — unchanged by construction; this "
        "artifact is self-produced and cannot close it",
        "generated_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "all_roles_clean": not breached,
        "breached_roles": breached,
        "roles": results,
        "note": "Self-simulation finds defects; it does not certify "
        "independence. Multi-role recursion raises internal rigor "
        "only. External author-absent reproduction remains required.",
    }


def main() -> int:
    rep = run()
    _OUT.parent.mkdir(exist_ok=True)
    _OUT.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    assert rep["independent_validation"] is False  # invariant guard
    if rep["all_roles_clean"]:
        print("INTERNAL ADVERSARIAL RED-TEAM — ALL ROLES CLEAN "
              "(tier=INTERNAL_ADVERSARIAL; independence NOT claimed; "
              "GAP_1 stays OPEN)")
        return 0
    print(f"INTERNAL ADVERSARIAL RED-TEAM — BREACH {rep['breached_roles']}")
    for r in rep["roles"]:
        if r["breach"]:
            print(f"  {r['role']}: {r['detail']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
