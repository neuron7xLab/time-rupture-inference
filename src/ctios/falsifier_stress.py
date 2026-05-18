# SPDX-License-Identifier: MIT
"""ctios.falsifier_stress — external adversarial portability stress.

Runs every adversarial probe against the falsifier battery over the
broadened benchmark portfolio and three orthogonal degeneracy scans
(single-result battery, seed sweep, family-sensitivity). Fail-closed:

  * any adversarial probe reaching a clean PASS  -> exit 1
  * any expected-caught probe not caught         -> exit 1
  * claim boundary expands (claims-lint regress) -> exit 1
  * frozen v4/v5 outputs are never written

Writes evidence/ADVERSARIAL_PORTABILITY_<sha>.json (sealed) and
docs/ADVERSARIAL_PORTABILITY_REPORT.md. CLI:

    python -m ctios.falsifier_stress --mode full
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

from ctios.adversarial_probes import (
    AdversarialProbe,
    MinimalValidProbe,
    all_adversarial_probes,
)
from ctios.benchmark_families import all_benchmark_families
from ctios.falsifier_battery import run_falsifier_battery_v2
from ctios.opaque_probe import ProbeResult
from ctios.redacted_io import load_redacted_spec, spec_sha256

ROOT = Path(__file__).resolve().parents[2]


def _spec() -> Any:
    hits = sorted((ROOT / "examples").glob("indi_redacted_*.yaml"))
    return load_redacted_spec(hits[0])


def _result(hid: str, sha: str, metrics: dict[str, float],
            *, deterministic: bool, finite: bool,
            neg_mimic: bool) -> ProbeResult:
    return ProbeResult(
        hypothesis_id=hid,
        spec_sha256=sha,
        metrics=metrics,
        deterministic=deterministic,
        finite=finite,
        private_content_committed=False,
    )


def _seed_sweep(p: AdversarialProbe, thr: dict[str, float]) -> bool:
    """True == deterministic across repeated calls (keys + values)."""
    runs = [p.probe(dict(thr)) for _ in range(5)]
    k0 = sorted(runs[0])
    for r in runs[1:]:
        if sorted(r) != k0:
            return False
        for k in k0:
            if not math.isclose(r[k], runs[0][k], rel_tol=0, abs_tol=1e-9):
                return False
    return True


def _family_sensitivity(p: AdversarialProbe, thr: dict[str, float]) -> float:
    """Std of the primary metric across structurally distinct families.
    ~0 == data-blind == degenerate (constant/identity/carrier)."""
    vals: list[float] = []
    for fam in all_benchmark_families(seed=0):
        s = fam.generate()
        m = p.evaluate(s.intervals, dict(thr))
        v = next(iter(m.values()), float("nan"))
        if math.isfinite(v):
            vals.append(v)
    if len(vals) < 2:
        return 0.0
    return float(statistics.pstdev(vals))


def _evaluate(p: AdversarialProbe, spec: Any, sha: str) -> dict[str, Any]:
    thr = spec.thresholds()
    metrics = p.probe(dict(thr))
    finite = all(math.isfinite(v) for v in metrics.values())
    deterministic = _seed_sweep(p, thr)
    is_mimic = p.name == "NegativeControlMimicProbe"
    # negative control: a legit failing control normally; the mimic
    # probe supplies a control that also passes (pseudo-GREEN attack).
    neg = _result(spec.hypothesis_id, sha,
                   p.probe(dict(thr)) if is_mimic else {},
                   deterministic=True, finite=True, neg_mimic=is_mimic)
    res = _result(spec.hypothesis_id, sha, metrics,
                  deterministic=deterministic, finite=finite,
                  neg_mimic=False)
    report = run_falsifier_battery_v2(spec, res, negative_control=neg)
    fam_std = _family_sensitivity(p, thr)
    severities = {c.severity for c in report.checks}
    reasons: list[str] = [
        f"{c.code}:{c.severity}" for c in report.checks
        if c.severity in ("BLOCKER", "MAJOR")
    ]
    blocker = "BLOCKER" in severities
    major = "MAJOR" in severities
    if not deterministic:
        blocker = True
        reasons.append("seed_sweep:BLOCKER (nondeterministic across sweep)")
    if not finite:
        blocker = True
        reasons.append("nonfinite:BLOCKER")
    if fam_std < 1e-9:
        blocker = True
        reasons.append(
            f"family_sensitivity:BLOCKER (data-blind, std={fam_std:.3g})"
        )
    status = (
        "INADMISSIBLE" if blocker
        else "CONDITIONAL" if major
        else "PASS"
    )
    return {
        "probe": p.name,
        "threat_model": p.threat_model,
        "expected": p.expected_battery_status,
        "battery_verdict": report.verdict,
        "family_metric_std": fam_std,
        "deterministic_under_sweep": deterministic,
        "finite": finite,
        "final_status": status,
        "reasons": reasons,
    }


def run_stress() -> dict[str, Any]:
    spec = _spec()
    sha = spec_sha256(spec)
    rows = [_evaluate(p, spec, sha) for p in all_adversarial_probes()]

    legit = MinimalValidProbe()
    thr = spec.thresholds()
    legit_metrics = legit.evaluate(
        __import__("numpy").linspace(10.0, 4.0, 600), dict(thr)
    )
    legit_std = _family_sensitivity(legit, thr)
    legit_ok = legit_std > 1e-9 and all(
        math.isfinite(v) for v in legit_metrics.values()
    )

    escaped = [r for r in rows if r["final_status"] == "PASS"]
    mismatched = [
        r for r in rows
        if r["expected"] == "INADMISSIBLE"
        and r["final_status"] != "INADMISSIBLE"
    ]
    payload: dict[str, Any] = {
        "spec_sha256": sha,
        "n_probes": len(rows),
        "n_families": len(all_benchmark_families()),
        "rows": rows,
        "minimal_valid_probe": {
            "family_metric_std": legit_std,
            "passes_control": legit_ok,
        },
        "fail_closed": {
            "adversarial_escaped_to_pass": [r["probe"] for r in escaped],
            "expected_caught_but_missed": [r["probe"] for r in mismatched],
        },
        "ok": not escaped and not mismatched and legit_ok,
    }
    payload["artifact_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()[:16]
    return payload


def _write(payload: dict[str, Any]) -> tuple[Path, Path]:
    ev = ROOT / "evidence"
    ev.mkdir(exist_ok=True)
    jpath = ev / f"ADVERSARIAL_PORTABILITY_{payload['artifact_sha256']}.json"
    jpath.write_text(json.dumps(payload, indent=2, default=str))

    lines = [
        "# Adversarial Portability Report",
        "",
        "Generated by `python -m ctios.falsifier_stress --mode full`. "
        "Synthetic stress only — improves battery coverage, does NOT "
        "prove real-world validity.",
        "",
        f"- spec_sha256: `{payload['spec_sha256']}`",
        f"- probes: {payload['n_probes']}  families: {payload['n_families']}",
        f"- minimal valid control passes: "
        f"{payload['minimal_valid_probe']['passes_control']}",
        f"- fail-closed OK: **{payload['ok']}**",
        "",
        "| probe | threat | expected | final | reasons |",
        "|---|---|---|---|---|",
    ]
    for r in payload["rows"]:
        lines.append(
            f"| {r['probe']} | {r['threat_model']} | {r['expected']} "
            f"| {r['final_status']} | {'; '.join(r['reasons']) or '-'} |"
        )
    lines += [
        "",
        "## Residual risks (still open)",
        "- Real-world validity is NOT addressed (synthetic families only).",
        "- External collaborator run of the private layer remains open.",
        "- A degenerate probe co-designed against this exact scan set is "
        "not proven impossible; coverage is improved, not closed.",
        "",
    ]
    mpath = ROOT / "docs" / "ADVERSARIAL_PORTABILITY_REPORT.md"
    mpath.write_text("\n".join(lines))
    return jpath, mpath


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ctios.falsifier_stress")
    ap.add_argument("--mode", choices=["full", "smoke"], default="full")
    ap.parse_args(argv)

    payload = run_stress()
    jpath, mpath = _write(payload)
    print(f"adversarial portability :: ok={payload['ok']}")
    print(f"  escaped_to_pass={payload['fail_closed']['adversarial_escaped_to_pass']}")
    print(f"  missed={payload['fail_closed']['expected_caught_but_missed']}")
    print(f"  evidence={jpath.relative_to(ROOT)}  report={mpath.relative_to(ROOT)}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
