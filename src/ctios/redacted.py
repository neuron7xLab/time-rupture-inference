# SPDX-License-Identifier: MIT
"""ctios.redacted — typed model of a redacted hypothesis.

A collaborator expresses a private research line as *shape only*:
claim / null / assumptions / variables / falsifiers / forbidden
inferences / evidence requirements / next-experiment policy. The
private mechanism, data, and theorem content never appear here — they
are supplied separately as a local opaque probe (see
``ctios.opaque_probe``). Structural invariants are enforced at
construction so an ill-posed skeleton cannot enter the loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_VALID_ROLES = ("manipulated", "measured", "control")
_VALID_OPS = ("<=", ">=", "<", ">")


@dataclass(frozen=True)
class RedactedVariable:
    name: str
    role: str  # manipulated | measured | control
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("RedactedVariable.name must be non-empty")
        if self.role not in _VALID_ROLES:
            raise ValueError(f"role must be one of {_VALID_ROLES}, got {self.role!r}")


@dataclass(frozen=True)
class RedactedFalsifier:
    metric: str
    op: str  # <= >= < >
    threshold_key: str
    threshold: float

    def __post_init__(self) -> None:
        if not self.metric.strip():
            raise ValueError("RedactedFalsifier.metric must be non-empty")
        if self.op not in _VALID_OPS:
            raise ValueError(f"op must be one of {_VALID_OPS}, got {self.op!r}")
        if not self.threshold_key.strip():
            raise ValueError("RedactedFalsifier.threshold_key must be non-empty")
        if self.threshold != self.threshold:  # NaN
            raise ValueError("RedactedFalsifier.threshold must be finite")


@dataclass(frozen=True)
class EvidenceRequirement:
    artifact: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.artifact.strip():
            raise ValueError("EvidenceRequirement.artifact must be non-empty")


@dataclass(frozen=True)
class ForbiddenInference:
    statement: str

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("ForbiddenInference.statement must be non-empty")


@dataclass(frozen=True)
class NextExperimentPolicy:
    auto_run: bool = False
    tighten_surviving_checks: bool = True
    loosen_failed_checks: bool = False
    failed_boundary_becomes_focus: bool = True

    def __post_init__(self) -> None:
        if self.auto_run:
            raise ValueError("NextExperimentPolicy.auto_run must be False")
        if self.loosen_failed_checks:
            raise ValueError("loosen_failed_checks must be False")


@dataclass(frozen=True)
class RedactedHypothesisSpec:
    hypothesis_id: str
    claim: str
    null: str
    assumptions: list[str]
    variables: list[RedactedVariable]
    falsifiers: list[RedactedFalsifier]
    forbidden_inferences: list[ForbiddenInference]
    evidence_requirements: list[EvidenceRequirement]
    next_experiment_policy: NextExperimentPolicy = field(
        default_factory=NextExperimentPolicy
    )
    human_review_required: bool = True
    commit_private_content: bool = False
    reviewer_notes: str = ""  # external/private; excluded from the sha

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id must be non-empty")
        if not self.claim.strip():
            raise ValueError("claim must be non-empty")
        if not self.null.strip():
            raise ValueError("null must be non-empty")
        if not self.assumptions:
            raise ValueError("at least one assumption is required")
        if not self.variables:
            raise ValueError("at least one variable is required")
        if not self.falsifiers:
            raise ValueError("at least one falsifier is required")
        if not self.forbidden_inferences:
            raise ValueError("at least one forbidden inference is required")
        if not self.evidence_requirements:
            raise ValueError("at least one evidence requirement is required")
        if not self.human_review_required:
            raise ValueError("human_review_required must be True")
        if self.commit_private_content:
            raise ValueError("commit_private_content must be False")

    def thresholds(self) -> dict[str, float]:
        """Threshold map keyed by falsifier threshold_key."""
        return {f.threshold_key: f.threshold for f in self.falsifiers}
