# SPDX-License-Identifier: MIT
"""ctios.opaque_probe — the IP boundary.

A collaborator's private mechanism is a black box behind this
interface. The engine calls ``run`` and never inspects the
implementation, the data, or the reasoning. Only a ``ProbeResult``
crosses back: scalar metrics, artifact references, and honesty flags.
A probe that smuggles private content, is non-deterministic without
declaring it, or returns non-finite metrics is a hard blocker
downstream (see ``ctios.falsifier_battery``).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from ctios.redacted import RedactedHypothesisSpec


@dataclass(frozen=True)
class ProbeResult:
    hypothesis_id: str
    spec_sha256: str
    metrics: dict[str, float]
    artifacts: dict[str, str] = field(default_factory=dict)
    private_content_committed: bool = False
    deterministic: bool = True
    finite: bool = True
    exploratory: bool = False  # explicit opt-out of the determinism block
    notes: list[str] = field(default_factory=list)

    def metrics_fingerprint(self) -> str:
        blob = json.dumps(self.metrics, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()


@runtime_checkable
class OpaqueProbe(Protocol):
    def run(self, spec: RedactedHypothesisSpec) -> ProbeResult: ...


class DeterministicMockProbe:
    """Interface-only demonstration probe. Makes NO scientific claim:
    it derives toy metrics deterministically from the pinned spec sha so
    the platform loop is exercised end to end without any real
    mechanism, data, or theorem. Never use as evidence of anything."""

    def __init__(self, spec_sha256: str) -> None:
        self._sha = spec_sha256

    def run(self, spec: RedactedHypothesisSpec) -> ProbeResult:
        # Deterministic, finite, and constructed to clear each falsifier
        # by a fixed margin — this exercises the pipeline, not science.
        metrics: dict[str, float] = {}
        for fz in spec.falsifiers:
            if fz.op in ("<=", "<"):
                metrics[fz.metric] = round(fz.threshold * 0.5, 6)
            else:
                metrics[fz.metric] = round(abs(fz.threshold) * 2.0 + 1.0, 6)
        return ProbeResult(
            hypothesis_id=spec.hypothesis_id,
            spec_sha256=self._sha,
            metrics=metrics,
            artifacts={"probe_kind": "DeterministicMockProbe (interface-only)"},
            private_content_committed=False,
            deterministic=True,
            finite=True,
            notes=["interface demonstration only; not scientific evidence"],
        )
