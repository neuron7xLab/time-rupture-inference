# SPDX-License-Identifier: MIT
"""ctios.redacted_io — YAML load, validation, deterministic hash.

Loading fails closed: any forbidden private key (mechanism / data /
strategy / theorem content) in the YAML aborts the load before a spec
object exists. The hash pins claim, assumptions, variables, falsifiers,
forbidden inferences, evidence requirements, and the next-experiment
policy — so a silently retuned threshold changes the sha and is
detectable. ``reviewer_notes`` is excluded from the hash unless
explicitly opted in.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ctios.redacted import (
    EvidenceRequirement,
    ForbiddenInference,
    NextExperimentPolicy,
    RedactedFalsifier,
    RedactedHypothesisSpec,
    RedactedVariable,
)

# Keys whose presence means private content is leaking into the repo.
FORBIDDEN_KEYS = (
    "private_mechanism",
    "proprietary_data",
    "company_strategy",
    "theorem_content",
    "model_weights",
    "raw_dataset",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str  # BLOCKER | MAJOR | MINOR
    message: str


def _yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return data


def load_redacted_spec(path: Path) -> RedactedHypothesisSpec:
    """Parse + structurally validate. Raises on forbidden keys or any
    invariant violation (the dataclass enforces structure)."""
    d = _yaml(path)
    leaked = sorted(k for k in FORBIDDEN_KEYS if k in d)
    if leaked:
        raise ValueError(
            f"forbidden private field(s) present, refusing to load: {leaked}. "
            "Private mechanism/data/strategy/theorem stay local."
        )
    nep = d.get("next_experiment_policy", {}) or {}
    # YAML footgun: an unquoted `null:` key parses to None, not "null".
    raw: Any = d
    null_v = d.get("null", d.get("null_hypothesis", ""))
    if None in raw:
        null_v = raw[None]
    return RedactedHypothesisSpec(
        hypothesis_id=str(d["hypothesis_id"]),
        claim=str(d["claim"]),
        null=str(null_v),
        assumptions=[str(a) for a in d.get("assumptions", [])],
        variables=[
            RedactedVariable(
                name=str(v["name"]),
                role=str(v["role"]),
                description=str(v.get("description", "")),
            )
            for v in d.get("variables", [])
        ],
        falsifiers=[
            RedactedFalsifier(
                metric=str(f["metric"]),
                op=str(f["op"]),
                threshold_key=str(f["threshold_key"]),
                threshold=float(f["threshold"]),
            )
            for f in d.get("falsifiers", [])
        ],
        forbidden_inferences=[
            ForbiddenInference(statement=str(s))
            for s in d.get("forbidden_inferences", d.get("forbidden_claims", []))
        ],
        evidence_requirements=[
            EvidenceRequirement(
                artifact=str(e) if not isinstance(e, dict) else str(e["artifact"]),
                description=(
                    "" if not isinstance(e, dict) else str(e.get("description", ""))
                ),
            )
            for e in d.get("evidence_requirements", d.get("required_artifacts", []))
        ],
        next_experiment_policy=NextExperimentPolicy(
            auto_run=bool(nep.get("auto_run", False)),
            tighten_surviving_checks=bool(nep.get("tighten_surviving_checks", True)),
            loosen_failed_checks=bool(nep.get("loosen_failed_checks", False)),
            failed_boundary_becomes_focus=bool(
                nep.get("failed_boundary_becomes_focus", True)
            ),
        ),
        human_review_required=bool(d.get("human_review_required", True)),
        commit_private_content=bool(d.get("commit_private_content", False)),
        reviewer_notes=str(d.get("reviewer_notes", "")),
    )


def validate_redacted_spec(
    spec: RedactedHypothesisSpec,
) -> list[ValidationIssue]:
    """Soft, non-raising audit on top of the hard structural invariants
    already guaranteed by construction."""
    issues: list[ValidationIssue] = []
    if not any(v.role == "control" for v in spec.variables):
        issues.append(
            ValidationIssue(
                "no_negative_control_variable",
                "MAJOR",
                "no variable with role 'control'; a discriminative "
                "negative control is required for an admissible GREEN",
            )
        )
    metrics_used = {f.metric for f in spec.falsifiers}
    measured = {v.name for v in spec.variables if v.role == "measured"}
    if measured and not (metrics_used & measured):
        issues.append(
            ValidationIssue(
                "falsifier_metric_unmeasured",
                "MAJOR",
                "no falsifier references a measured variable",
            )
        )
    if len(spec.assumptions) < 2:
        issues.append(
            ValidationIssue(
                "thin_assumptions",
                "MINOR",
                "fewer than two assumptions; boundary may be underdefined",
            )
        )
    return issues


def spec_sha256(spec: RedactedHypothesisSpec, *, include_notes: bool = False) -> str:
    """Deterministic pin. Order-independent within each list via sorting
    of the canonical JSON; reviewer_notes excluded unless opted in."""
    payload: dict[str, Any] = {
        "claim": spec.claim,
        "null": spec.null,
        "assumptions": sorted(spec.assumptions),
        "variables": sorted(
            [v.name, v.role, v.description] for v in spec.variables
        ),
        "falsifiers": sorted(
            [f.metric, f.op, f.threshold_key, f.threshold]
            for f in spec.falsifiers
        ),
        "forbidden_inferences": sorted(
            i.statement for i in spec.forbidden_inferences
        ),
        "evidence_requirements": sorted(
            [e.artifact, e.description] for e in spec.evidence_requirements
        ),
        "next_experiment_policy": [
            spec.next_experiment_policy.auto_run,
            spec.next_experiment_policy.tighten_surviving_checks,
            spec.next_experiment_policy.loosen_failed_checks,
            spec.next_experiment_policy.failed_boundary_becomes_focus,
        ],
        "human_review_required": spec.human_review_required,
        "commit_private_content": spec.commit_private_content,
    }
    if include_notes:
        payload["reviewer_notes"] = spec.reviewer_notes
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()
