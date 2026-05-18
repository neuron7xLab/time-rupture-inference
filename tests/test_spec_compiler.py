# SPDX-License-Identifier: MIT
"""Spec compiler — admission rules + CLI."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.redacted import (  # noqa: E402
    EvidenceRequirement,
    ForbiddenInference,
    RedactedFalsifier,
    RedactedHypothesisSpec,
    RedactedVariable,
)
from ctios.spec_cli import main as spec_cli_main  # noqa: E402
from ctios.spec_compiler import compile_redacted_hypothesis  # noqa: E402

EXAMPLE = ROOT / "examples" / "indi_redacted_cognitive_time.yaml"


def _spec(**over):
    base = dict(
        hypothesis_id="h",
        claim="c",
        null="n",
        assumptions=["a"],
        variables=[RedactedVariable("c", "control")],
        falsifiers=[RedactedFalsifier("m", "<=", "k", 1.0)],
        forbidden_inferences=[ForbiddenInference("no agi")],
        evidence_requirements=[EvidenceRequirement("sealed")],
    )
    base.update(over)
    return RedactedHypothesisSpec(**base)


def test_compile_starts_blocked_until_probed():
    c = compile_redacted_hypothesis(_spec())
    assert c.initial_verdict == "BLOCKED_UNTIL_PROBED"
    assert c.required_controls == ["c"]
    assert len(c.spec_sha256) == 64


def test_compile_notes_missing_control():
    c = compile_redacted_hypothesis(
        _spec(variables=[RedactedVariable("m", "measured")])
    )
    assert any("no control" in n for n in c.notes)


def test_cli_compile_writes_artifacts(tmp_path, capsys):
    rc = spec_cli_main(["compile", str(EXAMPLE), "--out", str(tmp_path)])
    assert rc == 0
    cs = json.loads((tmp_path / "compiled_spec.json").read_text())
    assert cs["initial_verdict"] == "BLOCKED_UNTIL_PROBED"
    assert (tmp_path / "evidence_contract.md").exists()
    assert (tmp_path / "next_experiment_policy.yaml").exists()


def test_cli_rejects_forbidden_private_field(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "hypothesis_id: h\nclaim: c\nnull: n\nassumptions: [a]\n"
        "variables: [{name: m, role: measured}]\n"
        "falsifiers: [{metric: m, op: '<=', threshold_key: k, threshold: 1.0}]\n"
        "forbidden_inferences: [no agi]\nevidence_requirements: [sealed]\n"
        "private_mechanism: leaked\n"
    )
    with pytest.raises(ValueError, match="forbidden private field"):
        spec_cli_main(["compile", str(bad), "--out", str(tmp_path / "o")])
