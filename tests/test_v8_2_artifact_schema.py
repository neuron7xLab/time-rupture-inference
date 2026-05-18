# SPDX-License-Identifier: MIT
"""Contract: after a diagnostic run the artifact set + schema are valid.
Runs the diagnostic once (deterministic, fast, no model)."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "v8_2"
REQUIRED = (
    "metrics.json", "metrics.csv", "trigger_mask.csv", "carrier_mask.csv",
    "background_mask.csv", "oracle_predictions.csv", "run_config_resolved.yaml",
    "environment_fingerprint.json", "git_commit.txt",
    "deterministic_replay_hash.txt",
)


def test_artifacts_present_and_metrics_schema():
    subprocess.run(
        [sys.executable, "scripts/run_v8_2_trigger_scoped_diagnostic.py"],
        cwd=ROOT, capture_output=True, check=False,
    )
    for f in REQUIRED:
        assert (ART / f).exists(), f"missing artifact {f}"
    m = json.loads((ART / "metrics.json").read_text())
    for key in ("verdict", "trigger_context_gap_ratio",
                "carrier_controlled_gap_ratio", "no_learned_model_run"):
        assert key in m
    assert m["no_learned_model_run"] is True
    assert m["verdict"] in ("GREEN", "PARTIAL_RED", "RED")
