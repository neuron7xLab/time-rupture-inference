# SPDX-License-Identifier: MIT
"""Review report rendering — structure only, no new claims."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.falsifier_battery import run_falsifier_battery_v2  # noqa: E402
from ctios.opaque_probe import DeterministicMockProbe  # noqa: E402
from ctios.redacted_io import load_redacted_spec, spec_sha256  # noqa: E402
from ctios.report import render_review_report, write_review_report  # noqa: E402
from ctios.spec_compiler import compile_redacted_hypothesis  # noqa: E402

EXAMPLE = ROOT / "examples" / "indi_redacted_temporal_hypothesis.yaml"


def _pipeline():
    spec = load_redacted_spec(EXAMPLE)
    sha = spec_sha256(spec)
    compiled = compile_redacted_hypothesis(spec)
    res = DeterministicMockProbe(sha).run(spec)
    bat = run_falsifier_battery_v2(spec, res)
    return compiled, res, bat


def test_report_has_required_sections():
    compiled, res, bat = _pipeline()
    md = render_review_report(compiled, res, bat)
    for h in (
        "# TRI-Falsify Review Report",
        "## Claim",
        "## Spec SHA",
        "## Probe",
        "## Falsifier Battery",
        "## Verdict",
        "## Evidence",
        "## Boundary",
        "## Residual Risks",
        "## Human Gate",
        "## Next Experiment",
    ):
        assert h in md


def test_report_writes_file(tmp_path):
    compiled, res, bat = _pipeline()
    p = write_review_report(tmp_path, render_review_report(compiled, res, bat))
    assert p.exists() and p.name == "REVIEW_REPORT.md"
    assert compiled.spec_sha256 in p.read_text()
