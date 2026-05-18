# SPDX-License-Identifier: MIT
"""ctios.spec_compiler — redacted hypothesis -> compiled research object.

Rule of admission: if there is no falsifier, no forbidden inference, or
no evidence requirement, there is no experiment. If the policy would
auto-run or skip the human gate, compilation fails. The compiled object
starts ``BLOCKED_UNTIL_PROBED`` — it cannot become a verdict until an
opaque probe and the battery have run.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ctios.redacted import RedactedHypothesisSpec
from ctios.redacted_io import spec_sha256


@dataclass
class CompiledSpec:
    spec_sha256: str
    hypothesis_id: str
    claim: str
    null: str
    assumptions: list[str]
    variables: list[dict[str, str]]
    falsifiers: list[dict[str, Any]]
    required_controls: list[str]
    evidence_contract: list[dict[str, str]]
    forbidden_inferences: list[str]
    next_experiment_policy: dict[str, bool]
    initial_verdict: str = "BLOCKED_UNTIL_PROBED"
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def compile_redacted_hypothesis(spec: RedactedHypothesisSpec) -> CompiledSpec:
    if not spec.falsifiers:
        raise ValueError("compile failed: no falsifier (no falsifier, no experiment)")
    if not spec.forbidden_inferences:
        raise ValueError(
            "compile failed: no forbidden inference (no boundary, claim BLOCKED)"
        )
    if not spec.evidence_requirements:
        raise ValueError(
            "compile failed: no evidence requirement (no verdict without evidence)"
        )
    if spec.next_experiment_policy.auto_run:
        raise ValueError("compile failed: next_experiment_policy.auto_run is True")
    if not spec.human_review_required:
        raise ValueError("compile failed: human_review_required is False")

    controls = [v.name for v in spec.variables if v.role == "control"]
    return CompiledSpec(
        spec_sha256=spec_sha256(spec),
        hypothesis_id=spec.hypothesis_id,
        claim=spec.claim,
        null=spec.null,
        assumptions=list(spec.assumptions),
        variables=[
            {"name": v.name, "role": v.role, "description": v.description}
            for v in spec.variables
        ],
        falsifiers=[
            {
                "metric": f.metric,
                "op": f.op,
                "threshold_key": f.threshold_key,
                "threshold": f.threshold,
            }
            for f in spec.falsifiers
        ],
        required_controls=controls,
        evidence_contract=[
            {"artifact": e.artifact, "description": e.description}
            for e in spec.evidence_requirements
        ],
        forbidden_inferences=[i.statement for i in spec.forbidden_inferences],
        next_experiment_policy={
            "auto_run": spec.next_experiment_policy.auto_run,
            "tighten_surviving_checks": (
                spec.next_experiment_policy.tighten_surviving_checks
            ),
            "loosen_failed_checks": spec.next_experiment_policy.loosen_failed_checks,
            "failed_boundary_becomes_focus": (
                spec.next_experiment_policy.failed_boundary_becomes_focus
            ),
        },
        notes=(
            [] if controls else ["no control variable: GREEN cannot be admissible"]
        ),
    )


def evidence_contract_md(c: CompiledSpec) -> str:
    lines = [
        f"# Evidence Contract — {c.hypothesis_id}",
        "",
        f"spec_sha256: `{c.spec_sha256}`",
        f"initial_verdict: `{c.initial_verdict}`",
        "",
        "## Claim",
        c.claim,
        "",
        "## Null",
        c.null,
        "",
        "## Required artifacts (verdict is inadmissible without these)",
    ]
    lines += [f"- `{e['artifact']}` — {e['description']}" for e in c.evidence_contract]
    lines += ["", "## Required controls"]
    lines += (
        [f"- {x}" for x in c.required_controls]
        if c.required_controls
        else ["- (none declared — GREEN cannot be admissible)"]
    )
    lines += ["", "## Forbidden inferences (hard boundary)"]
    lines += [f"- {s}" for s in c.forbidden_inferences]
    lines += ["", "_No threshold may be edited after a run; the sha pins it._"]
    return "\n".join(lines) + "\n"
