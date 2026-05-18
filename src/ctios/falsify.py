# SPDX-License-Identifier: MIT
"""ctios.falsify — generalized adversarial-falsification engine.

Consolidates the discipline that was previously re-implemented per
lineage (run_v8_4..., run_v9..., ...) into one auditable primitive:

    HypothesisSpec (pinned)  +  Probe (candidate ⊕ env)
        → adversarial battery (determinism · finiteness ·
          threshold-bites criticism · negative-control)
        → GREEN / RED / PARTIAL verdict
        → sealed, reproducible artifact (never tuned)

A `Probe` returns a metrics dict and accepts a thresholds dict so the
engine can mutate thresholds to prove the gate is load-bearing (the
"criticize it" step). No claim/capability language; no threshold edited
after results — the spec hash is recorded in the verdict.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

Probe = Callable[[dict[str, float]], dict[str, float]]


@dataclass(frozen=True)
class HypothesisSpec:
    hid: str
    claim: str
    null: str
    thresholds: dict[str, float]
    checks: list[dict[str, str]]          # {metric, op, threshold_key}
    parent: str = ""
    claim_boundary: str = ""

    @staticmethod
    def load(path: Path) -> HypothesisSpec:
        d = yaml.safe_load(path.read_text())
        # YAML footgun: an unquoted `null:` key parses to None, not the
        # string "null". Accept both, plus an explicit `null_hypothesis`.
        null_v = d.get("null", d.get(None, d.get("null_hypothesis", "")))
        return HypothesisSpec(
            hid=str(d["hid"]),
            claim=str(d["claim"]),
            null=str(null_v),
            thresholds={k: float(v) for k, v in d["thresholds"].items()},
            checks=list(d["checks"]),
            parent=str(d.get("parent", "")),
            claim_boundary=str(d.get("claim_boundary", "")),
        )

    def sha(self) -> str:
        blob = json.dumps(
            {"hid": self.hid, "thresholds": self.thresholds, "checks": self.checks},
            sort_keys=True,
        )
        return hashlib.sha256(blob.encode()).hexdigest()


@dataclass
class Verdict:
    hid: str
    status: str                           # GREEN | RED | PARTIAL
    checks: dict[str, bool]
    metrics: dict[str, float]
    battery: dict[str, bool]
    spec_sha256: str
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


_OPS: dict[str, Callable[[float, float], bool]] = {
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
}


def _eval_checks(metrics: dict[str, float], spec: HypothesisSpec) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for c in spec.checks:
        m, op, tk = c["metric"], c["op"], c["threshold_key"]
        out[f"{m}{op}{tk}"] = _OPS[op](float(metrics[m]), spec.thresholds[tk])
    return out


def run_battery(
    spec: HypothesisSpec,
    probe: Probe,
    metrics: dict[str, float],
    negative_control: Probe | None,
) -> dict[str, bool]:
    """Force boundary conditions and criticize the result."""
    b: dict[str, bool] = {}
    # 1. determinism — same thresholds → identical metrics
    m2 = probe(dict(spec.thresholds))
    b["deterministic"] = all(
        abs(metrics[k] - m2.get(k, float("nan"))) < 1e-9 for k in metrics
    )
    # 2. finiteness
    b["finite"] = all(
        v == v and v not in (float("inf"), float("-inf")) for v in metrics.values()
    )
    # 3. threshold-bites criticism — an impossibly strict threshold MUST
    #    flip every check to fail; a trivial one MUST pass. If neither
    #    moves the verdict, the gate is decorative.
    strict = {k: (v * 0.0 - 1.0) for k, v in spec.thresholds.items()}
    loose = {k: (abs(v) * 1e9 + 1e9) for k, v in spec.thresholds.items()}
    cs = _eval_checks(metrics, _rethr(spec, strict))
    cl = _eval_checks(metrics, _rethr(spec, loose))
    b["thresholds_load_bearing"] = (not all(cs.values())) and any(cl.values())
    # 4. negative control — a degenerate candidate must NOT pass
    if negative_control is not None:
        nc = negative_control(dict(spec.thresholds))
        b["negative_control_fails"] = not all(_eval_checks(nc, spec).values())
    else:
        b["negative_control_fails"] = True
    return b


def _rethr(spec: HypothesisSpec, thr: dict[str, float]) -> HypothesisSpec:
    return HypothesisSpec(
        spec.hid, spec.claim, spec.null, thr, spec.checks, spec.parent,
        spec.claim_boundary,
    )


def falsify(
    spec: HypothesisSpec,
    probe: Probe,
    *,
    negative_control: Probe | None = None,
    evidence_dir: Path | None = None,
) -> Verdict:
    metrics = probe(dict(spec.thresholds))
    checks = _eval_checks(metrics, spec)
    battery = run_battery(spec, probe, metrics, negative_control)
    all_checks = all(checks.values())
    all_batt = all(battery.values())
    if all_checks and all_batt:
        status = "GREEN"
    elif any(checks.values()) and battery["deterministic"] and battery["finite"]:
        status = "PARTIAL"
    else:
        status = "RED"
    reasons = (
        [f"check failed: {k}" for k, v in checks.items() if not v]
        + [f"battery failed: {k}" for k, v in battery.items() if not v]
    )
    verdict = Verdict(
        hid=spec.hid,
        status=status,
        checks=checks,
        metrics=metrics,
        battery=battery,
        spec_sha256=spec.sha(),
        reasons=reasons,
    )
    if evidence_dir is not None:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / f"FALSIFY_{spec.hid}.json").write_text(
            json.dumps(verdict.as_dict(), indent=2, default=float)
        )
        if status != "GREEN":
            (evidence_dir / f"NEGATIVE_FALSIFY_{spec.hid}.md").write_text(
                f"# SEALED NEGATIVE — {spec.hid} ({status})\n\n"
                f"claim: {spec.claim}\nnull: {spec.null}\n"
                f"spec_sha256: {spec.sha()}\nparent: {spec.parent}\n\n"
                "reasons:\n" + "".join(f"- {r}\n" for r in reasons)
                + "\nNo threshold tuned. Preserved.\n"
            )
    return verdict
