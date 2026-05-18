# SPDX-License-Identifier: MIT
"""ctios.adversarial_probes — a red-team battery of degenerate probes.

Each probe is a deterministic attack on the falsifier battery. The
contract is intentionally honest: probes whose degeneracy is visible in
a single ProbeResult are caught by ``ctios.falsifier_battery`` directly;
probes whose degeneracy is only visible across spec perturbations
(constant / identity / carrier shortcuts) are caught by the
spec-sensitivity scan in ``ctios.falsifier_stress``. No probe is
allowed to reach a clean PASS — that property is asserted by the test
suite and the fail-closed stress gate, not assumed.

Signature per the work order: ``probe(thresholds) -> dict[str, float]``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Battery/stress status vocabulary the suite asserts against.
INADMISSIBLE = "INADMISSIBLE"
CONDITIONAL = "CONDITIONAL"
FAIL = "FAIL"  # caught by the stress spec-sensitivity scan


@dataclass
class AdversarialProbe:
    name: str
    threat_model: str
    expected_battery_status: str
    # How the threat manifests, consumed by falsifier_stress:
    #   "single_result"  -> caught by falsifier_battery on one result
    #   "spec_invariant"  -> caught by the spec-sensitivity scan
    #   "seed_sweep"      -> caught by the determinism sweep
    detection: str
    _state: dict[str, float] = field(default_factory=dict)

    # default benign metric names the demo spec gates on
    METRIC = "post_rupture_error"
    METRIC2 = "separation_vs_baseline"

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        raise NotImplementedError

    def evaluate(
        self, intervals: object, thresholds: dict[str, float]
    ) -> dict[str, float]:
        """Stress-runner entry point. Default IGNORES the data — that
        data-blindness IS the degeneracy the family-sensitivity scan
        detects. A legitimate probe overrides this to read the data."""
        return self.probe(thresholds)


class ConstantMetricProbe(AdversarialProbe):
    """Returns a fixed flattering metric, ignoring thresholds and spec."""

    def __init__(self) -> None:
        super().__init__(
            "ConstantMetricProbe",
            "emits a constant passing metric regardless of the hypothesis",
            INADMISSIBLE,
            "spec_invariant",
        )

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        return {self.METRIC: 0.01, self.METRIC2: 999.0}


class ThresholdEchoProbe(AdversarialProbe):
    """Returns a metric pinned exactly to the supplied threshold —
    a verdict that sits on the knife-edge of every gate."""

    def __init__(self) -> None:
        # Honestly resolves to INADMISSIBLE: it is both knife-edge
        # unstable (battery MAJOR) and data-blind (family scan BLOCKER).
        super().__init__(
            "ThresholdEchoProbe",
            "echoes the threshold so the verdict is unstable by design",
            INADMISSIBLE,
            "single_result",
        )

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        keys = list(thresholds)
        return {
            self.METRIC: thresholds.get(keys[0], 1.0) if keys else 1.0,
            self.METRIC2: thresholds.get(
                keys[1] if len(keys) > 1 else "", 0.1
            ),
        }


class IdentityOracleProbe(AdversarialProbe):
    """Encodes the target result from spec metadata (leakage by
    construction) — degenerate but deterministic and discriminative."""

    def __init__(self) -> None:
        super().__init__(
            "IdentityOracleProbe",
            "reconstructs the desired verdict from the spec itself",
            INADMISSIBLE,
            "spec_invariant",
        )

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        # Always 1% under whatever ceiling it is told — looks adaptive,
        # is actually a copy of the gate.
        keys = list(thresholds)
        c = thresholds.get(keys[0], 1.0) if keys else 1.0
        return {self.METRIC: c * 0.99, self.METRIC2: 1.0}


class CarrierLeakProbe(AdversarialProbe):
    """Exploits a carrier/confound channel rather than the target
    signal; passes the gate without solving the task."""

    def __init__(self) -> None:
        super().__init__(
            "CarrierLeakProbe",
            "passes via a confound, not the rupture signal",
            INADMISSIBLE,
            "spec_invariant",
        )

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        return {self.METRIC: 0.05, self.METRIC2: 50.0}


class NonFiniteProbe(AdversarialProbe):
    """Returns nan / inf."""

    def __init__(self) -> None:
        super().__init__(
            "NonFiniteProbe",
            "emits non-finite metrics",
            INADMISSIBLE,
            "single_result",
        )

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        return {self.METRIC: float("nan"), self.METRIC2: float("inf")}


class RandomButSeededProbe(AdversarialProbe):
    """Deterministic under one fixed seed, divergent under a seed
    sweep — fake reproducibility."""

    def __init__(self) -> None:
        super().__init__(
            "RandomButSeededProbe",
            "looks deterministic at one seed, drifts under a sweep",
            INADMISSIBLE,
            "seed_sweep",
        )
        self._call = 0

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        self._call += 1
        # identical on the first call (one-seed illusion), drifts after.
        drift = 0.0 if self._call <= 1 else 1e-2 * self._call
        return {self.METRIC: 0.2 + drift, self.METRIC2: 0.5}


class MetricSwitchProbe(AdversarialProbe):
    """Changes the reported metric name/semantics between calls so the
    gate cannot bind to a stable surface."""

    def __init__(self) -> None:
        super().__init__(
            "MetricSwitchProbe",
            "renames the reported metric between calls",
            INADMISSIBLE,
            "seed_sweep",
        )
        self._call = 0

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        self._call += 1
        name = self.METRIC if self._call <= 1 else f"{self.METRIC}_v{self._call}"
        return {name: 0.1, self.METRIC2: 0.5}


class NegativeControlMimicProbe(AdversarialProbe):
    """Makes the negative control pass too, so the gate is not
    discriminative (pseudo-GREEN)."""

    def __init__(self) -> None:
        super().__init__(
            "NegativeControlMimicProbe",
            "negative control also clears every falsifier",
            INADMISSIBLE,
            "single_result",
        )

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        return {self.METRIC: 0.01, self.METRIC2: 999.0}


def all_adversarial_probes() -> list[AdversarialProbe]:
    return [
        ConstantMetricProbe(),
        ThresholdEchoProbe(),
        IdentityOracleProbe(),
        CarrierLeakProbe(),
        NonFiniteProbe(),
        RandomButSeededProbe(),
        MetricSwitchProbe(),
        NegativeControlMimicProbe(),
    ]


class MinimalValidProbe(AdversarialProbe):
    """A legitimate minimal probe: stable, spec-sensitive, clears the
    gate honestly. The control case — it MUST pass."""

    def __init__(self) -> None:
        super().__init__(
            "MinimalValidProbe",
            "honest minimal probe (control: must pass)",
            "PASS",
            "none",
        )

    def probe(self, thresholds: dict[str, float]) -> dict[str, float]:
        keys = list(thresholds)
        c = thresholds.get(keys[0], 1.0) if keys else 1.0
        s = thresholds.get(keys[1], 0.1) if len(keys) > 1 else 0.1
        return {self.METRIC: c * 0.5, self.METRIC2: s * 5.0 + 1.0}

    def evaluate(
        self, intervals: object, thresholds: dict[str, float]
    ) -> dict[str, float]:
        # Legit: the metric is DERIVED FROM THE DATA, so it varies
        # across benchmark families (passes the family-sensitivity scan).
        import numpy as np

        x = np.asarray(intervals, dtype=np.float64)
        half = max(1, x.size // 2)
        post = x[half:]
        err = float(np.mean(np.abs(post - np.median(post)))) if post.size else 1.0
        keys = list(thresholds)
        s = thresholds.get(keys[1], 0.1) if len(keys) > 1 else 0.1
        return {self.METRIC: err, self.METRIC2: s * 5.0 + 1.0}
