# SPDX-License-Identifier: MIT
"""ctios.report — sealed Markdown review report.

One human-readable artifact per run: claim, spec sha, probe, battery,
verdict, evidence, boundary, residual risks, human gate, next
experiment. No new claims — it only renders what the loop produced.
"""

from __future__ import annotations

from pathlib import Path

from ctios.falsifier_battery import BatteryReport
from ctios.human_gate import GateRecord
from ctios.opaque_probe import ProbeResult
from ctios.spec_compiler import CompiledSpec


def render_review_report(
    compiled: CompiledSpec,
    probe: ProbeResult,
    battery: BatteryReport,
    *,
    gate_trail: list[GateRecord] | None = None,
    next_experiment: str = "(none — proposed only on non-PASS, human-gated)",
) -> str:
    blockers = [c for c in battery.checks if c.severity == "BLOCKER"]
    majors = [c for c in battery.checks if c.severity == "MAJOR"]
    gate_trail = gate_trail or []

    lines: list[str] = [
        "# TRI-Falsify Review Report",
        "",
        "## Claim",
        compiled.claim,
        "",
        "## Spec SHA",
        f"`{compiled.spec_sha256}`  (initial: `{compiled.initial_verdict}`)",
        "",
        "## Probe",
        f"- hypothesis_id: `{probe.hypothesis_id}`",
        f"- deterministic: {probe.deterministic}  finite: {probe.finite}  "
        f"exploratory: {probe.exploratory}",
        f"- private_content_committed: {probe.private_content_committed}",
        f"- metrics: {probe.metrics}",
        f"- metrics_fingerprint: `{probe.metrics_fingerprint()}`",
        "",
        "## Falsifier Battery",
        f"**verdict: {battery.verdict}**",
        "",
        "| code | severity | message |",
        "|---|---|---|",
    ]
    lines += [
        f"| {c.code} | {c.severity} | {c.message} |" for c in battery.checks
    ]
    lines += [
        "",
        "## Verdict",
        f"`{battery.verdict}`  "
        f"(BLOCKER={len(blockers)}, MAJOR={len(majors)})",
        "",
        "## Evidence",
    ]
    lines += [
        f"- `{e['artifact']}` — {e['description']}"
        for e in compiled.evidence_contract
    ]
    lines += ["", "## Boundary (forbidden inferences)"]
    lines += [f"- {s}" for s in compiled.forbidden_inferences]
    lines += ["", "## Residual Risks"]
    risk = [c for c in battery.checks if c.severity in ("MAJOR", "MINOR")]
    lines += (
        [f"- [{c.severity}] {c.code}: {c.message}" for c in risk]
        if risk
        else ["- none flagged by the battery (still bounded by SPEC scope)"]
    )
    lines += ["", "## Human Gate"]
    lines += (
        [f"- {r.ts_utc} {r.action} by {r.reviewer}: {r.reason}" for r in gate_trail]
        if gate_trail
        else ["- no decision recorded; next experiment NOT runnable"]
    )
    lines += ["", "## Next Experiment", next_experiment, ""]
    return "\n".join(lines) + "\n"


def write_review_report(run_dir: Path, content: str) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / "REVIEW_REPORT.md"
    p.write_text(content)
    return p
