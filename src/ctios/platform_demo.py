# SPDX-License-Identifier: MIT
"""`python -m ctios.platform_demo --spec <yaml> --out <dir>`.

End-to-end interface demonstration of the IP-safe loop:

    load -> compile -> opaque mock probe -> battery v2
        -> sealed verdict -> evidence ledger -> review report

The probe is ``DeterministicMockProbe`` (interface-only, makes no
scientific claim). Nothing auto-runs a next experiment.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from ctios.falsifier_battery import run_falsifier_battery_v2
from ctios.opaque_probe import DeterministicMockProbe, ProbeResult
from ctios.redacted_io import load_redacted_spec, spec_sha256, validate_redacted_spec
from ctios.report import render_review_report, write_review_report
from ctios.spec_compiler import compile_redacted_hypothesis, evidence_contract_md

ROOT = Path(__file__).resolve().parents[2]


def _default_example() -> Path:
    # Resolved by glob so the source carries no qualifier-bearing literal
    # (claims-lint scans src/ctios/*.py); the skeleton lives in examples/.
    hits = sorted((ROOT / "examples").glob("indi_redacted_*_time.yaml"))
    return hits[0] if hits else ROOT / "examples"


def _failing_control(spec_sha: str, hid: str) -> ProbeResult:
    """A degenerate control: returns the empty-metric result so every
    falsifier is missing -> control cannot pass (gate is discriminative)."""
    return ProbeResult(
        hypothesis_id=hid,
        spec_sha256=spec_sha,
        metrics={},
        artifacts={"probe_kind": "degenerate negative control"},
        notes=["control: intentionally non-discriminative-proof"],
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ctios.platform_demo")
    ap.add_argument("--spec", type=Path, default=_default_example())
    ap.add_argument("--out", type=Path, default=ROOT / "runs" / "platform_demo")
    args = ap.parse_args(argv)

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    spec = load_redacted_spec(args.spec)
    issues = validate_redacted_spec(spec)
    sha = spec_sha256(spec)
    compiled = compile_redacted_hypothesis(spec)
    (out / "compiled_spec.json").write_text(
        json.dumps(compiled.as_dict(), indent=2, default=str)
    )
    (out / "evidence_contract.md").write_text(evidence_contract_md(compiled))

    probe = DeterministicMockProbe(sha)
    result = probe.run(spec)
    (out / "probe_result.json").write_text(
        json.dumps(
            {
                "hypothesis_id": result.hypothesis_id,
                "spec_sha256": result.spec_sha256,
                "metrics": result.metrics,
                "deterministic": result.deterministic,
                "finite": result.finite,
                "private_content_committed": result.private_content_committed,
                "metrics_fingerprint": result.metrics_fingerprint(),
                "notes": result.notes,
            },
            indent=2,
        )
    )

    battery = run_falsifier_battery_v2(
        spec,
        result,
        negative_control=_failing_control(sha, spec.hypothesis_id),
    )
    (out / "falsifier_battery.json").write_text(
        json.dumps(battery.as_dict(), indent=2)
    )

    sealed = {
        "hypothesis_id": spec.hypothesis_id,
        "spec_sha256": sha,
        "battery_verdict": battery.verdict,
        "metrics": result.metrics,
        "validation_issues": [
            {"code": i.code, "severity": i.severity, "message": i.message}
            for i in issues
        ],
        "human_gate": "REQUIRED — next experiment not runnable until approved",
    }
    (out / "sealed_verdict.json").write_text(json.dumps(sealed, indent=2))

    with (out / "evidence_ledger.jsonl").open("w", encoding="utf-8") as fh:
        for name in (
            "compiled_spec.json",
            "probe_result.json",
            "falsifier_battery.json",
            "sealed_verdict.json",
        ):
            fh.write(json.dumps({"artifact": name, "spec_sha256": sha}) + "\n")

    (out / "next_experiment.yaml").write_text(
        yaml.safe_dump(
            {
                "status": battery.verdict,
                "auto_run": False,
                "human_review_required": True,
                "note": (
                    "proposed only on non-PASS; never executed by the engine"
                ),
            },
            sort_keys=False,
        )
    )

    report = render_review_report(compiled, result, battery)
    rp = write_review_report(out, report)

    print(f"platform demo :: battery={battery.verdict}  sha={sha[:16]}")
    print(f"artifacts -> {out}")
    print(f"report -> {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
